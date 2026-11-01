"""Entropy as fixed-scale probability-by-surprisal areas."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from manim import (Scene,VGroup,Line,Circumscribe,Rectangle,Text,DecimalNumber,ValueTracker,FadeIn,FadeOut,
                   always_redraw,linear)
from core.components import BG,WHITE,MUTED,COLORS,label
from core.entropy_components import axes,rectangles,entropy_meter,probability_strip,rare_a_leader
from core.math import entropy,bridge
from core.entropy_geometry import rectangle_geometry
from core.story03 import story
import numpy as np


class EntropyAsArea(Scene):
    def construct(self):
        self.camera.background_color=BG
        model=story();states=model['states'];cues=model['cues']
        self.add(label('SYNTHETIC MODEL  •  fixed diagnoses A, B, C',22,color=MUTED).move_to([0,3.68,0]))

        def heading(title,subtitle):
            return VGroup(label(title,40,max_width=12).move_to([0,3.15,0]),
                          label(subtitle,23,color=MUTED,max_width=11.8).move_to([0,2.67,0]))

        def caption(text): return label(text,28,max_width=12).move_to([0,-3.25,0])

        def panel(lines):
            return VGroup(*[label(text,26,color=color,max_width=4.4).move_to([3.85,1.45-i*.55,0])
                            for i,(text,color) in enumerate(lines)])

        def state_frame(title,subtitle,p,lines,*,categories=(0,1,2),meter=True):
            result=VGroup(heading(title,subtitle),axes(),rectangles(p,categories),panel(lines))
            if meter:result.add(entropy_meter(entropy(p)))
            return result

        def probability_cards(p):
            r=rectangle_geometry(p,plot_width=6.8,plot_height=3.9,max_surprisal=7.2)
            return [(f'{name}  p={100*x.p:.1f}%  s={x.surprisal:.3f} bits',COLORS[i])
                    for i,(name,x) in enumerate(zip('ABC',r))]

        def dynamic_panel(p_function, before_h=None):
            entropy_title = f'H {before_h:.3f} →' if before_h is not None else 'Total entropy'
            g=VGroup(); specs=[('A probability',lambda p:100*p[0],1,'%'),
                              ('A surprisal',lambda p:-np.log2(p[0]),3,'bits'),
                              ('A contribution',lambda p:-p[0]*np.log2(p[0]),3,'bits'),
                              (entropy_title,entropy,3,'bits')]
            for i,(title,fn,digits,unit) in enumerate(specs):
                y=1.42-i*.53
                g.add(label(title,23,color=MUTED,max_width=2.6).move_to([2.95,y,0]))
                value=DecimalNumber(fn(p_function()),mob_class=Text,num_decimal_places=digits,font_size=26,color=WHITE)
                value.move_to([4.82,y,0]);value.add_updater(lambda m,fn=fn: m.set_value(fn(p_function())))
                g.add(value,label(unit,20,color=MUTED).move_to([5.72,y,0]))
            g.add(label('A  /  B  /  C probability strip',21,color=MUTED).move_to([3.75,-1.04,0]))
            return g

        r0,r1,r2,uniform,concentrated=[states[key]['p'] for key in ('R0','R1','R2','U','C')]
        strip0=probability_strip(r0,left=-4.5,y=.3,width=9)
        screens=[]
        strip_bracket=VGroup(Line([-4.5,-.05,0],[4.5,-.05,0],color=WHITE,stroke_width=2),
                             Line([-4.5,-.12,0],[-4.5,.02,0],color=WHITE,stroke_width=2),
                             Line([4.5,-.12,0],[4.5,.02,0],color=WHITE,stroke_width=2),
                             label('100% of the distribution',25,color=MUTED).move_to([0,-.42,0]))
        screens.append(VGroup(heading('Divide belief among possibilities','Three exclusive categories; total probability = 100%'),strip0,
                              label('A 50%       B 25%       C 25%',32).move_to([0,1,0]),strip_bracket))
        screens.append(state_frame('A rectangle for diagnosis A','Width = probability; height = surprisal if A is revealed',r0,
                      [('A probability = 0.50',COLORS[0]),('A surprisal = 1.000 bit',WHITE),('Width × height = 0.500 bit',WHITE),('B and C remain possible.',MUTED)],categories=(0,),meter=False))
        a_filled=screens[1][2]
        screens[1].remove(a_filled)
        a_outline=a_filled.copy().set_fill(opacity=0)
        screens.append(state_frame('Less likely can be more surprising','Left to right: A, B, C  •  fixed probability and surprisal scales',r0,
                      probability_cards(r0)+[('sᵢ = −log₂(pᵢ)',WHITE)],meter=False))
        screens.append(state_frame('Multiply probability by surprisal','Each rectangle’s area is one entropy contribution',r0,
                      [('A: 0.50 × 1 = 0.50 bit',COLORS[0]),('B: 0.25 × 2 = 0.50 bit',COLORS[1]),('C: 0.25 × 2 = 0.50 bit',COLORS[2])],meter=False))
        screens.append(state_frame('Add the three areas','The total is expected surprisal across the distribution',r0,
                      [('0.50 + 0.50 + 0.50',WHITE),('H = 1.500 bits',WHITE),('H = −Σ pᵢ log₂(pᵢ)',WHITE)]))
        # E06 and E09 are populated with tracker-driven objects inside the loop.
        screens.append(VGroup(heading('A separate hypothetical sweep','A: 10% → 1%; B = C = (1 − A)/2  •  not new evidence'),axes()))
        r2data=rectangle_geometry(r2,plot_width=6.8,plot_height=3.6,max_surprisal=7.2)[0]
        screens.append(state_frame('Rare can be surprising, yet contribute little','Selected A values only  •  fixed axes',r2,
                      [('A: 50%  |  s=1.000  |  area=.500',COLORS[0]),('A: 10%  |  s=3.322  |  area=.332',COLORS[0]),
                       (f'A: 1%  |  s={r2data.surprisal:.3f}  |  area={r2data.contribution:.3f}',COLORS[0]),
                       ('The 1% rectangle is not widened.',MUTED)]))
        screens[-1].add(rare_a_leader(r2))
        screens.append(state_frame('Uniform probabilities maximize entropy','Uniform example  •  same fixed scales',uniform,
                      probability_cards(uniform)+[('Maximum for 3: log₂(3) bits',WHITE)]))
        screens.append(VGroup(heading('An observed finding changes the areas','Prior (90%, 5%, 5%); P(E | A,B,C) = (0.10, 0.90, 0.90)'),axes()))
        screens.append(state_frame('Entropy is probability-weighted surprise','Fixed A, B, C  •  the entire normalized distribution matters',r0,
                      [('A contribution = 0.500 bit',COLORS[0]),('B contribution = 0.500 bit',COLORS[1]),
                       ('C contribution = 0.500 bit',COLORS[2]),('H = −Σ pᵢ log₂(pᵢ)',WHITE)]))
        previous=VGroup()
        for cue,screen in zip(cues,screens):
            tracker=None; animated=[]
            if cue.beat_id in ('E06','E09'):
                tracker=ValueTracker(0)
                if cue.beat_id=='E06':
                    def values():
                        a=.1-.09*tracker.get_value()
                        return np.array([a,(1-a)/2,(1-a)/2])
                else:
                    def values(): return bridge(model['prior'],model['likelihood'],tracker.get_value())
                blocks=always_redraw(lambda:rectangles(values()))
                strip=always_redraw(lambda:probability_strip(values()))
                meter=always_redraw(lambda:entropy_meter(entropy(values())))
                details=dynamic_panel(values, entropy(model['prior']) if cue.beat_id=='E09' else None)
                screen.add(blocks,strip,meter,details)
                animated=[blocks,strip,meter,details]
                if cue.beat_id=='E06':
                    leader=always_redraw(lambda:rare_a_leader(values()))
                    screen.add(leader);animated.append(leader)
            present=VGroup(screen,caption(cue.caption))
            self.play(FadeOut(previous),run_time=.4)
            self.play(FadeIn(present),run_time=.6)
            if cue.beat_id=='E02':
                self.play(FadeIn(a_outline),run_time=1)
                self.play(FadeIn(a_filled),run_time=1)
                self.remove(a_outline,a_filled);screen.add(a_outline,a_filled)
                self.wait(cue.end-cue.start-3)
            elif cue.beat_id=='E04':
                for rectangle in screen[2]:
                    self.play(Circumscribe(rectangle,buff=.03,color=WHITE,stroke_width=2),run_time=.8)
                self.wait(cue.end-cue.start-3.4)
            elif cue.beat_id=='E06':
                self.wait(4)
                self.play(tracker.animate.set_value(1),run_time=10,rate_func=linear)
                for item in animated:item.clear_updaters(recursive=True)
                self.wait(cue.end-cue.start-15)
            elif cue.beat_id=='E08':
                self.wait(6)
                other=state_frame('A concentrated prior','A new example; not an additional observation',concentrated,
                      probability_cards(concentrated)+[('H is lower than for uniform.',WHITE)])
                replacement=VGroup(other,caption(cue.caption))
                self.play(FadeOut(present),run_time=.4)
                self.play(FadeIn(replacement),run_time=.6)
                present=replacement
                self.wait(cue.end-cue.start-8)
            elif cue.beat_id=='E09':
                self.wait(2)
                self.play(tracker.animate.set_value(1),run_time=8,rate_func=linear)
                for item in animated:item.clear_updaters(recursive=True)
                self.wait(cue.end-cue.start-11)
            else:self.wait(cue.end-cue.start-1)
            previous=present
