"""Four synthetic Bayes trajectories and three windows on one path."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from manim import (Scene,Group,VGroup,Dot,Line,Rectangle,ValueTracker,FadeIn,FadeOut,
                   always_redraw,linear)
from core.components import BG,WHITE,MUTED,label
from core.atlas_components import triangle,trace_axes,path,trace,bars,legend
from core.atlas_geometry import position,trace_position
from core.math import bridge,entropy
from core.story04 import story


class DiagnosticTrajectoryAtlas(Scene):
    def construct(self):
        self.camera.background_color=BG
        model=story(); cases=model['cases']; cues=model['cues']
        self.add(label('SYNTHETIC MODELS  •  fixed diagnoses A, B, C',21,MUTED).move_to([0,3.68,0]))
        def title(text,sub=''):
            return VGroup(label(text,37,max_width=12).move_to([0,3.15,0]),label(sub,20,MUTED,max_width=12).move_to([0,2.66,0]))
        def caption(cue):return label(cue.caption,25,max_width=12).move_to([0,-3.27,0])
        def present(screen,cue):
            return Group(screen,caption(cue))
        def switch(old,new):
            self.play(FadeOut(old),run_time=.4);self.play(FadeIn(new),run_time=.6)
        def board(p,title_text,sub='',show_trace=True):
            g=Group(title(title_text,sub),triangle(),legend(),bars(p))
            if show_trace:g.add(trace_axes())
            return g
        def mini(case_id,center,title_text):
            cx,cy=center; s=1.65; bottom=cy-.76; left=cx+.12
            states=cases[case_id]['states']; tri_center=(cx-1.35,bottom)
            return Group(label(title_text,21,max_width=5.8).move_to([cx,cy+.95,0]),
                         triangle(s,tri_center,False),path(states,tri_center,s,small=True),
                         trace_axes(left,bottom,2.3,1.2,True),trace(states,left,bottom,2.3,1.2,small=True))
        def comparison():
            return Group(title('Four possible realized paths','Same triangle orientation and fixed entropy scale  •  each vignette has its own prior'),
                         mini('convergence',(-3.3,1.05),'Convergence'),mini('reopening',(3.2,1.05),'Reopening'),
                         mini('substitution',(-3.3,-1.35),'Substitution'),mini('persistent_ambiguity',(3.2,-1.35),'Persistent ambiguity'),
                         label('Entropy trace: 0–1.65 bits  •  finding index: 0–4',17,MUTED).move_to([0,-2.67,0]))
        # 0–15: deliberately separate synthetic examples.
        cue=cues[0]
        intro=Group(title('An atlas of diagnostic trajectories','Three examples  •  not a comparison of methods'),
                    label('Concentrated differential',25).move_to([-4,1.25,0]),
                    label('Open differential',25).move_to([0,1.25,0]),
                    label('Changed leading diagnosis',25).move_to([4,1.25,0]),
                    label('A 80%  B 10%  C 10%',20,MUTED).move_to([-4,.55,0]),
                    label('A 33%  B 33%  C 33%',20,MUTED).move_to([0,.55,0]),
                    label('A 80% → B 80%',20,MUTED).move_to([4,.55,0]),
                    label('Illustrative paths, not estimates of clinical frequency',23,MUTED).move_to([0,-1.1,0]))
        prev=Group(); cur=present(intro,cue);switch(prev,cur);self.wait(14);prev=cur
        # A02: geometry explanation; these illustrative changes are not findings.
        cue=cues[1]; tracker=ValueTracker(0)
        examples=[np.array([1/3]*3),np.array([.8,.1,.1]),np.array([.1,.8,.1])]
        def example_p():
            t=tracker.get_value();i=min(int(t),1);return examples[i]*(1-(t-i))+examples[i+1]*(t-i)
        screen=Group(title('One point, one distribution','Illustrative positions; no findings are observed here'),triangle(),legend(),
                     always_redraw(lambda:bars(example_p())),always_redraw(lambda:Dot(position(example_p()),radius=.11,color=WHITE)))
        cur=present(screen,cue);switch(prev,cur);self.wait(5);self.play(tracker.animate.set_value(1),run_time=3,rate_func=linear);self.wait(5);self.play(tracker.animate.set_value(2),run_time=3,rate_func=linear);self.wait(13);prev=cur
        # A03: explain discrete state marker and trace before any vignette.
        cue=cues[2];p=examples[0]
        screen=board(p,'Entropy and recorded findings','Heat map uses one fixed 0 to log₂(3) bits scale')
        screen.add(Dot(position(p),radius=.09,color=WHITE),Dot(trace_position(0,entropy(p)),radius=.06,color=WHITE),
                   label('0: prior   •   1–4: after findings',19,MUTED).move_to([3.45,-2.45,0]),
                   label('Motion illustrates transitions',19,MUTED).move_to([3.45,-2.72,0]))
        cur=present(screen,cue);switch(prev,cur);self.wait(19);prev=cur
        titles=['Convergence','Reopening','Substitution','Persistent ambiguity']
        names=['convergence','reopening','substitution','persistent_ambiguity']
        for cue,name,heading in zip(cues[3:7],names,titles):
            states=cases[name]['states']; ls=cases[name]['likelihoods']
            fixed=Group(title(heading,'New independent synthetic vignette  •  reset to its own prior'),triangle(),legend(),trace_axes())
            current=ValueTracker(0); index=[0]
            def live():return bridge(states[index[0]],ls[index[0]],current.get_value())
            moving=Group(always_redraw(lambda:bars(live())),always_redraw(lambda:Dot(position(live()),radius=.10,color=WHITE)))
            offsets = ([[-.65,.45,0],[-.72,-.15,0],[.55,.48,0],[.72,-.10,0],[0,-.6,0]] if name == 'persistent_ambiguity' else [[.12,.12,0]]*5)
            history=VGroup(Dot(position(states[0]),radius=.06,color=WHITE),Dot(trace_position(0,entropy(states[0])),radius=.055,color=WHITE),label('0',15).move_to(position(states[0])+offsets[0]))
            if name == 'persistent_ambiguity':
                history.add(Line(position(states[0]),position(states[0])+offsets[0],color=MUTED,stroke_width=1))
            fixed.add(history,moving)
            cur=present(fixed,cue);switch(prev,cur)
            for i in range(4):
                index[0]=i;current.set_value(0)
                event=label(f'Observed finding E{i+1}',21,WHITE).move_to([3.55,2.12,0]);self.play(FadeIn(event),run_time=.6)
                self.play(current.animate.set_value(1),run_time=3,rate_func=linear)
                a,b=states[i],states[i+1]
                history.add(Line(position(a),position(b),color=WHITE,stroke_width=2),Dot(position(b),radius=.06,color=WHITE),label(str(i+1),15).move_to(position(b)+offsets[i+1]),
                            Line(trace_position(i,entropy(a)),trace_position(i+1,entropy(b)),color=WHITE,stroke_width=2),Dot(trace_position(i+1,entropy(b)),radius=.055,color=WHITE))
                if name == 'persistent_ambiguity':
                    history.add(Line(position(b),position(b)+offsets[i+1],color=MUTED,stroke_width=1))
                self.add(history);self.wait(.6);self.play(FadeOut(event),run_time=.4)
            if name=='substitution':
                equality=label(f'Initial H = {entropy(states[0]):.3f}  •  final H = {entropy(states[-1]):.3f} bits',20).move_to([3.5,2.1,0])
                fixed.add(equality); self.play(FadeIn(equality),run_time=.6); self.wait(15)
            else:
                self.wait(15.6)
            moving.clear_updaters(recursive=True);prev=cur
        cue=cues[7];cur=present(comparison(),cue);switch(prev,cur);self.wait(29);prev=cur
        # Three windows preserve the identical path and original indices.
        cue=cues[8];states=cases['substitution']['states']
        def window(first,last,subtitle):
            g=Group(title('One path, different encounter windows',subtitle),triangle(),legend(),trace_axes(),
                    path(states,first=first,last=last),trace(states,first=first,last=last),bars(states[last]))
            left=1.4+4.2*first/4;right=1.4+4.2*last/4
            g.add(Rectangle(width=right-left,height=1.5,stroke_color='#E69F00',stroke_width=2,fill_opacity=0).move_to([(left+right)/2,-1.,0]))
            return g
        windows=[window(0,2,'States 0–2  •  observed findings E1 and E2'),
                 window(2,4,'States 2–4  •  starting beliefs already include E1 and E2  •  visible E3 and E4'),
                 window(0,4,'States 0–4  •  complete substitution path')]
        cur=present(windows[0],cue);switch(prev,cur);self.wait(10)
        nxt=present(windows[1],cue);switch(cur,nxt);cur=nxt;self.wait(10)
        nxt=present(windows[2],cue);switch(cur,nxt);cur=nxt;self.wait(12);prev=cur
        cue=cues[9];cur=present(comparison(),cue);switch(prev,cur);self.wait(14)
