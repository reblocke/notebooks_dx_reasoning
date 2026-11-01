"""Freeze producer inputs before rendering and bind them to the exported movie."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile


MANIFEST = 'render_sources.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_files_for_film(root, slug, scene, audio_expected):
    root = Path(root)
    names = ['pyproject.toml', 'uv.lock', 'manim.cfg', 'render.py',
             'core/__init__.py', 'data/manim_fixtures.json', 'core/math.py',
             'core/components.py', 'core/cues.py', 'core/provenance.py',
             'scripts/review_video.py', 'scripts/finalize_film.py']
    if slug != 'preflight':
        names.append(f'core/story{slug[:2]}.py')
    names.append(f'scenes/{scene}')
    if slug.startswith('02_'):
        names.append('core/rulers.py')
    if slug.startswith('03_'):
        names.extend(['core/entropy_geometry.py', 'core/entropy_components.py'])
    if slug.startswith('04_'):
        names.extend(['core/atlas_geometry.py', 'core/atlas_components.py'])
    if audio_expected:
        names.extend([f'core/story{slug[:2]}_clinical.py', 'core/narration.py',
                      'core/voice_config.py'])
    return [root / name for name in names]


def input_names(slug, audio_expected):
    if slug == 'preflight':
        return []
    names = [f'{slug}_timing.json', f'{slug}.srt', f'{slug}.vtt', f'{slug}_narration.md']
    if audio_expected:
        names.extend([f'{slug}_narration.wav', f'{slug}_narration_audio.json'])
    return names


def capture_render_sources(root, output, slug, scene, audio_expected, quality):
    """The scene is run from this copy, so later checkout edits cannot change it."""
    root, output = Path(root), Path(output)
    parent = output / 'render_sources'
    parent.mkdir(exist_ok=True)
    snapshot = Path(tempfile.mkdtemp(prefix=f'{quality}-', dir=parent))
    record = {'version': 1, 'slug': slug, 'scene': scene,
              'audio_expected': audio_expected, 'source_sha256': {}, 'input_sha256': {}}
    for source in source_files_for_film(root, slug, scene, audio_expected):
        relative = str(source.relative_to(root))
        destination = snapshot / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        record['source_sha256'][relative] = digest(destination)
    for name in input_names(slug, audio_expected):
        shutil.copy2(output / name, snapshot / name)
        record['input_sha256'][name] = digest(snapshot / name)
    manifest = snapshot / MANIFEST
    manifest.write_text(json.dumps(record, indent=2) + '\n')
    return {'snapshot': str(snapshot), 'manifest_sha256': digest(manifest)}


def _relative_file(root, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or path == Path('.'):
        raise ValueError('Render source manifest contains a non-relative file path')
    return root / path


def verify_render_sources(storage, movie, output, *, slug, scene, audio_expected):
    """Check the movie binding, frozen files, and current package input sidecars."""
    binding = storage.get('render_sources')
    if not isinstance(binding, dict) or storage.get('video_sha256') != digest(movie):
        raise ValueError('Export lacks movie-bound render-time source provenance')
    try:
        snapshot = Path(binding['snapshot'])
        manifest = snapshot / MANIFEST
        if digest(manifest) != binding['manifest_sha256']:
            raise ValueError('Render source manifest changed after rendering')
        record = json.loads(manifest.read_text())
        sources, inputs = record['source_sha256'], record['input_sha256']
        if record.get('version') != 1 or not isinstance(sources, dict) or not sources or not isinstance(inputs, dict):
            raise ValueError('Invalid render-time source manifest')
        if (record.get('slug'), record.get('scene'), record.get('audio_expected')) != (slug, scene, audio_expected):
            raise ValueError('Render source provenance belongs to a different film or scene')
        if set(inputs) != set(input_names(slug, audio_expected)):
            raise ValueError('Render source provenance omits required package inputs')
        if f'scenes/{scene}' not in sources:
            raise ValueError('Render source provenance omits the scene')
        for group in (sources, inputs):
            for relative, expected in group.items():
                if digest(_relative_file(snapshot, relative)) != expected:
                    raise ValueError(f'Render source snapshot changed: {relative}')
        for relative, expected in inputs.items():
            if digest(_relative_file(Path(output), relative)) != expected:
                raise ValueError(f'Package input differs from the rendered input: {relative}')
    except (KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        raise ValueError('Incomplete render-time source provenance') from exc
    return snapshot, record
