"""Assemble reviewed film artifacts after both renders have passed inspection."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import shutil
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from core.provenance import MANIFEST, source_files_for_film as render_source_files, verify_render_sources
from core.films import film_for_slug

FIXTURE_HASH = 'd4204afd2e4ee8e8bcac9cd6d5842a4dbe172932a250930516d5f62b1922407b'


def fixture_contract(slug, scene):
    if slug[:2] in ('01', '02', '03', '04'):
        return 'data/manim_fixtures.json', FIXTURE_HASH
    film = film_for_slug(slug)
    if scene != film.scene:
        raise ValueError('Scene does not match registered film')
    return film.fixture_path, film.fixture_hash


def validate_segmented_tracks(timing, narration, tracks):
    from core.subtitles import subtitle_rows, normalized
    from core.cues import timestamp
    cues = [SimpleNamespace(**row) for row in timing['cues']]
    rows = subtitle_rows(cues, narration)
    if rows != timing.get('subtitle_intervals'):
        raise ValueError('Subtitle timing differs from measured narration')
    pattern = r'(\d\d:\d\d:\d\d[,.]\d{3}) --> (\d\d:\d\d:\d\d[,.]\d{3})\n([^\n]+(?:\n[^\n]+)*)'
    for track in tracks:
        parsed = re.findall(pattern, track)
        if len(parsed) != len(rows):
            raise ValueError('Wrong number of measured subtitle segments')
        for row, (start, end, text) in zip(rows, parsed):
            if (start.replace(',', '.') != timestamp(row['start'], '.')
                    or end.replace(',', '.') != timestamp(row['end'], '.')
                    or normalized(text) != normalized(row['text'])):
                raise ValueError('Subtitle text or timing differs from measured segment')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_visual_review(record, *, allow_pending_playback=False):
    """A pending package still requires actual frame review, never an assumed pass."""
    if record.get('visual_review') == 'passed':
        return
    if (allow_pending_playback and record.get('visual_review') == 'pending'
            and record.get('frame_review') == 'passed'
            and record.get('playback_review') == 'pending'):
        return
    raise ValueError('Export lacks the required visual review')


def source_files_for_film(slug, scene, audio_expected):
    return render_source_files(ROOT, slug, scene, audio_expected)


def require_narrated_review(record, *, allow_pending_playback=False):
    for gate in ('playback_review', 'audio_review'):
        status = record.get(gate)
        allowed = ('passed', 'pending') if allow_pending_playback else ('passed',)
        if status not in allowed:
            raise ValueError(f'Narrated export lacks the required playback/listening pass: {gate}')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slug',required=True)
    parser.add_argument('--scene',required=True)
    parser.add_argument('--review-note',required=True,
                        help='Actual human/agent visual review observations and limits')
    parser.add_argument('--allow-pending-playback', action='store_true',
                        help='Assemble a clearly pending package after frame review; does not pass playback or listening gates')
    args=parser.parse_args()
    root=ROOT/'output'/args.slug
    timing=json.loads((root/f'{args.slug}_timing.json').read_text())
    fixture_path, fixture_hash = fixture_contract(args.slug, args.scene)
    if args.slug[:2] in ('01', '02', '03', '04') and digest(ROOT/fixture_path) != fixture_hash:
        raise ValueError('Fixture identity changed')
    previews={q:json.loads((root/f'{args.slug}_{q}_probe.json').read_text()) for q in ('preview','final')}
    storage = {}
    strict_receipts = {}
    producer_sources = {}
    for q,record in previews.items():
        movie=root/f"{args.slug}_{'preview' if q=='preview' else '1080p30'}.mp4"
        strict=json.loads((root/f'{args.slug}_{q}_strict_decode_v3.json').read_text())
        strict_receipts[q] = strict
        expected_width, expected_height, expected_fps = ((854, 480, 15) if q == 'preview' else (1920, 1080, 30))
        timeline = strict.get('video_timeline', {})
        if (strict.get('verification_version') != 3 or strict.get('full_decode') != 'passed'
                or strict.get('sha256') != digest(movie)
                or strict.get('decode_returncode') != 0
                or '-xerror' not in strict.get('decode_command', [])
                or strict.get('diagnostics', '').strip()
                or strict.get('audio_expected') != timing.get('audio_expected', False)
                or (strict.get('width'), strict.get('height'), strict.get('fps')) != (expected_width, expected_height, expected_fps)
                or timeline.get('status') != 'passed'
                or timeline.get('expected_duration') != timing['duration_seconds']
                or timeline.get('frame_count') != timing['duration_seconds'] * expected_fps):
            raise ValueError(f'{q} lacks a current strict decode receipt')
        if record['full_decode']!='passed' or digest(movie)!=record['sha256']:
            raise ValueError(f'{q} export changed or did not decode')
        require_visual_review(record, allow_pending_playback=args.allow_pending_playback)
        if timing.get('audio_expected'):
            require_narrated_review(record, allow_pending_playback=args.allow_pending_playback)
        if abs(record['duration']-timing['duration_seconds'])>1/record['fps']:
            raise ValueError('Render duration does not match timing metadata')
        storage_path = root/f"{args.slug}_{'preview' if q=='preview' else '1080p30'}_storage.json"
        storage[q] = json.loads(storage_path.read_text())
        if (storage[q].get('status') != 'complete' or
                storage[q]['minimum_sampled_free_bytes'] < storage[q]['reserve_bytes'] or
                storage[q]['free_bytes_after'] < storage[q]['reserve_bytes']):
            raise ValueError(f'{q} did not complete with its storage reserve')
        producer_sources[q] = verify_render_sources(
            storage[q], movie, root, slug=args.slug, scene=args.scene,
            audio_expected=timing.get('audio_expected', False))
        frozen, source_record = producer_sources[q]
        if (source_record['source_sha256'].get(fixture_path) != fixture_hash
                or digest(frozen/fixture_path) != fixture_hash):
            raise ValueError('Rendered fixture identity differs from the approved fixture')
    final_snapshot, final_sources = producer_sources['final']
    if producer_sources['preview'][1] != final_sources:
        raise ValueError('Preview and final were rendered from different source inputs')
    srt=(root/f'{args.slug}.srt').read_text()
    vtt=(root/f'{args.slug}.vtt').read_text()
    def parse_time(text):
        h, m, seconds = text.replace(',', '.').split(':')
        return int(h)*3600 + int(m)*60 + float(seconds)
    pattern = r'(\d\d:\d\d:\d\d[,.]\d{3}) --> (\d\d:\d\d:\d\d[,.]\d{3})'
    narration_record = None
    if timing.get('audio_expected'):
        narration_record = json.loads((root/f'{args.slug}_narration_audio.json').read_text())
    if narration_record and 'subtitle_intervals' in narration_record:
        validate_segmented_tracks(timing, narration_record, (srt, vtt))
    for track in (() if narration_record and 'subtitle_intervals' in narration_record else (srt, vtt)):
        intervals = re.findall(pattern, track)
        if len(intervals) != len(timing['cues']):
            raise ValueError('Wrong number of sidecar cues')
        for cue, (start, end) in zip(timing['cues'], intervals):
            if (cue['narration'] not in track or abs(parse_time(start)-cue.get('narration_start', cue['start'])) > .001
                    or abs(parse_time(end)-cue.get('narration_end', cue['end'])) > .001):
                raise ValueError('Narration or sidecar timing disagrees with cue source')
    narration_record = None
    if timing.get('audio_expected'):
        audio = root/f'{args.slug}_narration.wav'
        audio_meta = root/f'{args.slug}_narration_audio.json'
        narration_record = json.loads(audio_meta.read_text())
        if digest(audio) != narration_record['audio_sha256']:
            raise ValueError('Narration audio changed after timing')
    final_frames=root/f'{args.slug}_final_keyframes'
    canonical=root/f'{args.slug}_keyframes'
    snapshot=root/'source_snapshot'
    if canonical.exists():
        raise ValueError('Canonical keyframe directory already exists; inspect before replacement')
    if snapshot.exists():
        raise ValueError('Source snapshot already exists; inspect before replacement')
    shutil.copytree(final_frames,canonical)
    shutil.copy2(root/f'{args.slug}_final_contact_sheet.png',root/f'{args.slug}_contact_sheet.png')
    snapshot.mkdir()
    for relative, expected in {**final_sources['source_sha256'], **final_sources['input_sha256']}.items():
        destination = snapshot / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(final_snapshot / relative, destination)
        if digest(destination) != expected:
            raise ValueError(f'Render source snapshot changed during packaging: {relative}')
    shutil.copy2(final_snapshot / MANIFEST, snapshot / MANIFEST)
    acceptance_status = 'pending_playback_review' if args.allow_pending_playback else 'reviewed'
    pending_gates = (['Complete normal-speed preview and final playback with sound',
                      'Narration pronunciation, intelligibility and audible subtitle alignment']
                     if args.allow_pending_playback else [])
    payload={'slug':args.slug,'acceptance_status':acceptance_status,'pending_gates':pending_gates,
             'python':sys.version,'manim':importlib.metadata.version('manim'),
             'renderer':'cairo','fixture_path':fixture_path,'fixture_sha256':fixture_hash,'duration_seconds':timing['duration_seconds'],
             'final_hold_seconds':timing['final_hold_seconds'], 'renders':previews, 'render_storage_and_commands':storage,
             'strict_decode_receipts':strict_receipts, 'narration':narration_record,
             'source_sha256':final_sources['source_sha256'],
             'input_sha256':final_sources['input_sha256'],
             'source_snapshot':str(snapshot), 'review_note':args.review_note}
    (root/f'{args.slug}_manifest.json').write_text(json.dumps(payload,indent=2)+'\n')
    qa=f'''# {args.slug} quality review\n\n{args.review_note}\n\n## Verification\n\n- Fixture: `{fixture_path}`; SHA-256: `{fixture_hash}`. Production calculations tested independently.\n- Preview and final videos each passed full-file decoding, frame-rate, resolution and duration checks.\n- Timing and narration sidecars use the same beat/cue definitions; all narration text appears in both formats.\n- Actual commands, source hashes and video hashes are in the companion manifest and probe records.\n- Stored state and transition samples, plus the final hold, are in the keyframe folders.\n- Labels, colors and values refer to authored synthetic examples and do not establish clinical calibration.\n'''
    if args.allow_pending_playback:
        qa = '**Playback/listening review pending; this package is not a completed film.**\n\n' + qa
    (root/f'{args.slug}_qa.md').write_text(qa)
    print(json.dumps({'status':'assembled','acceptance_status':acceptance_status,
                      'manifest':str(root/f'{args.slug}_manifest.json')},indent=2))


if __name__=='__main__': main()
