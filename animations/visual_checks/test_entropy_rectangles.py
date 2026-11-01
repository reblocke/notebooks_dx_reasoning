"""Real rendered rectangle objects must preserve the fixture geometry."""
import unittest
import json
from pathlib import Path
from core.entropy_components import rectangles,PLOT_WIDTH,PLOT_HEIGHT,MAX_SURPRISAL,X0,Y0

class Rectangles(unittest.TestCase):
    def test_width_height_area_and_tiny_case(self):
        f=json.loads((Path(__file__).resolve().parents[1]/'data/manim_fixtures.json').read_text())['goal_03']
        for state in f['states'].values():
            offset=0
            for box,p,h,area in zip(rectangles(state['p']),state['p'],state['surprisal_bits'],state['contribution_bits']):
                self.assertAlmostEqual(box.width,PLOT_WIDTH*p,places=10)
                self.assertAlmostEqual(box.height,PLOT_HEIGHT*h/MAX_SURPRISAL,places=10)
                self.assertAlmostEqual(box.width*box.height,area*PLOT_WIDTH*PLOT_HEIGHT/MAX_SURPRISAL,places=10)
                self.assertAlmostEqual(box.get_left()[0],X0+PLOT_WIDTH*offset,places=10)
                self.assertAlmostEqual(box.get_bottom()[1],Y0,places=10)
                offset+=p

if __name__=='__main__': unittest.main()
