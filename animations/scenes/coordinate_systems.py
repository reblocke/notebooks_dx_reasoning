"""One LR update displayed on three fixed, shared coordinate systems."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from manim import (Scene, VGroup, ValueTracker, Square, FadeIn, FadeOut, always_redraw,
                   linear)
from core.components import BG, MUTED, label, card
from core.rulers import ruler_rows, dynamic_marks, screen_x, BLUE
from math import pi
from core.story02 import story


class OneEvidenceThreeCoordinates(Scene):
    def construct(self):
        self.camera.background_color=BG
        model=story();examples=model['examples'];cues=model['cues']
        self.add(label('SYNTHETIC EXAMPLES  •  three independent binary beliefs',22,color=MUTED).move_to([0,3.68,0]))

        def heading(title,subtitle):
            return VGroup(label(title,41,max_width=12).move_to([0,3.15,0]),
                          label(subtitle,25,color=MUTED,max_width=12).move_to([0,2.55,0]))

        def caption(text): return label(text,29,max_width=12.2).move_to([0,-3.25,0])

        def key(): return label('Open circle: before     Filled diamond: after',21,color=MUTED).move_to([0,2.05,0])

        def values(kind, inverse=False):
            rows=[]
            for i,e in enumerate(examples):
                if kind=='probability':
                    delta=100*(e['posterior']-e['prior'])
                    after = 100*e['posterior']
                    after_text = f'{after:.0f}' if abs(after-round(after)) < 1e-10 else f'{after:.2f}'
                    delta_text = f'{delta:.0f}' if abs(delta-round(delta)) < 1e-10 else f'{delta:.2f}'
                    text=f"{100*e['prior']:.0f}→{after_text}%  +{delta_text} pp"
                elif kind=='odds':
                    text=['1/9 → 1/3  (×3)','1 → 3  (×3)','9 → 27  (×3)'][i]
                else:
                    text=f"{e['log_before']:+.3f} → {e['log_after']:+.3f}"
                    if inverse: text=f"{e['log_after']:+.3f} → {e['log_before']:+.3f}"
                    else: text += "\n+ln(3) ≈ +1.099"
                rows.append(label(text,22,max_width=2.65).move_to([5.05,1.38-i*1.22,0]))
            return VGroup(*rows)

        def frame(title,sub,kind,after=False,foot=''):
            objects=[heading(title,sub),key(),ruler_rows(examples,kind,show_after=after)]
            if after: objects.append(values(kind))
            if foot: objects.append(label(foot,23,color=MUTED,max_width=12).move_to([0,-2.32,0]))
            return VGroup(*objects)

        screens=[
            VGroup(heading('One finding, three coordinate systems','Three examples; the same finding has LR = 3'),
                   card('Separate binary starts','10%     |     50%     |     90%',width=8).move_to([0,.5,0]),
                   label('Each row represents a different starting belief.',29,color=MUTED).move_to([0,-1.2,0])),
            frame('Start with probabilities','Fixed probability domain: 0% to 100%','probability',foot='p′ = p × LR / (1 − p + p × LR)'),
            frame('One update, unequal probability changes','LR = 3  •  Each row remains a separate binary example','probability',foot='Transitions connect computed states; no additional evidence.'),
            frame('Express the same beliefs as odds','Changing coordinates adds no evidence  •  odds = p / (1 − p)','odds',after=True,foot='One shared linear-odds ruler, from 0 to 30.'),
            frame('The same update multiplies odds','Replay of the original update  •  not a second finding','odds',foot='The small 1/9 → 1/3 movement remains small on this common scale.'),
            frame('Change to natural-log odds','Changing coordinates  •  natural logarithm, base e','log_odds',after=True,foot='ln(odds × 3) = ln(odds) + ln(3)'),
            frame('Log-odds movements are equal','Same original update  •  common domain −3.5 to 3.5','log_odds',foot='Each shift = +ln(3) ≈ +1.099'),
            frame('Apply the inverse mathematical update','LR = 1/3  •  not a claim about a negative test result','log_odds',foot='Subtract ln(3) to recover the original beliefs.'),
            frame('One update, three descriptions','Forward LR = 3: recap, not another observation','log_odds',after=True,
                  foot='Probability changes differ  •  odds ×3  •  log odds +ln(3)'),
        ]
        # The inverse begins at the previously updated values. Keep those fixed
        # as outlined diamonds while the filled diamond returns to the original.
        screens[7].remove(screens[7][1])
        screens[7].add(label('Open circle: original  •  Outline diamond: inverse start  •  Filled: current',
                             20,color=MUTED,max_width=12).move_to([0,2.05,0]))
        for i,e in enumerate(examples):
            screens[7].add(Square(side_length=.20,color=BLUE,fill_opacity=0,stroke_width=2)
                           .rotate(pi/4).move_to([screen_x(e['posterior'],'log_odds'),1.38-i*1.22,0]))
        screens[7].add(label('Probability: 25→10%, 75→50%, 96.43→90%   |   Odds: 1/3→1/9, 3→1, 27→9',
                             20,color=MUTED,max_width=12).move_to([0,-2.65,0]))
        previous=VGroup()
        for cue,screen in zip(cues,screens):
            present=VGroup(screen,caption(cue.caption))
            self.play(FadeOut(previous),run_time=.4)
            self.play(FadeIn(present),run_time=.6)
            extra=0
            kind={'C03':'probability','C05':'odds','C07':'log_odds','C08':'log_odds'}.get(cue.beat_id)
            if kind:
                inverse=cue.beat_id=='C08'
                alpha=ValueTracker(1 if inverse else 0)
                moving=always_redraw(lambda: dynamic_marks(examples,kind,alpha.get_value(),inverse=inverse))
                self.add(moving)
                self.play(alpha.animate.set_value(0 if inverse else 1),run_time=5,rate_func=linear)
                moving.clear_updaters(recursive=True)
                self.remove(moving);screen.add(moving)
                endpoint_text=values(kind,inverse=inverse)
                self.play(FadeIn(endpoint_text),run_time=.4)
                self.remove(endpoint_text);screen.add(endpoint_text)
                extra=5.4
            self.wait(cue.end-cue.start-1-extra)
            previous=present
