"""Check real Manim bar objects against the independent probability fixture."""
import json
from pathlib import Path
import unittest
import numpy as np
from manim import Rectangle
from core.components import probability_chart, label, fade_replace


class ProbabilityBarTests(unittest.TestCase):
    def test_text_changes_by_fading_without_morphing_glyph_geometry(self):
        source = label('Before the result', 27)
        target = label('Observed: exudative fluid', 27).shift([1, 0, 0])
        animation = fade_replace(source, target)
        original = source.copy()
        animation.begin()
        for alpha, expected in [(.25, original), (.75, target), (1, target)]:
            animation.interpolate(alpha)
            self.assertAlmostEqual(source.width, expected.width)
            self.assertAlmostEqual(source.height, expected.height)
            # Pango/Cairo transforms can leave roundoff near the zero axes.
            np.testing.assert_allclose(source.get_center(), expected.get_center(),
                                       rtol=0, atol=1e-10)
        animation.finish()

    def test_lengths_preserve_prior_and_selected_joint_mass(self):
        fixture=json.loads((Path(__file__).resolve().parents[1]/'data/manim_fixtures.json').read_text())['goal_01']
        prior=fixture['prior']
        likelihood=fixture['branches'][0]['likelihood']
        group=probability_chart('Synthetic prior',prior,width=3.1,selected=likelihood)
        bars=[m for m in group.submobjects if isinstance(m,Rectangle)]
        self.assertEqual(len(bars),6)
        for i in range(3):
            self.assertAlmostEqual(bars[2*i].width,3.1*prior[i],places=10)
            self.assertAlmostEqual(bars[2*i+1].width,3.1*fixture['branches'][0]['joint_masses'][i],places=10)
        absent=probability_chart('Absent',fixture['branches'][1]['posterior'],width=3.1)
        tiny=[m for m in absent.submobjects if isinstance(m,Rectangle)]
        self.assertAlmostEqual(tiny[1].width,3.1/164,places=10)
        self.assertAlmostEqual(tiny[2].width,3.1/164,places=10)


if __name__=='__main__': unittest.main()
