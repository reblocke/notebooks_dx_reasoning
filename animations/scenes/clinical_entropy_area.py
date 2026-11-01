"""Clinical entropy-area cut, using the same fixed probability and bit scales."""
from pathlib import Path
import sys
from math import log2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from manim import Scene, VGroup, Rectangle, Line, ValueTracker, FadeIn, FadeOut, always_redraw, linear
from core.components import BG, WHITE, MUTED, COLORS, label, fade_replace
from core.entropy_geometry import rectangle_geometry
from core.math import entropy, bridge
from core.story03_clinical import story


class ClinicalEntropyArea(Scene):
    def construct(self):
        self.camera.background_color = BG
        model = story()
        states, cues = model['states'], model['cues']
        names = ('A  Heart failure', 'B  Pneumonia-related', 'C  Malignancy')
        x0, y0, width, height, max_h = -5.3, -1.25, 7.8, 3.8, 7.2
        self.add(label('TOY MODEL  •  ILLUSTRATIVE PROBABILITIES', 21, MUTED).move_to([0, 3.67, 0]))

        def title(text):
            return label(text, 38, WHITE, 12).move_to([0, 3.12, 0])

        def caption(text):
            return label(text, 27, WHITE, 12).move_to([0, -3.25, 0])

        def axes():
            group = VGroup(Line([x0, y0, 0], [x0+width, y0, 0], color=WHITE),
                           Line([x0, y0, 0], [x0, y0+height, 0], color=WHITE))
            for v in (0, .25, .5, .75, 1):
                group.add(label(f'{v:.0%}', 20, MUTED).move_to([x0+width*v, y0-.25, 0]))
            for v in (0, 1, 2, 4, 6, 7.2):
                group.add(label(f'{v:g}', 19, MUTED).move_to([x0-.3, y0+height*v/max_h, 0]))
            group.add(label('Cumulative probability', 23, MUTED).move_to([x0+width/2, -1.95, 0]),
                      label('Surprisal: −log₂(p) bits', 23, MUTED).move_to([-1.35, 2.65, 0]))
            return group

        def drawing(p, categories=(0, 1, 2)):
            geometry = rectangle_geometry(p, plot_width=width, plot_height=height, max_surprisal=max_h)
            group = VGroup()
            for i in categories:
                r = geometry[i]
                box = Rectangle(width=r.width, height=r.height, stroke_color=COLORS[i], stroke_width=2,
                                fill_color=COLORS[i], fill_opacity=.58)
                group.add(box.move_to([x0+r.left+r.width/2, y0+r.height/2, 0]))
            if 0 in categories and geometry[0].p <= .02:
                r = geometry[0]
                top = [x0+r.width/2, y0+r.height, 0]
                group.add(Line(top, [top[0]+.5, top[1], 0], color=WHITE),
                          label(f'{100*r.p:.1f}%', 21).move_to([top[0]+.78, top[1], 0]))
            return group

        def details(p, mode='values'):
            geo = rectangle_geometry(p, plot_width=width, plot_height=height, max_surprisal=max_h)
            group = VGroup()
            for i, (name, color, r) in enumerate(zip(names, COLORS, geo)):
                y = 1.6-i*.68
                group.add(label(name, 23, color, 3.5).move_to([4.3, y, 0]))
                value = f'{100*r.p:.1f}%'
                extra = (f'  ×  {r.surprisal:.2f}  ≈  {r.contribution:.2f} bits'
                         if mode == 'areas' or (mode == 'area_A' and i == 0) else '')
                group.add(label(value+extra, 20, WHITE, 3.6).move_to([4.3, y-.29, 0]))
            group.add(label(f'H = {entropy(p):.3f} bits', 26).move_to([4.3, -.8, 0]))
            group.add(Line([3.05, -1.28, 0], [5.55, -1.28, 0], color=MUTED, stroke_width=5),
                      Line([3.05, -1.28, 0], [3.05+2.5*entropy(p)/log2(3), -1.28, 0], color=WHITE, stroke_width=5),
                      label('0', 17, MUTED).move_to([3.05, -1.55, 0]),
                      label('log₂(3) bits', 17, MUTED).move_to([5.2, -1.55, 0]))
            return group

        def until(t):
            if t-self.time > 1e-6:
                # Static waits floor frame counts; use the dynamic frame clock
                # so a tiny rounding guard cannot discard a required frame.
                self.wait(t-self.time-1e-7, frozen_frame=False)

        header, cap = title('Entropy is expected surprise'), caption(cues[0].caption)
        p = states['R0']['p']
        panel = details(p)
        strip = VGroup()
        left = x0
        for probability, color in zip(p, COLORS):
            strip.add(Rectangle(width=width*probability, height=.2, stroke_width=0,
                                fill_color=color, fill_opacity=1)
                      .move_to([left+width*probability/2, y0+.1, 0]))
            left += width*probability
        width_note = label('Width = probability  •  total width 100%', 23, MUTED)
        width_note.move_to([x0+width/2, -.5, 0])
        self.add(header, cap, axes(), panel, strip, width_note,
                 label('Pleural effusion • exactly one cause', 20, MUTED, 3.8).move_to([4.25, 2.25, 0]))
        until(6)
        self.remove(strip, width_note)
        rects = drawing(p, (0,))
        self.play(FadeIn(rects), fade_replace(header, title('One rectangle: width × height')),
                  fade_replace(cap, caption(cues[1].caption)), fade_replace(panel, details(p, 'area_A')), run_time=.4)
        until(14)
        remaining = drawing(p, (1, 2))
        self.play(FadeIn(remaining), fade_replace(panel, details(p, 'areas')),
                  fade_replace(header, title('Add the three areas')),
                  fade_replace(cap, caption(cues[2].caption)), run_time=.4)
        self.remove(remaining)
        rects.add(*remaining.submobjects)
        self.add(rects)
        until(22)
        tracker = ValueTracker(.1)
        def rare_p():
            a = tracker.get_value()
            return [a, (1-a)/2, (1-a)/2]
        rare_rects = always_redraw(lambda: drawing(rare_p()))
        rare_panel = always_redraw(lambda: details(rare_p(), 'areas'))
        self.remove(rects, panel)
        self.add(rare_rects, rare_panel)
        self.play(fade_replace(header, title('Separate hypothetical example')),
                  fade_replace(cap, caption(cues[3].caption)), run_time=.4)
        until(23.4)
        self.play(tracker.animate.set_value(.01), run_time=2.6, rate_func=linear)
        rare_rects.update(0)
        rare_panel.update(0)
        rare_rects.clear_updaters(recursive=True)
        rare_panel.clear_updaters(recursive=True)
        selected = label('Heart failure contributions:  50% → 0.50   •   10% → 0.33   •   1% → 0.07 bits',
                         21, WHITE, 11.5).move_to([0, -2.47, 0])
        self.add(selected)
        until(32)
        self.remove(rare_rects, rare_panel, selected)
        rects, panel = drawing(states['U']['p']), details(states['U']['p'], 'areas')
        self.add(rects, panel)
        self.play(fade_replace(header, title('Equal probabilities maximize entropy')),
                  fade_replace(cap, caption(cues[4].caption)), run_time=.4)
        until(35.2)
        self.play(fade_replace(rects, drawing(states['C']['p'])),
                  fade_replace(header, title('Concentrated prior: lower entropy')),
                  fade_replace(panel, details(states['C']['p'], 'areas')), run_time=.4)
        until(39)
        update = ValueTracker(0)
        def posterior():
            return bridge(model['prior'], model['likelihood'], update.get_value())
        changing_rects = always_redraw(lambda: drawing(posterior()))
        changing_panel = always_redraw(lambda: details(posterior(), 'areas'))
        self.remove(rects, panel)
        self.add(changing_rects, changing_panel)
        self.play(fade_replace(header, title('Observed: exudative fluid')),
                  fade_replace(cap, caption(cues[5].caption)), run_time=.4)
        likelihoods = label('P(E | A / B / C) = 10 / 90 / 90%', 20, WHITE, 3.6).move_to([4.25, -2.08, 0])
        self.add(likelihoods)
        self.play(update.animate.set_value(1), run_time=2.6, rate_func=linear)
        changing_rects.update(0)
        changing_panel.update(0)
        changing_rects.clear_updaters(recursive=True)
        changing_panel.clear_updaters(recursive=True)
        until(47.6)
        formula = label('H = −Σ p log₂(p)', 28).move_to([0, -2.5, 0])
        self.play(fade_replace(header, title('Entropy is probability-weighted surprise')),
                  fade_replace(cap, caption(cues[6].caption)), FadeOut(likelihoods), FadeIn(formula), run_time=.4)
        until(54)
