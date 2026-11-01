"""Exercise scene construction and frame bounds without rendering a video."""
import tempfile
import unittest

from manim import tempconfig
from scenes.clinical_uncertainty import ClinicalUncertainty


class ClinicalSceneChecks(unittest.TestCase):
    def test_scene_constructs_within_frame_and_has_a_seven_second_hold(self):
        with tempfile.TemporaryDirectory() as folder, tempconfig({'media_dir': folder}):
            scene = ClinicalUncertainty()
            objects, durations = [], []
            original_add = scene.add

            def add(*mobjects):
                objects.extend(mobjects)
                return original_add(*mobjects)

            def play(*animations, run_time=1, **kwargs):
                durations.append(run_time)
                for animation in animations:
                    objects.append(animation.mobject)
                    target = getattr(animation, 'target_mobject', None)
                    if target is not None:
                        objects.append(target)

            scene.add = add
            scene.play = play
            scene.wait = lambda duration=1: durations.append(duration)
            scene.construct()
            self.assertAlmostEqual(sum(durations), 54)
            self.assertEqual(durations[-1], 7)
            for obj in objects:
                if obj is None or not obj.get_all_points().size:
                    continue
                self.assertGreaterEqual(obj.get_left()[0], -7.12)
                self.assertLessEqual(obj.get_right()[0], 7.12)
                self.assertGreaterEqual(obj.get_bottom()[1], -4)
                self.assertLessEqual(obj.get_top()[1], 4)


if __name__ == '__main__':
    unittest.main()
