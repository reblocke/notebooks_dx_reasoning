"""Check actual atlas primitives against the shared numerical coordinates."""
import unittest
import numpy as np
from core.atlas_components import path, trace, bars, heatmap
from core.atlas_geometry import position, trace_position
from core.math import entropy
from core.story04 import story


class AtlasGeometry(unittest.TestCase):
    def test_heatmap_pixel_scale_and_boundary(self):
        pixels = heatmap().pixel_array
        h,w = pixels.shape[:2]
        self.assertEqual(pixels[0,0,3], 0)
        vertex = pixels[h-1,0,:3].astype(float)
        center = pixels[round(2*(h-1)/3), w//2, :3].astype(float)
        self.assertTrue(np.allclose(vertex, [28,45,67], atol=1))
        self.assertTrue(np.allclose(center, [94,115,137], atol=1))

    def test_actual_path_and_trace_endpoints(self):
        for case in story()['cases'].values():
            states=case['states']; p=path(states); t=trace(states)
            for i in range(4):
                np.testing.assert_allclose(p[i].get_start(),position(states[i]))
                np.testing.assert_allclose(p[i].get_end(),position(states[i+1]))
                np.testing.assert_allclose(t[i].get_start(),trace_position(i,entropy(states[i])))
                np.testing.assert_allclose(t[i].get_end(),trace_position(i+1,entropy(states[i+1])))
            for pstate in states:
                chart=bars(pstate)
                for i,value in enumerate(pstate):
                    self.assertAlmostEqual(chart[i*4+2].get_length(),3.35*value,places=8)

if __name__ == '__main__': unittest.main()
