"""Producer snapshots are taken before launch and survive later checkout edits."""
import json
from pathlib import Path

import pytest

from core import provenance
import render


def test_capture_freezes_sources_and_narration_before_later_edits(tmp_path, monkeypatch):
    root = tmp_path / 'animations'
    output = root / 'output/01_test'
    output.mkdir(parents=True)
    scene = root / 'scenes/test.py'
    scene.parent.mkdir()
    scene.write_text("TITLE = 'before'\n")
    monkeypatch.setattr(provenance, 'source_files_for_film', lambda *args: [scene])
    for name in provenance.input_names('01_test', True):
        (output / name).write_text('original ' + name)
    binding = provenance.capture_render_sources(root, output, '01_test', 'test.py', True, 'preview')
    movie = output / '01_test_preview.mp4'
    movie.write_bytes(b'exported movie')
    storage = {'render_sources': binding, 'video_sha256': provenance.digest(movie)}
    scene.write_text("TITLE = 'after'\n")
    snapshot, record = provenance.verify_render_sources(
        storage, movie, output, slug='01_test', scene='test.py', audio_expected=True)
    assert (snapshot / 'scenes/test.py').read_text() == "TITLE = 'before'\n"
    assert record['source_sha256']['scenes/test.py'] != provenance.digest(scene)
    assert (snapshot / '01_test_narration.wav').read_text() == 'original 01_test_narration.wav'
    (output / '01_test_narration.wav').write_bytes(b'changed audio')
    with pytest.raises(ValueError, match='input differs'):
        provenance.verify_render_sources(storage, movie, output, slug='01_test',
                                         scene='test.py', audio_expected=True)


def test_runner_executes_the_frozen_scene_and_binds_the_result(tmp_path, monkeypatch):
    original = Path(render.__file__).resolve().parent
    root = tmp_path / 'animations'
    # A preflight needs no narration generation or production render.
    for source in provenance.source_files_for_film(original, 'preflight', 'preflight.py', False):
        destination = root / source.relative_to(original)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
    seen = {}

    class Renderer:
        returncode = 0

        def __init__(self, command, *, cwd, start_new_session):
            seen.update(command=command, cwd=Path(cwd))
            assert Path(command[-2]).is_relative_to(Path(cwd))
            assert Path(command[command.index('--config_file') + 1]).is_relative_to(Path(cwd))
            target = Path(command[command.index('--media_dir') + 1]) / 'videos/test/preflight_preview.mp4'
            target.parent.mkdir(parents=True)
            target.write_bytes(b'exported from the frozen scene')

        def poll(self):
            return 0

    monkeypatch.setattr(render, 'ROOT', root)
    monkeypatch.setattr(render.subprocess, 'Popen', Renderer)
    monkeypatch.setattr(render.sys, 'argv', ['render.py', '--goal', 'preflight', '--quality', 'preview'])
    render.main()
    output = root / 'output/preflight'
    storage = json.loads((output / 'preflight_preview_storage.json').read_text())
    snapshot, _ = provenance.verify_render_sources(
        storage, output / 'preflight_preview.mp4', output, slug='preflight',
        scene='preflight.py', audio_expected=False)
    assert snapshot == seen['cwd']
    assert snapshot != root
    assert storage['status'] == 'complete'
