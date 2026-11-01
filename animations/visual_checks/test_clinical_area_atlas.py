"""Build the revised scenes without rendering and check timeline and frame bounds."""
import tempfile
import unittest

from manim import ValueTracker, tempconfig
from scenes.clinical_entropy_area import ClinicalEntropyArea
from scenes.clinical_trajectory_atlas import ClinicalTrajectoryAtlas


class ClinicalAreaAtlasChecks(unittest.TestCase):
    def test_scenes_construct_in_bounds_and_keep_final_hold(self):
        for scene_type, duration, hold in [(ClinicalEntropyArea, 54, 6),
                                           (ClinicalTrajectoryAtlas, 72, 7)]:
            with self.subTest(scene=scene_type.__name__), tempfile.TemporaryDirectory() as folder, tempconfig({'media_dir': folder}):
                scene = scene_type()
                objects, durations = [], []
                original_add = scene.add

                def add(*mobjects):
                    objects.extend(mobjects)
                    return original_add(*mobjects)

                def play(*animations, run_time=1, **kwargs):
                    durations.append(run_time)
                    scene.renderer.time += run_time
                    for animation in animations:
                        objects.append(animation.mobject)
                        objects.append(getattr(animation, 'target_mobject', None))
                        if isinstance(animation.mobject, ValueTracker) and hasattr(animation.mobject, 'target'):
                            animation.mobject.set_value(animation.mobject.target.get_value())
                    scene.update_mobjects(0)

                def wait(seconds=1, **kwargs):
                    durations.append(seconds)
                    scene.renderer.time += seconds

                scene.add, scene.play, scene.wait = add, play, wait
                scene.construct()
                self.assertAlmostEqual(sum(durations), duration, places=6)
                self.assertAlmostEqual(durations[-1], hold, places=6)
                for obj in objects:
                    if obj is None or not obj.get_all_points().size:
                        continue
                    self.assertGreaterEqual(obj.get_left()[0], -7.12)
                    self.assertLessEqual(obj.get_right()[0], 7.12)
                    self.assertGreaterEqual(obj.get_bottom()[1], -4)
                    self.assertLessEqual(obj.get_top()[1], 4)


if __name__ == '__main__':
    unittest.main()
