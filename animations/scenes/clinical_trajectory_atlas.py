"""Four short, independent clinical-toy trajectories and encounter windows."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from manim import (Scene, Group, VGroup, Dot, Line, Rectangle, ValueTracker,
                   Transform, always_redraw, linear)
from core.components import BG, WHITE, MUTED, COLORS, label, fade_replace
from core.atlas_components import triangle, trace_axes, path, trace, bars, legend
from core.atlas_geometry import position, trace_position
from core.math import bridge, entropy
from core.story04_clinical import story


class ClinicalTrajectoryAtlas(Scene):
    def construct(self):
        self.camera.background_color = BG
        model = story()
        cases, cues = model['cases'], model['cues']
        self.add(label('TOY MODEL  •  ILLUSTRATIVE PROBABILITIES', 21, MUTED).move_to([0, 3.67, 0]))
        names = VGroup(label('A  Heart failure', 23, COLORS[0]).move_to([-4.75, 2.55, 0]),
                       label('B  Pneumonia-related', 23, COLORS[1]).move_to([0, 2.55, 0]),
                       label('C  Malignancy', 23, COLORS[2]).move_to([4.3, 2.55, 0]))
        self.add(names)

        def title(text):
            return label(text, 37, WHITE, 12).move_to([0, 3.12, 0])

        def caption(text):
            return label(text, 27, WHITE, 12).move_to([0, -3.25, 0])

        def until(t):
            if t-self.time > 1e-6:
                self.wait(t-self.time-1e-7, frozen_frame=False)

        def base():
            return Group(triangle(), legend(), trace_axes())

        header, cap = title('Diagnostic uncertainty can follow different paths'), caption(cues[0].caption)
        intro = Group(label('One cause of pleural effusion among these three', 29).move_to([0, .6, 0]),
                      label('Four separate hypothetical patients', 27, MUTED).move_to([0, -.2, 0]))
        self.add(header, cap, intro)
        until(6)
        self.remove(intro)
        examples = [np.array([1/3]*3), np.array([.8, .1, .1]), np.array([.1, .8, .1])]
        orientation = base()
        tracker = ValueTracker(0)
        def orientation_p():
            t = tracker.get_value()
            i = min(int(t), 1)
            return examples[i]*(1-(t-i)) + examples[i+1]*(t-i)
        orientation.add(always_redraw(lambda: bars(orientation_p())),
                        always_redraw(lambda: Dot(position(orientation_p()), radius=.10, color=WHITE)),
                        label('0: prior  •  1–4: after findings', 20, MUTED).move_to([3.6, -2.45, 0]),
                        label('Motion illustrates transitions', 20, MUTED).move_to([3.6, -2.72, 0]))
        self.add(orientation)
        self.play(fade_replace(header, title('One point represents one distribution')),
                  fade_replace(cap, caption(cues[1].caption)), run_time=.4)
        until(9)
        self.play(tracker.animate.set_value(1), run_time=.5, rate_func=linear)
        until(11.5)
        self.play(tracker.animate.set_value(2), run_time=.5, rate_func=linear)
        until(16)
        self.remove(orientation)

        ids = ['convergence', 'reopening', 'substitution', 'persistent_ambiguity']
        headings = ['Convergence', 'Reopening', 'Substitution', 'Persistent ambiguity']
        last_board = None
        for n, (case_id, heading) in enumerate(zip(ids, headings)):
            cue = cues[n+2]
            states = cases[case_id]['states']
            likelihoods = cases[case_id]['likelihoods']
            if last_board is not None:
                self.remove(last_board)
            board = base()
            index, alpha = [0], ValueTracker(0)
            def live():
                return bridge(states[index[0]], likelihoods[index[0]], alpha.get_value())
            moving = Group(always_redraw(lambda: bars(live())),
                           always_redraw(lambda: Dot(position(live()), radius=.10, color=WHITE)))
            history = VGroup(Dot(position(states[0]), radius=.06, color=WHITE),
                             Dot(trace_position(0, entropy(states[0])), radius=.055, color=WHITE),
                             label('0', 17).move_to(position(states[0])+[.14, .14, 0]))
            patient_note = label('New patient • own prior', 21, MUTED).move_to([3.5, 2.13, 0])
            board.add(moving, history, patient_note)
            self.add(board)
            self.remove(header, cap)
            header, cap = title(heading), caption(cue.caption)
            self.add(header, cap)
            self.wait(1)
            board.remove(patient_note)
            for i in range(4):
                index[0] = i
                alpha.set_value(0)
                event = label(f'Observed finding E{i+1}', 21, WHITE).move_to([3.5, 1.98, 0])
                self.add(event)
                self.play(alpha.animate.set_value(1), run_time=.4, rate_func=linear)
                a, b = states[i], states[i+1]
                offset = ([[-.55,.4,0],[-.65,-.15,0],[.5,.42,0],[.58,-.1,0],[0,-.48,0]][i+1]
                          if case_id == 'persistent_ambiguity' else [.14,.14,0])
                history.add(Line(position(a), position(b), color=WHITE, stroke_width=2),
                            Dot(position(b), radius=.06, color=WHITE),
                            label(str(i+1), 17).move_to(position(b)+offset),
                            Line(trace_position(i, entropy(a)), trace_position(i+1, entropy(b)), color=WHITE, stroke_width=2),
                            Dot(trace_position(i+1, entropy(b)), radius=.055, color=WHITE))
                if case_id == 'persistent_ambiguity':
                    history.add(Line(position(b), position(b)+offset, color=MUTED, stroke_width=1))
                # Nineteen, nineteen, nineteen, then eighteen preview frames
                # make exactly five seconds at both 15 and 30 fps.
                self.wait((13 if i < 3 else 12)/15)
                self.remove(event)
            if case_id == 'substitution':
                board.add(label(f'Start H = end H = {entropy(states[0]):.3f} bits', 20).move_to([3.55, 2.0, 0]))
            self.wait(2)
            moving.clear_updaters(recursive=True)
            last_board = board
        self.remove(last_board)

        def comparison():
            group = Group()
            for case_id, heading, (cx, cy) in zip(ids, headings, [(-3.3,1.0),(3.2,1.0),(-3.3,-1.3),(3.2,-1.3)]):
                states = cases[case_id]['states']
                side, bottom = 1.8, cy-.75
                center = (cx-1.35, bottom)
                group.add(label(heading, 25, WHITE, 5.7).move_to([cx, cy+.95, 0]),
                          triangle(side, center, False), path(states, center, side, small=True),
                          trace_axes(cx+.1, bottom, 2.45, 1.25, True),
                          trace(states, cx+.1, bottom, 2.45, 1.25, small=True))
            group.add(label('Shared scales: H 0–1.65 bits  •  finding index 0–4', 21, MUTED).move_to([0, -2.72, 0]))
            return group

        summary = comparison()
        self.remove(header, cap)
        header, cap = title('Four possible realized paths'), caption(cues[6].caption)
        self.add(header, cap, summary)
        until(53)
        self.remove(summary)
        states = cases['substitution']['states']
        for cue, first, last, note in zip(cues[7:10], [0,2,0], [2,4,4],
                                          ['E1 and E2 shown', 'Start already includes E1 and E2; show E3 and E4', 'Full path: leader changes, net ΔH = 0']):
            window = Group(base(), path(states, first=first, last=last),
                           trace(states, first=first, last=last), bars(states[last]),
                           label(f'Bars: ending state {last}', 20, MUTED).move_to([3.6, .42, 0]),
                           label(note, 21, MUTED, 7).move_to([3.5, 2.08, 0]))
            left, right = 1.4+4.2*first/4, 1.4+4.2*last/4
            window.add(Rectangle(width=right-left, height=1.5, stroke_color='#E69F00',
                                 stroke_width=2).move_to([(left+right)/2, -1, 0]))
            self.remove(header, cap)
            header, cap = title('One path, different encounter windows'), caption(cue.caption)
            self.add(header, cap, window)
            until(cue.end)
            self.remove(window)
        self.remove(header, cap)
        header, cap = title('Follow the evidence'), caption(cues[10].caption)
        self.add(header, cap, comparison())
        until(72)
