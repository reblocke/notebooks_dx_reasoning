import pytest

from core.story01_clinical import story


def test_clinical_story_preserves_mathematical_fixture():
    data = story()
    assert data['prior'] == [0.9, 0.05, 0.05]
    assert data['likelihood'] == [0.1, 0.9, 0.9]
    assert data['observed'].posterior == pytest.approx([.5, .25, .25])
    assert data['absent'].posterior == pytest.approx([81/82, 1/164, 1/164])
    assert data['observed'].evidence_probability == pytest.approx(.18)
    assert data['expected_h'] == pytest.approx(.357914141, abs=1e-8)
    assert data['expected_gain'] == pytest.approx(.211081452, abs=1e-8)
    assert data['observed_h'] - data['prior_h'] == pytest.approx(.931004406, abs=1e-8)


def test_clinical_timing_and_final_hold():
    cues = story()['cues']
    assert [(c.start, c.end) for c in cues] == [(0, 9), (9, 19), (19, 26),
            (26, 34), (34, 39), (39, 47), (47, 54)]
    assert cues[-1].end - cues[-1].start == 7
