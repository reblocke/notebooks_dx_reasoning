"""Observed entropy increase versus the positive expected information gain."""
from pathlib import Path
from math import log2
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from manim import (Scene, VGroup, Text, Line, Arrow, Dot, Rectangle, FadeIn, FadeOut,
                   TransformFromCopy, UP, DOWN, LEFT, RIGHT)
from core.components import BG, WHITE, MUTED, COLORS, label, probability_chart, card
from core.story01 import story


class UncertaintyIncreases(Scene):
    def construct(self):
        self.camera.background_color = BG
        model = story()
        prior, likelihood = model['prior'], model['likelihood']
        obs, absent = model['observed'], model['absent']
        cues = model['cues']
        synthetic = label('SYNTHETIC EXAMPLE  •  A, B, C are exclusive', 22, color=MUTED).move_to([0,3.68,0])
        self.add(synthetic)

        def heading(text, sub=''):
            items=[label(text,42,max_width=12).move_to([0,3.15,0])]
            if sub: items.append(label(sub,25,color=MUTED,max_width=11.8).move_to([0,2.55,0]))
            return VGroup(*items)

        def caption(text):
            return label(text,30,max_width=12.2).move_to([0,-3.25,0])

        def prior_chart(x=0,y=.3,width=4.4):
            return probability_chart('Before observing E',prior,width=width).move_to([x,y,0])

        def post_chart(x=0,y=.3,width=4.4):
            return probability_chart('Posterior after E',obs.posterior,width=width).move_to([x,y,0])

        screens=[]
        # Each screen is an explicit state, built from the same full-precision model.
        screens.append(VGroup(heading('A confident starting point'),prior_chart(),
                              label('One diagnosis begins with most of the probability.',27,color=MUTED).move_to([0,-2.05,0])))
        screens.append(VGroup(heading('One binary finding','Three exclusive diagnoses; E can be present or absent'),
                              prior_chart(-3,.1,3.4),card('Possible outcomes','E present   |   E absent',width=4.8).move_to([3,.65,0]),
                              card('Before E: uncertainty',f'H ≈ {model["prior_h"]:.3f} bits',width=4.8).move_to([3,-1,0])))
        likelihood_rows=VGroup(*[label(f'P(E | {name}) = {v:.2f}',30,color=COLORS[i]).move_to([3,1-i*.55,0])
                                 for i,(name,v) in enumerate(zip('ABC',likelihood))])
        screens.append(VGroup(heading('E fits the alternatives better','Observed outcome: E present'),
                              prior_chart(-3,.1,3.4),label('Conditional likelihoods',27,color=MUTED).move_to([3,1.62,0]),
                              likelihood_rows,label(f'Prior entropy, before E ≈ {model["prior_h"]:.3f} bits',23,color=MUTED).move_to([3,-1.55,0])))
        joint_rows=VGroup(*[label(f'{name}    {prior[i]:.2f} × {likelihood[i]:.2f}  =  {mass:.3f}',29,color=COLORS[i]).move_to([3,.75-i*.62,0])
                           for i,(name,mass) in enumerate(zip('ABC',obs.joint))])
        mass_source=probability_chart('Prior: highlighted fraction has E', prior, width=3.1, selected=likelihood).move_to([-3,.25,0])
        joint_total=card('Total joint mass',f'P(E) = {obs.evidence_probability:.2f}',width=4.6).move_to([3,-1.75,0])
        screens.append(VGroup(heading('Select the joint masses','Joint masses: diagnosis and E  •  not a posterior'),mass_source))
        mass_labels=VGroup(*[label(f'{name}  {v:.3f}',28,color=COLORS[i]).move_to([-4,.75-i*.48,0]) for i,(name,v) in enumerate(zip('ABC',obs.joint))])
        normalized_chart=post_chart(3,.1,3.1)
        normalized_labels=VGroup(
            label('Posterior total = 100%',24,color=MUTED).move_to([3,-1.85,0]),
            label('Posterior = (' + ', '.join(f'{x:.3f}' for x in obs.joint) + f') ÷ {obs.evidence_probability:.2f} = (' + ', '.join(f'{x:.2f}' for x in obs.posterior) + ')',23,color=MUTED,max_width=11.8).move_to([0,-2.45,0]))
        screens.append(VGroup(heading('Normalize within the observed branch','Divide by P(E) = 0.18 • motion connects computed states'),
                              label('Joint masses',25,color=MUTED).move_to([-4,1.38,0]),mass_labels,
                              Arrow(LEFT*1.9,RIGHT*.15,buff=.1,color=WHITE).move_to([-1.2,.2,0]),
                              label('÷ 0.18',30).move_to([-1.15,.78,0])))
        screens.append(VGroup(heading('Uncertainty increases','Entropy is calculated only for normalized distributions'),
                              prior_chart(-3,.25,3.2),post_chart(3,.25,3.2),
                              Line([-4.4,-1.58,0],[-1.6,-1.58,0],stroke_width=6,color='#374151'),
                              Line([-4.4,-1.58,0],[-4.4+2.8*model['prior_h']/log2(3),-1.58,0],stroke_width=6,color=WHITE),
                              Line([1.6,-1.58,0],[4.4,-1.58,0],stroke_width=6,color='#374151'),
                              Line([1.6,-1.58,0],[1.6+2.8*model['observed_h']/log2(3),-1.58,0],stroke_width=6,color=WHITE),
                              label(f'Before E: {model["prior_h"]:.3f} bits',27).move_to([-3,-1.95,0]),
                              label(f'After E: {model["observed_h"]:.3f} bits',27).move_to([3,-1.95,0]),
                              label('Entropy scale: 0 to log₂(3) ≈ 1.585 bits',22,color=MUTED).move_to([0,-2.45,0])))
        screens.append(VGroup(heading('The result remains unresolved','Observed: E present'),post_chart(),
                              label('Diagnosis remains unresolved',32).move_to([0,-2,0])))
        screens.append(VGroup(heading('Rewind to before the outcome','Change of perspective — not new evidence'),
                              prior_chart(-2.2,.1,3.3),card('Two possible outcomes','E present   |   E absent',width=4.4).move_to([3,.55,0]),
                              card('Historical observed E','A 50%  •  B 25%  •  C 25%',width=4.4).move_to([3,-1.1,0])))
        branches=VGroup(probability_chart('E present  •  P(E) = 0.18',obs.posterior,width=2.95).move_to([-3.25,.25,0]),
                        probability_chart('E absent  •  P(not E) = 0.82',absent.posterior,width=2.95).move_to([3.25,.25,0]),
                        label(f'H = {model["observed_h"]:.3f} bits',27).move_to([-3.25,-1.55,0]),
                        label(f'H ≈ {model["absent_h"]:.3f} bits',27).move_to([3.25,-1.55,0]))
        tree=VGroup(label('Prior: A 90%, B 5%, C 5%',23,color=MUTED).move_to([0,2.15,0]),
                    Line([-.5,1.92,0],[-2.4,1.52,0],stroke_width=1.5,color=MUTED),
                    Line([.5,1.92,0],[2.4,1.52,0],stroke_width=1.5,color=MUTED))
        screens.append(VGroup(heading('Two possible posteriors','Outcome probabilities differ from diagnosis probabilities'),tree,branches,
                              label('Each branch is a separate normalized posterior.',24,color=MUTED).move_to([0,-2.25,0])))
        small_branches=VGroup(probability_chart('E present  •  P = 0.18',obs.posterior,width=2.6).move_to([-3.25,.95,0]),
                              probability_chart('E absent  •  P = 0.82',absent.posterior,width=2.6).move_to([3.25,.95,0]),
                              label(f'H = {model["observed_h"]:.3f} bits',23,color=MUTED).move_to([-3.25,-.76,0]),
                              label(f'H ≈ {model["absent_h"]:.3f} bits',23,color=MUTED).move_to([3.25,-.76,0]))
        screens.append(VGroup(heading('Average the branch entropies','An expectation over outcomes — not a third posterior'),small_branches,
                              label(f'0.18 × {model["observed_h"]:.3f}  +  0.82 × {model["absent_h"]:.6f}  ≈  {model["expected_h"]:.3f} bits',30).move_to([0,-1.35,0]),
                              label(f'Prior entropy ≈ {model["prior_h"]:.3f} bits  →  expected gain ≈ {model["expected_gain"]:.3f} bits',26).move_to([0,-2.1,0])))
        screens.append(VGroup(heading('Return to the observed outcome','E present is the branch actually observed'),post_chart(),
                              label(f'After E: H = {model["observed_h"]:.3f} bits',30).move_to([0,-1.75,0]),
                              label(f'Expected gain before observing: ≈ {model["expected_gain"]:.3f} bits',23,color=MUTED).move_to([0,-2.25,0])))
        screens.append(VGroup(heading('A valid update can widen the differential','Observed: E present'),post_chart(0,.3,4.4),
                              label(f'Uncertainty: {model["observed_h"]:.3f} bits',30).move_to([0,-1.65,0]),
                              label('Diagnosis remains unresolved',30).move_to([0,-2.2,0])))
        previous=VGroup()
        for cue, screen in zip(cues,screens):
            present=VGroup(screen,caption(cue.caption))
            self.play(FadeOut(previous),run_time=.4)
            self.play(FadeIn(present),run_time=.6)
            extra = 0
            if cue.beat_id == 'U04':
                selected = [m for m in mass_source.submobjects if isinstance(m, Rectangle)][1::2]
                markers = [Dot(point=[1.45,.75-i*.62,0], radius=.055, color=color)
                           for i,color in enumerate(COLORS)]
                self.play(*[TransformFromCopy(source, target) for source,target in zip(selected, markers)],
                          FadeIn(joint_rows), run_time=2)
                self.remove(joint_rows, *markers)
                screen.add(joint_rows, *markers)
                self.play(FadeIn(joint_total),run_time=.4)
                self.remove(joint_total)
                screen.add(joint_total)
                extra = 2.4
            elif cue.beat_id == 'U05':
                markers = [Dot(point=[-2.95,.75-i*.48,0], radius=.055, color=color)
                           for i,color in enumerate(COLORS)]
                targets = [Dot(point=[1.05,.75-i*.48,0], radius=.055, color=color)
                           for i,color in enumerate(COLORS)]
                self.add(*markers)
                self.play(*[TransformFromCopy(source,target) for source,target in zip(markers, targets)],
                          FadeIn(normalized_chart), run_time=2)
                self.remove(normalized_chart, *markers, *targets)
                screen.add(normalized_chart)
                self.play(FadeIn(normalized_labels),run_time=.4)
                self.remove(normalized_labels)
                screen.add(normalized_labels)
                extra = 2.4
            # Animation connects computed states; it is not another observation.
            self.wait(cue.end-cue.start-1-extra)
            previous=present
