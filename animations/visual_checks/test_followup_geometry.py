"""Measure actual Manim geometry rather than assuming formulas render faithfully."""
import math
import unittest
import numpy as np
from types import SimpleNamespace
from manim import VGroup, Mobject, tempconfig
from core.components import label
from core.teaching_scene import TeachingScene
from core.cohort_components import people, selected_destinations, DISEASE, NO_DISEASE
from core.leaf_components import leaf_axes, result_curve, utility_axes, utility_mark, utility_line
from core.decision_math import utility_difference


class FollowupGeometry(unittest.TestCase):
    def test_replacing_body_clears_late_added_scene_children(self):
        with tempconfig({'dry_run':True,'frame_rate':15,'pixel_width':426,'pixel_height':240}):
            scene=TeachingScene()
            scene.setup_story({'cues':[SimpleNamespace(caption='Caption')],
                               'events':[{'id':'replace','start':0,'settled':.4}]},'Title')
            original=VGroup(label('Original body'));scene.add(original);scene.body=original
            late=label('Late child');scene.add(late);original.add(late)
            scene.add(Mobject())  # Wait animations can leave a non-vector placeholder.
            replacement=VGroup(label('Replacement body'))
            scene.replace_body('replace',replacement)
            self.assertEqual(scene.mobjects,[*scene.chrome,replacement])
            self.assertNotIn(late,scene.get_mobject_family_members())

    def test_selected_people_are_exact_individuals(self):
        for a,b in [(2,9),(1,18)]:
            blue=people(a,DISEASE,(-3,0));gray=people(b,NO_DISEASE,(3,0))
            self.assertEqual(len(blue)+len(gray),a+b)
            targets=selected_destinations(a+b)
            self.assertEqual(len(set(targets)),a+b)
            for mark,target in zip(list(blue)+list(gray),targets):mark.move_to(target)
            self.assertTrue(np.allclose(blue[0].get_center(),targets[0]))

    def test_logit_axes_have_equal_physical_units_and_slope_one(self):
        _,axes=leaf_axes(True)
        dx=axes.c2p(1,0)-axes.c2p(0,0);dy=axes.c2p(0,1)-axes.c2p(0,0)
        self.assertAlmostEqual(np.linalg.norm(dx),np.linalg.norm(dy),places=12)
        curve=result_curve(axes,3,True)
        vector=curve.get_end()-curve.get_start()
        self.assertAlmostEqual(vector[0],vector[1],places=12)
        _,prob=leaf_axes()
        self.assertAlmostEqual(np.linalg.norm(prob.c2p(.5,0)-prob.c2p(0,0)),2.25,places=12)

    def test_changed_cost_moves_utility_but_not_belief(self):
        _,axes=utility_axes()
        before=utility_mark(axes,.25,1);after=utility_mark(axes,.25,4)
        self.assertAlmostEqual(before.get_x(),after.get_x(),places=12)
        self.assertTrue(np.allclose(after.get_center(),axes.c2p(.25,-2)))
        for cost in (1,2,4):
            line=utility_line(axes,cost)
            self.assertTrue(np.allclose(line.get_start(),axes.c2p(0,-cost)))
            self.assertTrue(np.allclose(line.get_end(),axes.c2p(1,4)))
