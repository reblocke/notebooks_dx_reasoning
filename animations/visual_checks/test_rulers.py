"""Test the actual Manim arrow endpoints, not a parallel geometry formula."""
import unittest
import math
from core.story02 import story
from core.rulers import DOMAINS, WIDTH, screen_x, update_arrow, dynamic_marks


class RulerGeometry(unittest.TestCase):
    def test_arrow_endpoints_and_equal_log_shifts(self):
        examples=story()['examples']
        lengths=[]
        for kind in DOMAINS:
            for row in examples:
                a=update_arrow(row['prior'],row['posterior'],kind,0)
                self.assertAlmostEqual(a.get_start()[0],screen_x(row['prior'],kind),places=10)
                self.assertAlmostEqual(a.get_end()[0],screen_x(row['posterior'],kind),places=10)
                if kind=='log_odds': lengths.append(a.get_end()[0]-a.get_start()[0])
        self.assertLess(max(lengths)-min(lengths),14.222/1920)
        self.assertAlmostEqual(lengths[0],WIDTH*math.log(3)/7,places=10)
        inverse=dynamic_marks(examples,'log_odds',0,inverse=True)
        for i,row in enumerate(examples):
            arrow=inverse[2*i]
            self.assertAlmostEqual(arrow.get_start()[0],screen_x(row['posterior'],'log_odds'),places=10)
            self.assertAlmostEqual(arrow.get_end()[0],screen_x(row['prior'],'log_odds'),places=10)


if __name__=='__main__': unittest.main()
