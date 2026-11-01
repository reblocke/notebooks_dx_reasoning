"""A narrated clinical framing of the original entropy counterexample."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from manim import Scene, VGroup, Rectangle, Line, FadeIn, FadeOut, Succession, AnimationGroup
from core.components import BG, WHITE, MUTED, COLORS, label, fade_replace
from core.story01_clinical import story


class ClinicalUncertainty(Scene):
    def construct(self):
        self.camera.background_color = BG
        model = story()
        observed, absent = model['observed'], model['absent']
        cues = model['cues']
        names = ('Heart failure', 'Pneumonia', 'Malignancy')
        ys = (.75, -.05, -.85)
        self.add(label('TOY MODEL  •  ILLUSTRATIVE PROBABILITIES', 21, MUTED).move_to([0, 3.67, 0]))

        def title(text):
            return label(text, 40, WHITE, 12).move_to([0, 3.12, 0])

        def caption(text):
            return label(text, 28, WHITE, 12).move_to([0, -3.24, 0])

        def diagnoses():
            return VGroup(*[label(name, 27, color, 3.3).move_to([-4.55, y, 0])
                            for name, y, color in zip(names, ys, COLORS)])

        def chart(values):
            items = []
            for p, y, color in zip(values, ys, COLORS):
                items.append(Line([-2.45, y, 0], [1.55, y, 0], stroke_width=8, color='#374151'))
                if p:
                    bar = Rectangle(width=4*float(p), height=.19, stroke_width=0,
                                    fill_color=color, fill_opacity=1)
                    bar.move_to([-2.45+2*float(p), y, 0])
                    items.append(bar)
                percent = 100*float(p)
                display = f'{percent:.1f}%' if percent % 1 else f'{percent:.0f}%'
                items.append(label(display, 27).move_to([2.12, y, 0]))
            items.append(Line([-2.45, -1.55, 0], [1.55, -1.55, 0], stroke_width=1.5, color=MUTED))
            for value in (0, .5, 1):
                x = -2.45 + 4*value
                items.append(label(f'{value:.0%}', 19, MUTED).move_to([x, -1.82, 0]))
            return VGroup(*items)

        def heading_sub(text):
            return label(text, 25, MUTED, 12).move_to([0, 2.5, 0])

        header = title('What is the expected change?')
        subtitle = heading_sub('Before the result is known: average over possible outcomes')
        cap = caption(cues[0].caption)
        strip1 = Rectangle(width=1.8, height=.58, stroke_width=0, fill_color='#6486A8', fill_opacity=1).move_to([-3.8, .15, 0])
        strip2 = Rectangle(width=8.2, height=.58, stroke_width=0, fill_color='#AAB5C5', fill_opacity=.55).move_to([1.2, .15, 0])
        intro = VGroup(strip1, strip2,
                       label('Exudative: 18%', 27).move_to([-3.8, 1.05, 0]),
                       label('Non-exudative: 82%', 27).move_to([1.2, 1.05, 0]),
                       label('Weight = probability of the result', 27, MUTED).move_to([0, -.8, 0]),
                       label('Expected change = sum of (weight × change)', 29).move_to([0, -1.6, 0]))
        self.add(header, subtitle, cap)
        self.play(FadeIn(intro), run_time=.4)
        self.wait(8.6)

        labels = diagnoses()
        bars = chart(model['prior'])
        prior_info = VGroup(label('Before fluid result', 27, MUTED).move_to([-1, 1.72, 0]),
                            label(f'Entropy ≈ {model["prior_h"]:.3f} bits', 25).move_to([4.15, .1, 0]))
        self.play(Succession(FadeOut(intro), AnimationGroup(FadeIn(labels), FadeIn(bars), FadeIn(prior_info))),
                  fade_replace(header, title('A pleural effusion: three possible causes')),
                  fade_replace(subtitle, heading_sub('Assume exactly one cause in this teaching model')),
                  fade_replace(cap, caption(cues[1].caption)), run_time=.4)
        self.wait(9.6)

        likelihoods = VGroup(label('P(exudative | cause)', 24, MUTED, 3.6).move_to([4.25, 1.62, 0]),
                             *[label(f'{100*v:.0f}%', 29, color).move_to([4.25, y, 0])
                               for v, y, color in zip(model['likelihood'], ys, COLORS)])
        self.play(Succession(FadeOut(prior_info), FadeIn(likelihoods)),
                  fade_replace(header, title('What does the fluid result mean?')),
                  fade_replace(subtitle, heading_sub('E: the fluid meets exudative criteria')),
                  fade_replace(cap, caption(cues[2].caption)), run_time=.4)
        self.wait(6.6)

        joint_note = VGroup(label('Prior × P(E | cause)', 25, MUTED, 3.7).move_to([4.3, .85, 0]),
                            label('Joint total: 18%', 27).move_to([4.3, .2, 0]),
                            label('not yet a posterior', 22, MUTED).move_to([4.3, -.4, 0]))
        post_note = VGroup(label('Divide by P(E)', 25, MUTED).move_to([4.3, .85, 0]),
                           label('÷ 0.18', 32).move_to([4.3, .2, 0]),
                           label('Posterior totals 100%', 22, MUTED).move_to([4.3, -.4, 0]))
        self.play(Succession(FadeOut(likelihoods), FadeIn(joint_note)), fade_replace(bars, chart(observed.joint)),
                  fade_replace(header, title('Observed: exudative fluid')),
                  fade_replace(subtitle, heading_sub('Select the joint masses, then normalize')),
                  fade_replace(cap, caption(cues[3].caption)), run_time=.8)
        self.wait(2)
        self.play(fade_replace(bars, chart(observed.posterior)), fade_replace(joint_note, post_note), run_time=1)
        self.wait(4.2)

        entropy_info = VGroup(label('Prior entropy', 24, MUTED).move_to([4.25, .88, 0]),
                              label(f'≈ {model["prior_h"]:.3f} bits', 27).move_to([4.25, .35, 0]),
                              label('After E', 24, MUTED).move_to([4.25, -.35, 0]),
                              label(f'{model["observed_h"]:.3f} bits', 27).move_to([4.25, -.88, 0]))
        self.play(Succession(FadeOut(joint_note), FadeIn(entropy_info)),
                  fade_replace(header, title('This result increases uncertainty')),
                  fade_replace(subtitle, heading_sub('Posterior after observing exudative fluid')),
                  fade_replace(cap, caption(cues[4].caption)), run_time=.4)
        self.wait(4.6)

        branch = VGroup(label('Exudative • 18%', 26).move_to([-.55, 1.6, 0]),
                        label('Non-exudative • 82%', 26).move_to([3.35, 1.6, 0]))
        for name, color, y, a, b in zip(names, COLORS, ys, observed.posterior, absent.posterior):
            branch.add(label(name, 25, color, 3.4).move_to([-4.55, y, 0]),
                       label(f'{a:.0%}', 26).move_to([-.55, y, 0]),
                       label(f'{b:.2%}', 26).move_to([3.35, y, 0]))
        branch.add(label(f'H = {model["observed_h"]:.3f}', 23, MUTED).move_to([-.55, -1.4, 0]),
                   label(f'H ≈ {model["absent_h"]:.3f}', 23, MUTED).move_to([3.35, -1.4, 0]),
                   label(f'0.18 × 1.500 + 0.82 × 0.107 ≈ {model["expected_h"]:.3f} bits', 26).move_to([0, -2, 0]),
                   label(f'Expected change ≈ −{model["expected_gain"]:.3f} bits', 25, MUTED).move_to([0, -2.55, 0]))
        self.play(Succession(AnimationGroup(FadeOut(labels), FadeOut(bars), FadeOut(entropy_info)), FadeIn(branch)),
                  fade_replace(header, title('Average before the result is known')),
                  fade_replace(subtitle, heading_sub('Weight each posterior entropy by its outcome probability')),
                  fade_replace(cap, caption(cues[5].caption)), run_time=.4)
        self.wait(7.2)

        final_info = VGroup(label(f'After E: {model["observed_h"]:.3f} bits', 26).move_to([4.25, .45, 0]),
                            label('Diagnosis unresolved', 24, MUTED, 3.7).move_to([4.25, -.25, 0]))
        self.play(Succession(FadeOut(branch), AnimationGroup(FadeIn(labels), FadeIn(bars), FadeIn(final_info))),
                  fade_replace(header, title('This result leaves us less certain')),
                  fade_replace(subtitle, heading_sub('Observed: exudative fluid')),
                  fade_replace(cap, caption(cues[6].caption)), run_time=.4)
        self.wait(7)
