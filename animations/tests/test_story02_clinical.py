import math
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from core.story02_clinical import SLUG, story
from render import apply_clinical_timing, clinical_timing
from scripts.finalize_film import source_files_for_film


def test_clinical_cut_preserves_original_binary_updates():
    data = story()
    assert SLUG == '02_coordinate_systems_clinical_v2'
    assert [(c.start, c.end) for c in data['cues']] == [
        (0, 8), (8, 16), (16, 23), (23, 30), (30, 38), (38, 43), (43, 48)
    ]
    assert [e['prior'] for e in data['examples']] == pytest.approx([.1, .5, .9])
    assert [e['posterior'] for e in data['examples']] == pytest.approx([.25, .75, 27 / 28])
    for example in data['examples']:
        assert example['inverse'] == pytest.approx(example['prior'], abs=1e-10, rel=0)
        assert example['log_after'] - example['log_before'] == pytest.approx(math.log(3), abs=1e-10, rel=0)
    assert 'hypothetical' in data['cues'][1].narration.lower()


def test_clinical_cut_timing_is_specific_to_each_film():
    hold1, events1 = clinical_timing('01')
    hold2, events2 = clinical_timing('02')
    assert (hold1, hold2) == (7, 5)
    assert events1[-1]['settled'] == 47
    assert events2[-1]['settled'] == 43
    assert any(event['id'] == 'inverse_update' for event in events2)
    with pytest.raises(ValueError):
        clinical_timing('preflight')


def test_source_snapshot_uses_the_matching_clinical_story():
    names = {p.name for p in source_files_for_film(SLUG, 'clinical_coordinates.py', True)}
    assert {'story02.py', 'story02_clinical.py', 'rulers.py', 'narration.py'} <= names
    assert 'story01_clinical.py' not in names


@pytest.mark.parametrize(('slug', 'scene', 'story_module'), [
    ('01_uncertainty_increases_clinical_v2', 'clinical_uncertainty.py', 'story01_clinical'),
    (SLUG, 'clinical_coordinates.py', 'story02_clinical'),
    ('03_entropy_area_clinical_v2', 'clinical_entropy_area.py', 'story03_clinical'),
    ('04_trajectory_atlas_clinical_v2', 'clinical_trajectory_atlas.py', 'story04_clinical'),
])
def test_source_snapshot_imports_independently(tmp_path, slug, scene, story_module):
    root = Path(__file__).resolve().parents[1]
    for source in source_files_for_film(slug, scene, True):
        destination = tmp_path / source.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    python = root / '.venv/bin/python'
    if not python.exists():
        if importlib.util.find_spec('manim') is None:
            pytest.skip('isolated snapshot scene check requires the animation environment')
        python = Path(sys.executable)
    script = ("import sys; sys.path.insert(0, sys.argv[1]); "
              "from core.narration import make_narration; "
              f"from core.{story_module} import story; "
              f"import scenes.{Path(scene).stem}; assert story()['cues']")
    env = os.environ.copy()
    env.pop('PYTHONPATH', None)
    subprocess.run([str(python), '-I', '-c', script, str(tmp_path)], cwd=tmp_path,
                   env=env, check=True, capture_output=True, text=True)


def test_clinical_timing_uses_coordinate_cut_and_spoken_intervals():
    cues = story()['cues']
    timing = {'cues': [vars(cue).copy() for cue in cues]}
    intervals = [{'beat_id': cue.beat_id, 'start': cue.start + .1, 'end': cue.start + 2}
                 for cue in cues]
    apply_clinical_timing(timing, cues, {'speech_intervals': intervals}, '02')
    assert timing['final_hold_seconds'] == 5
    assert timing['cues'][-1]['narration_start'] == 43.1
    assert timing['cues'][-1]['caption_fully_visible_at'] == 43
    assert timing['cues'][-1]['caption_visible_end'] == 48
    intervals[-1]['beat_id'] = 'wrong'
    with pytest.raises(ValueError, match='IDs'):
        apply_clinical_timing(timing, cues, {'speech_intervals': intervals}, '02')
