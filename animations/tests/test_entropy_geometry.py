"""Independent rectangle geometry checks against the supplied data."""
import json
from pathlib import Path
import numpy as np
import pytest
from core.entropy_geometry import rectangle_geometry

F=json.loads((Path(__file__).resolve().parents[1]/'data/manim_fixtures.json').read_text())['goal_03']


def test_fixture_rectangles_and_pixel_area_scaling():
    for state in F['states'].values():
        result=rectangle_geometry(state['p'],plot_width=7.2,plot_height=4.0,max_surprisal=7.2)
        np.testing.assert_allclose([r.p for r in result],state['p'],atol=1e-10)
        np.testing.assert_allclose([r.surprisal for r in result],state['surprisal_bits'],atol=1e-10)
        np.testing.assert_allclose([r.contribution for r in result],state['contribution_bits'],atol=1e-10)
        np.testing.assert_allclose([r.left/7.2 for r in result],state['rectangle_left_edges'],atol=1e-10)
        for r in result:
            assert r.width*r.height == pytest.approx(r.contribution*7.2*4/7.2,abs=1e-10)
    rare=rectangle_geometry(F['states']['R2']['p'],plot_width=7.2,plot_height=4,max_surprisal=7.2)[0]
    assert rare.width == pytest.approx(.072,abs=1e-12)
    assert rare.surprisal == pytest.approx(6.643856189774724,abs=1e-10)


def test_hypothetical_sweep_and_bad_inputs():
    for a in np.linspace(.1,.01,41):
        p=[a,(1-a)/2,(1-a)/2]
        r=rectangle_geometry(p,plot_width=7.2,plot_height=4,max_surprisal=7.2)
        assert sum(x.width for x in r)==pytest.approx(7.2)
        assert sum(x.contribution for x in r)==pytest.approx(-sum(x*np.log2(x) for x in p))
    for p in [[1,0,0],[.5,.3],[-.1,.5,.6]]:
        with pytest.raises(ValueError):rectangle_geometry(p,plot_width=7.2,plot_height=4,max_surprisal=7.2)
