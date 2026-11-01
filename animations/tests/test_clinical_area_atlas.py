"""Numerical and cue-level guarantees for the two faster clinical cuts."""
import math

import numpy as np
import pytest

from core.entropy_geometry import rectangle_geometry
from core.math import bridge, entropy
from core.story03_clinical import story as area_story
from core.story04_clinical import story as atlas_story
from render import clinical_timing, apply_clinical_timing


def test_area_cut_retains_exact_states_and_weighted_surprise():
    data = area_story()
    assert data['cues'][-1].end == 54
    expected = {'R0': [0.5, .25, .25], 'R1': [.1, .45, .45],
                'R2': [.01, .495, .495], 'U': [1/3]*3, 'C': [.9, .05, .05]}
    for name, values in expected.items():
        p = data['states'][name]['p']
        assert p == pytest.approx(values)
        rectangles = rectangle_geometry(p, plot_width=7.8, plot_height=3.8, max_surprisal=7.2)
        assert sum(r.contribution for r in rectangles) == pytest.approx(entropy(p))
        assert [r.width for r in rectangles] == pytest.approx(np.asarray(p)*7.8)
    assert entropy(data['states']['U']['p']) == pytest.approx(math.log2(3))
    assert data['posterior'] == pytest.approx(expected['R0'])
    assert bridge(data['prior'], data['likelihood'], 1) == pytest.approx(data['posterior'])


def test_atlas_cut_reuses_frozen_bayes_paths_and_encounter_windows():
    data = atlas_story()
    assert data['cues'][-1].end == 72
    assert set(data['cases']) == {'convergence', 'reopening', 'substitution', 'persistent_ambiguity'}
    for case in data['cases'].values():
        assert len(case['states']) == 5
        for prior, likelihood, posterior in zip(case['states'], case['likelihoods'], case['states'][1:]):
            assert bridge(prior, likelihood, 1) == pytest.approx(posterior)
            mid = bridge(prior, likelihood, .5)
            assert sum(mid) == pytest.approx(1)
            assert entropy(mid) >= 0
    states = data['cases']['substitution']['states']
    assert entropy(states[0]) == pytest.approx(entropy(states[4]))
    assert entropy(states[2]) > entropy(states[0])
    assert states[0] != pytest.approx(states[4])


@pytest.mark.parametrize(('goal', 'hold', 'last'), [('03',6,54), ('04',7,72)])
def test_each_cut_uses_its_own_events_and_keyframes(goal, hold, last):
    cues = (area_story if goal == '03' else atlas_story)()['cues']
    intervals = [{'beat_id': cue.beat_id, 'start': cue.start+.1, 'end': cue.start+.5} for cue in cues]
    timing = {'cues': [vars(cue).copy() for cue in cues]}
    apply_clinical_timing(timing, cues, {'speech_intervals': intervals}, goal)
    assert clinical_timing(goal)[0] == hold
    assert timing['final_hold_seconds'] == hold
    assert timing['cues'][-1]['caption_visible_end'] == last
    assert all(0 <= k['time'] < last for k in timing['extra_keyframes'])
    if goal == '04':
        assert len([e for e in timing['events'] if '_E' in e['id']]) == 16
        assert len([k for k in timing['extra_keyframes'] if '_state_' in k['id']]) == 20
