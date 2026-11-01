"""The same illustrative binary update on three common coordinate systems."""
from math import pi
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from manim import Scene, VGroup, ValueTracker, Square, FadeIn, FadeOut, Succession, AnimationGroup, always_redraw, linear
from core.components import BG, MUTED, label, fade_replace
from core.rulers import BLUE, dynamic_marks, ruler_rows, screen_x
from core.story02_clinical import story


class ClinicalCoordinates(Scene):
    def construct(self):
        self.camera.background_color = BG
        data = story()
        examples, cues = data['examples'], data['cues']
        row_labels = [f"Patient {i}: {e['prior']:.0%}" for i, e in enumerate(examples, 1)]
        self.add(label('TOY MODEL  •  ILLUSTRATIVE PROBABILITIES', 21, MUTED).move_to([0, 3.68, 0]))

        def title(text):
            return label(text, 40, max_width=12).move_to([0, 3.13, 0])

        def subtitle(text):
            return label(text, 25, MUTED, 12).move_to([0, 2.55, 0])

        def caption(text):
            return label(text, 28, max_width=12).move_to([0, -3.25, 0])

        def foot(text):
            return label(text, 23, MUTED, 12).move_to([0, -2.35, 0])

        def values(kind):
            if kind == 'probability':
                lines = ('10→25%  +15 pp', '50→75%  +25 pp', '90→96.43%  +6.43 pp')
            elif kind == 'odds':
                lines = ('1/9 → 1/3  ×3', '1 → 3  ×3', '9 → 27  ×3')
            else:
                lines = ('−2.197 → −1.099', '0 → +1.099', '+2.197 → +3.296')
            return VGroup(*[label(text, 23, max_width=3.05).move_to([5.15, 1.38-i*1.22, 0])
                            for i, text in enumerate(lines)])

        def axes(kind, after=False):
            return ruler_rows(examples, kind, show_after=after, row_labels=row_labels)

        header = title('One finding, three starting beliefs')
        sub = subtitle('Pneumonia versus no pneumonia  •  separate patients')
        cap = caption(cues[0].caption)
        key = label('Open circle: before     Filled diamond: after', 21, MUTED).move_to([0, 2.05, 0])
        note = foot('Three independent hypothetical starting probabilities')
        probability = axes('probability')
        self.add(header, sub, cap, key, note, probability)
        self.wait(8)

        self.play(fade_replace(header, title('One hypothetical positive test')),
                  fade_replace(sub, subtitle('P(positive | pneumonia) / P(positive | no pneumonia) = 3')),
                  fade_replace(note, foot('The same LR = 3 applies to each patient')),
                  fade_replace(cap, caption(cues[1].caption)), run_time=.4)
        self.wait(7.6)

        self.play(fade_replace(header, title('Probability changes differ')),
                  fade_replace(sub, subtitle('Same finding, same LR = 3')),
                  fade_replace(note, foot('Changes are percentage points, not relative percent changes')),
                  fade_replace(cap, caption(cues[2].caption)), run_time=.4)
        progress = ValueTracker(0)
        moving = always_redraw(lambda: dynamic_marks(examples, 'probability', progress.get_value()))
        self.add(moving)
        self.play(progress.animate.set_value(1), run_time=1.5, rate_func=linear)
        moving.clear_updaters(recursive=True)
        probability_values = values('probability')
        self.play(FadeIn(probability_values), run_time=.4)
        self.wait(4.7)

        odds = VGroup(axes('odds', after=True), values('odds'))
        self.play(Succession(AnimationGroup(FadeOut(probability), FadeOut(moving), FadeOut(probability_values)), FadeIn(odds)),
                  fade_replace(header, title('The same update in odds')),
                  fade_replace(sub, subtitle('Changing coordinates: no new finding')),
                  fade_replace(note, foot('Odds = probability / (1 − probability)  •  common scale: 0 to 30')),
                  fade_replace(cap, caption(cues[3].caption)), run_time=.4)
        self.wait(6.6)

        logs = VGroup(axes('log_odds', after=True), values('log_odds'))
        self.play(Succession(FadeOut(odds), FadeIn(logs)),
                  fade_replace(header, title('Equal shifts in natural-log odds')),
                  fade_replace(sub, subtitle('Same update again  •  natural logarithm, base e')),
                  fade_replace(note, foot('Each displacement = +ln(3) ≈ +1.099 natural-log units')),
                  fade_replace(cap, caption(cues[4].caption)), run_time=.4)
        self.wait(7.6)

        inverse_axes = axes('log_odds')
        for i, example in enumerate(examples):
            inverse_axes.add(Square(side_length=.20, color=BLUE, fill_opacity=0, stroke_width=2)
                             .rotate(pi/4).move_to([screen_x(example['posterior'], 'log_odds'),
                                                   1.38-i*1.22, 0]))
        progress = ValueTracker(1)
        inverse = always_redraw(lambda: dynamic_marks(examples, 'log_odds', progress.get_value(), inverse=True))
        self.play(Succession(FadeOut(logs), AnimationGroup(FadeIn(inverse_axes), FadeIn(inverse))),
                  fade_replace(header, title('Reverse the mathematical update')),
                  fade_replace(sub, subtitle('LR = 1/3  •  not a negative-test likelihood ratio')),
                  fade_replace(key, label('Circle: original     Outline diamond: inverse start     Filled: current',
                                       20, MUTED, 12).move_to([0, 2.05, 0])),
                  fade_replace(note, foot('Subtract ln(3); the starting probabilities and odds return')),
                  fade_replace(cap, caption(cues[5].caption)), run_time=.4)
        self.play(progress.animate.set_value(0), run_time=1.5, rate_func=linear)
        inverse.clear_updaters(recursive=True)
        self.wait(2.7)

        recap = VGroup(axes('log_odds', after=True), values('log_odds'))
        self.play(Succession(AnimationGroup(FadeOut(inverse_axes), FadeOut(inverse)), FadeIn(recap)),
                  fade_replace(header, title('One update, three descriptions')),
                  fade_replace(sub, subtitle('Forward LR = 3: recap, not another finding')),
                  fade_replace(key, label('Open circle: before     Filled diamond: after', 21, MUTED).move_to([0, 2.05, 0])),
                  fade_replace(note, foot('Equal log-odds shifts do not imply equal uncertainty changes')),
                  fade_replace(cap, caption(cues[6].caption)), run_time=.4)
        self.wait(5)
