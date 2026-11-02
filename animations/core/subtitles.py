"""Optional measured phrase subtitles for longer narrated films.

Legacy Cue and narration receipts are deliberately unchanged. New films supply
explicit segments whose joined text must equal each cue's complete narration.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import textwrap


def normalized(text):
    return ' '.join(text.split())


def validate_segments(cues, segments):
    if set(segments) != {c.beat_id for c in cues}:
        raise ValueError('Speech segment cue IDs disagree')
    for cue in cues:
        parts = segments[cue.beat_id]
        if (not parts or any(not isinstance(s, str) or not s.strip() for s in parts)
                or normalized(' '.join(parts)) != normalized(cue.narration)):
            raise ValueError('Speech segments must preserve the complete cue narration')
        for text in parts:
            if len(textwrap.wrap(text, 42, break_long_words=False, break_on_hyphens=False)) > 2:
                raise ValueError('Subtitle segment exceeds two readable lines')


def subtitle_rows(cues, record):
    """Validate ordered measured subtitle intervals, coverage and parent windows."""
    rows = record['subtitle_intervals']
    if not rows:
        raise ValueError('Missing subtitle intervals')
    lookup = {c.beat_id: c for c in cues}
    grouped = {c.beat_id: [] for c in cues}
    last_end, ids = -1, set()
    for row in rows:
        if row['beat_id'] not in lookup or row['segment_id'] in ids:
            raise ValueError('Invalid subtitle cue or duplicate segment ID')
        cue = lookup[row['beat_id']]
        if not cue.start <= row['start'] < row['end'] <= cue.end or row['start'] < last_end:
            raise ValueError('Subtitle intervals overlap or extend beyond their cue')
        if not row['text'].strip():
            raise ValueError('Empty subtitle text')
        last_end = row['end']; ids.add(row['segment_id'])
        grouped[cue.beat_id].append(row)
    validate_segments(cues, {key: [r['text'] for r in group] for key, group in grouped.items()})
    speech = record['speech_intervals']
    if [r['beat_id'] for r in speech] != [c.beat_id for c in cues]:
        raise ValueError('Speech interval IDs disagree')
    for row in speech:
        parts = grouped[row['beat_id']]
        if row['start'] != parts[0]['start'] or row['end'] != parts[-1]['end']:
            raise ValueError('Subtitle and speech intervals disagree')
    return rows


def build_segmented_narration(cues, output, slug, segments, *, voice, rate):
    validate_segments(cues, segments)
    output = Path(output)
    audio, receipt = output/f'{slug}_narration.wav', output/f'{slug}_narration_audio.json'
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    cue_hash = hashlib.sha256(json.dumps([vars(c) for c in cues], sort_keys=True).encode()).hexdigest()
    segment_hash = hashlib.sha256(json.dumps(segments, sort_keys=True).encode()).hexdigest()
    if audio.exists() or receipt.exists():
        if not audio.exists() or not receipt.exists():
            raise ValueError('Incomplete existing narration; inspect before replacing it')
        data = json.loads(receipt.read_text())
        if (data.get('cue_source_sha256') != cue_hash or data.get('segment_source_sha256') != segment_hash
                or data.get('audio_sha256') != digest(audio) or data.get('voice') != voice
                or data.get('rate_wpm') != rate or data.get('segmentation_version') != 1):
            raise ValueError('Existing narration does not match this segmented cue source')
        subtitle_rows(cues, data)
        return data
    intervals, subtitles, files = [], [], []
    with tempfile.TemporaryDirectory(prefix='phrases-', dir=output) as temporary:
        folder = Path(temporary)
        for cue in cues:
            start = cue.start + .1
            first = start
            for number, text in enumerate(segments[cue.beat_id], 1):
                ident = f'{cue.beat_id}_{number:02d}'
                part = folder/f'{ident}.aiff'
                subprocess.run(['/usr/bin/say', '-v', voice, '-r', str(rate), '-o', str(part), text], check=True)
                duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
                    'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(part)], text=True))
                end = start + duration
                if end > cue.end - .1:
                    raise ValueError(f'{cue.beat_id} segmented narration exceeds its cue window ({end:.3f} > {cue.end-.1})')
                subtitles.append({'beat_id': cue.beat_id, 'segment_id': ident, 'text': text,
                                  'start': round(start, 3), 'end': round(end, 3), 'source_duration': duration})
                files.append(part)
                start = end + .12
            intervals.append({'beat_id': cue.beat_id, 'start': round(first, 3), 'end': round(end, 3),
                              'source_duration': end-first})
        command = ['ffmpeg', '-v', 'error', '-xerror']
        for part in files:
            command += ['-i', str(part)]
        filters = [f'[{i}:a]aresample=48000,adelay={round(row["start"]*1000)}:all=1[a{i}]'
                   for i, row in enumerate(subtitles)]
        joined = ''.join(f'[a{i}]' for i in range(len(files)))
        filters.append(f'{joined}amix=inputs={len(files)}:duration=longest:normalize=0,'
                       f'apad,atrim=duration={cues[-1].end},asetpts=PTS-STARTPTS[out]')
        candidate = folder/'complete.wav'
        command += ['-filter_complex', ';'.join(filters), '-map', '[out]', '-ar', '48000',
                    '-ac', '1', '-c:a', 'pcm_s16le', str(candidate)]
        subprocess.run(command, check=True)
        data = {'voice': voice, 'rate_wpm': rate, 'sample_rate': 48000,
                'cue_source_sha256': cue_hash, 'segment_source_sha256': segment_hash,
                'segmentation_version': 1, 'speech_intervals': intervals, 'subtitle_intervals': subtitles,
                'audio_sha256': digest(candidate),
                'os_version': subprocess.check_output(['sw_vers', '-productVersion'], text=True).strip()}
        subtitle_rows(cues, data)
        candidate.replace(audio)
    receipt.write_text(json.dumps(data, indent=2)+'\n')
    return data
