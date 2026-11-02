"""Final acceptance must respect listening gates and the actual producer inputs."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

from scripts import finalize_film


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


@pytest.fixture
def package(tmp_path, monkeypatch):
    """Already-decoded synthetic receipts isolate the final acceptance boundary."""
    root = tmp_path / 'animations'
    slug = '01_example_clinical_v2'
    output = root / 'output' / slug
    output.mkdir(parents=True)
    source = root / 'core/components.py'
    source.parent.mkdir()
    source.write_text("COLOR = 'original'\n")
    scene = root / 'scenes/example.py'
    scene.parent.mkdir()
    scene.write_text('from core.components import COLOR\n')
    fixture = root / 'data/manim_fixtures.json'
    fixture.parent.mkdir()
    fixture.write_text('{}')
    write_json(output / f'{slug}_timing.json', {
        'duration_seconds': 2, 'final_hold_seconds': 1, 'audio_expected': True,
        'cues': [{'start': 0, 'end': 2, 'narration': 'Test narration.'}],
    })
    (output / f'{slug}.srt').write_text('1\n00:00:00,000 --> 00:00:02,000\nTest narration.\n')
    (output / f'{slug}.vtt').write_text('WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nTest narration.\n')
    (output / f'{slug}_narration.md').write_text('Test narration.\n')
    audio = output / f'{slug}_narration.wav'
    audio.write_bytes(b'fixed narration')
    write_json(output / f'{slug}_narration_audio.json', {'audio_sha256': digest(audio)})
    frames = output / f'{slug}_final_keyframes'
    frames.mkdir()
    (frames / 'final_hold.png').write_bytes(b'previously reviewed frame')
    (output / f'{slug}_final_contact_sheet.png').write_bytes(b'reviewed contact sheet')
    input_names = [f'{slug}_timing.json', f'{slug}.srt', f'{slug}.vtt',
                   f'{slug}_narration.md', f'{slug}_narration.wav', f'{slug}_narration_audio.json']
    for quality, tag, fps, width, height in [
        ('preview', 'preview', 15, 854, 480), ('final', '1080p30', 30, 1920, 1080),
    ]:
        movie = output / f'{slug}_{tag}.mp4'
        movie.write_bytes(f'previously decoded {quality} movie'.encode())
        snapshot = output / 'render_sources' / quality
        (snapshot / 'core').mkdir(parents=True)
        (snapshot / 'core/components.py').write_bytes(source.read_bytes())
        (snapshot / 'scenes').mkdir()
        (snapshot / 'scenes/example.py').write_bytes(scene.read_bytes())
        (snapshot / 'data').mkdir()
        (snapshot / 'data/manim_fixtures.json').write_bytes(fixture.read_bytes())
        for name in input_names:
            (snapshot / name).write_bytes((output / name).read_bytes())
        write_json(snapshot / 'render_sources.json', {
            'version': 1, 'slug': slug, 'scene': 'example.py', 'audio_expected': True,
            'source_sha256': {'core/components.py': digest(source), 'scenes/example.py': digest(scene),
                              'data/manim_fixtures.json': digest(fixture)},
            'input_sha256': {name: digest(output / name) for name in input_names},
        })
        write_json(output / f'{slug}_{tag}_storage.json', {
            'status': 'complete', 'reserve_bytes': 100,
            'minimum_sampled_free_bytes': 200, 'free_bytes_after': 200,
            'video_sha256': digest(movie),
            'render_sources': {'snapshot': str(snapshot),
                               'manifest_sha256': digest(snapshot / 'render_sources.json')},
        })
        write_json(output / f'{slug}_{quality}_strict_decode_v3.json', {
            'verification_version': 3, 'full_decode': 'passed', 'sha256': digest(movie),
            'decode_returncode': 0, 'decode_command': ['ffmpeg', '-xerror'],
            'diagnostics': '', 'audio_expected': True, 'width': width, 'height': height,
            'fps': fps, 'video_timeline': {'status': 'passed', 'expected_duration': 2,
                                         'frame_count': 2 * fps},
        })
        write_json(output / f'{slug}_{quality}_probe.json', {
            'full_decode': 'passed', 'sha256': digest(movie), 'duration': 2, 'fps': fps,
            'visual_review': 'passed', 'frame_review': 'passed',
            'playback_review': 'passed', 'audio_review': 'passed',
        })
    monkeypatch.setattr(finalize_film, 'ROOT', root)
    monkeypatch.setattr(finalize_film, 'FIXTURE_HASH', digest(fixture))
    monkeypatch.setattr(finalize_film, 'source_files_for_film', lambda *args: [source])
    monkeypatch.setattr(sys, 'argv', ['finalize_film.py', '--slug', slug,
                                   '--scene', 'example.py', '--review-note', 'Synthetic review.'])
    return output, slug, source


@pytest.mark.parametrize('quality', ['preview', 'final'])
@pytest.mark.parametrize('gate', ['playback_review', 'audio_review'])
@pytest.mark.parametrize('status', ['pending', 'failed', None])
def test_narrated_acceptance_requires_playback_and_listening(package, quality, gate, status):
    output, slug, _ = package
    path = output / f'{slug}_{quality}_probe.json'
    probe = json.loads(path.read_text())
    if status is None:
        probe.pop(gate)
    else:
        probe[gate] = status
    write_json(path, probe)
    with pytest.raises(ValueError, match='playback|listening|audio'):
        finalize_film.main()
    assert not (output / f'{slug}_keyframes').exists()


def test_finalizer_packages_the_frozen_render_source_after_checkout_changes(package):
    output, slug, source = package
    original = source.read_bytes()
    source.write_text("COLOR = 'changed after rendering'\n")
    finalize_film.main()
    assert (output / 'source_snapshot/core/components.py').read_bytes() == original
    manifest = json.loads((output / f'{slug}_manifest.json').read_text())
    assert manifest['source_sha256']['core/components.py'] == hashlib.sha256(original).hexdigest()
    assert manifest['acceptance_status'] == 'reviewed'


def test_pending_listening_can_only_produce_an_explicit_pending_package(package):
    output, slug, _ = package
    for quality in ('preview', 'final'):
        path = output / f'{slug}_{quality}_probe.json'
        probe = json.loads(path.read_text())
        probe.update(playback_review='pending', audio_review='pending')
        write_json(path, probe)
    sys.argv.append('--allow-pending-playback')
    finalize_film.main()
    manifest = json.loads((output / f'{slug}_manifest.json').read_text())
    assert manifest['acceptance_status'] == 'pending_playback_review'
    assert manifest['pending_gates']


@pytest.mark.parametrize('gate', ['playback_review', 'audio_review'])
def test_pending_option_never_accepts_a_failed_review(package, gate):
    output, slug, _ = package
    path = output / f'{slug}_preview_probe.json'
    probe = json.loads(path.read_text())
    probe[gate] = 'failed'
    write_json(path, probe)
    sys.argv.append('--allow-pending-playback')
    with pytest.raises(ValueError, match='playback|listening|audio'):
        finalize_film.main()


@pytest.mark.parametrize('fault', ['snapshot', 'movie_binding', 'missing_provenance', 'different_sources', 'changed_input'])
def test_finalizer_rejects_invalid_render_provenance_before_writing(package, fault):
    output, slug, _ = package
    storage_path = output / f'{slug}_1080p30_storage.json'
    storage = json.loads(storage_path.read_text())
    snapshot = Path(storage['render_sources']['snapshot'])
    if fault in ('snapshot', 'different_sources'):
        (snapshot / 'core/components.py').write_text("COLOR = 'different'\n")
        if fault == 'different_sources':
            manifest_path = snapshot / 'render_sources.json'
            manifest = json.loads(manifest_path.read_text())
            manifest['source_sha256']['core/components.py'] = digest(snapshot / 'core/components.py')
            write_json(manifest_path, manifest)
            storage['render_sources']['manifest_sha256'] = digest(manifest_path)
    elif fault == 'changed_input':
        (output / f'{slug}_narration.wav').write_bytes(b'not the rendered narration')
    elif fault == 'movie_binding':
        storage['video_sha256'] = 'stale movie hash'
    else:
        storage.pop('render_sources')
    write_json(storage_path, storage)
    with pytest.raises(ValueError, match='source|provenance|snapshot|render'):
        finalize_film.main()
    assert not (output / f'{slug}_keyframes').exists()
    assert not (output / 'source_snapshot').exists()


def test_finalizer_rejects_self_consistent_but_unapproved_frozen_fixture(package):
    output, slug, _ = package
    path=output/f'{slug}_preview_storage.json'
    storage=json.loads(path.read_text())
    snapshot=Path(storage['render_sources']['snapshot'])
    fixture=snapshot/'data/manim_fixtures.json'
    fixture.write_text('{"changed": true}')
    manifest_path=snapshot/'render_sources.json'
    manifest=json.loads(manifest_path.read_text())
    manifest['source_sha256']['data/manim_fixtures.json']=digest(fixture)
    write_json(manifest_path,manifest)
    storage['render_sources']['manifest_sha256']=digest(manifest_path)
    write_json(path,storage)
    with pytest.raises(ValueError,match='approved fixture'):
        finalize_film.main()
    assert not (output/f'{slug}_keyframes').exists()
    assert not (output/'source_snapshot').exists()
