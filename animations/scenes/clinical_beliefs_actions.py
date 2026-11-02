"""One belief, useful coordinates, and explicit consequences."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import math

from manim import (VGroup, FadeIn, FadeOut, Succession, Line, DashedLine, Dot, Arrow,
                   GrowArrow, ValueTracker, always_redraw, linear)
from core.components import label, MUTED
from core.teaching_scene import TeachingScene, lines
from core.leaf_components import (leaf_axes, result_curve, leaf_guide, utility_axes,
    utility_line, utility_mark, threshold_mark, POSITIVE, NEGATIVE)
from core.decision_math import utility_difference, thresholds, preference
from core.math import binary_update, log_odds
from core.story06_clinical import story


def notes(texts, top=1.65, spacing=.8, size=26):
    return lines(texts,x=3.4,top=top,spacing=spacing,size=size,width=5.2)


class ClinicalBeliefsActions(TeachingScene):
    def construct(self):
        data=story();self.setup_story(data,'What changes belief? What changes action?')
        examples=data['examples']
        intro=lines(['Pneumonia versus no pneumonia',
                     'Patient 1: 10% → 25%', 'Patient 2: 50% → 75%',
                     'Patient 3: 90% → 96.43%'],top=2.1,spacing=.9,size=30)
        intro.add(label('The same positive finding: LR = 3',27,MUTED).move_to([0,-2.25,0]))
        self.add(intro);self.body=intro

        self.cue(1,'Build the probability leaf')
        axes_group,axes=leaf_axes()
        legend=notes(['One hypothetical test','Sensitivity 60%','Specificity 80%',
                      'Positive: LR+ = 3','Negative: LR− = 0.5'],top=2,spacing=.8,size=25)
        legend[-2].set_color(POSITIVE);legend[-1].set_color(NEGATIVE)
        self.replace_body('leaf_axes',VGroup(axes_group,legend))
        positive,negative=result_curve(axes,3),result_curve(axes,.5)
        self.event('leaf_positive',FadeIn(positive));self.body.add(positive)
        self.event('leaf_negative',FadeIn(negative));self.body.add(negative)

        self.cue(2,'Read the result from the starting belief')
        guide=leaf_guide(axes,.1,3)
        positive_note=notes(['Patient 1','10% → 25%','Positive result','LR+ = 3'],top=1.8,spacing=.9,size=29)
        self.event('positive_read',Succession(FadeOut(legend),FadeIn(positive_note)),FadeIn(guide))
        self.body.remove(legend);self.body.add(guide,positive_note)
        self.event('negative_reset',FadeOut(guide),FadeOut(positive_note))
        self.body.remove(guide,positive_note)
        guide=leaf_guide(axes,.1,.5)
        negative_note=notes(['Patient 1','10% → 5.26%','Negative result','LR− = 1/2, not 1/3'],top=1.8,spacing=.9,size=27)
        self.event('negative_read',FadeIn(guide),FadeIn(negative_note));self.body.add(guide,negative_note)
        other=VGroup(Dot(axes.c2p(.5,.75),radius=.06,color=POSITIVE),
                     Dot(axes.c2p(.9,27/28),radius=.06,color=POSITIVE))
        other_note=label('Other positive endpoints: 75%, 96.43%',22,MUTED).move_to([3.4,-2,0])
        self.event('other_patients',FadeIn(other),FadeIn(other_note));self.body.add(other,other_note)

        self.cue(3,'Change both axes: no new evidence')
        logs,log_axes=leaf_axes(True)
        legend=notes(['X = ln[p / (1 − p)]','Y = ln[q / (1 − q)]','Both axes: natural-log units',
                      '0% and 100% map to infinity'],top=1.8,spacing=.85,size=24)
        self.replace_body('coordinate_change',VGroup(logs,legend))
        lp,lm=result_curve(log_axes,3,True),result_curve(log_axes,.5,True)
        equation=label('Y = X + ln LR',30).move_to([3.4,-1.8,0])
        self.event('log_lines',FadeIn(lp),FadeIn(lm),FadeIn(equation));self.body.add(lp,lm,equation)
        offsets=VGroup()
        for row in examples:
            x,y=row['log_positive']
            offsets.add(Arrow(log_axes.c2p(x,x),log_axes.c2p(x,y),buff=0,color=POSITIVE,tip_length=.08),
                        Dot(log_axes.c2p(x,y),radius=.055,color=POSITIVE))
        offsets.add(Arrow(log_axes.c2p(0,0),log_axes.c2p(0,-math.log(2)),buff=0,color=NEGATIVE,tip_length=.08))
        offsets_note=notes(['Positive offset: +ln 3','≈ +1.099','Negative offset: −ln 2','≈ −0.693'],top=1.8,spacing=.8,size=26)
        self.event('log_offsets',Succession(FadeOut(legend),FadeIn(offsets_note)),FadeIn(offsets))
        self.body.remove(legend);self.body.add(offsets,offsets_note)

        self.cue(4,'A distinct second finding')
        ruler=VGroup(label('New finding • LR conditional on the first result',27).move_to([0,2.2,0]),
                     label('P(E₂ | disease, E₁) = 0.8     P(E₂ | no disease, E₁) = 0.4',24,MUTED).move_to([0,1.5,0]),
                     label('Conditional LR₂ = 0.8 / 0.4 = 2',24,MUTED).move_to([0,1.0,0]),
                     Line([-4,0,0],[4,0,0],color=MUTED))
        sx=lambda z:-4+2*(z+3)
        for z in (-3,-2,-1,0,1):
            ruler.add(label(str(z),20,MUTED).move_to([sx(z),-.35,0]))
        ruler.add(label('Natural-log odds',23,MUTED).move_to([0,-.9,0]))
        z0,z1,z2=log_odds(.1),log_odds(.25),log_odds(.4)
        ruler.add(Dot([sx(z0),0,0],color=POSITIVE),label('10%',28).move_to([-3,-1.75,0]))
        self.replace_body('sequence_axes',ruler)
        arrow=Arrow([sx(z0),0,0],[sx(z1),0,0],buff=0,color=POSITIVE)
        annotation=label('+ln 3',25,POSITIVE).move_to([(sx(z0)+sx(z1))/2,.45,0])
        self.event('first_finding',GrowArrow(arrow),FadeIn(annotation));self.body.add(arrow,annotation)
        endpoint=label('→ 25%',28).move_to([-.6,-1.75,0]);self.add(endpoint);self.body.add(endpoint)
        arrow=Arrow([sx(z1),0,0],[sx(z2),0,0],buff=0,color=NEGATIVE)
        annotation=label('+ln 2',25,NEGATIVE).move_to([(sx(z1)+sx(z2))/2,.45,0])
        self.event('second_finding',GrowArrow(arrow),FadeIn(annotation));self.body.add(arrow,annotation)
        endpoint=label('→ 40%',28).move_to([1.8,-1.75,0]);self.add(endpoint);self.body.add(endpoint)
        conditional=label('Dependent findings require conditional LRs.',24,MUTED).move_to([0,-2.55,0])
        self.add(conditional);self.body.add(conditional)

        self.cue(5,'Probabilities weight consequences')
        utility_card=lines(['Act versus defer: incremental utility',
                           'Disease present: +4 units', 'Disease absent: −1 unit',
                           'G(p) = p × 4 − (1 − p) × 1'],top=1.9,spacing=1,size=31)
        self.replace_body('consequences',utility_card)
        plot,ua=utility_axes();line=utility_line(ua)
        info=notes(['B = 4, C = 1','G(p) = 5p − 1','Above zero: act','Below zero: defer'],top=1.7,spacing=.9,size=27)
        self.replace_body('utility_line',VGroup(plot,line,info))

        self.cue(6,'The action changes at a threshold')
        threshold=threshold_mark(ua)
        info2=notes(['Threshold: 20%','At 20%: indifferent','Illustrative consequences'],top=1.7,spacing=.9,size=26)
        self.event('threshold',Succession(FadeOut(info),FadeIn(info2)),FadeIn(threshold))
        self.body.remove(info);self.body.add(threshold,info2)
        p=ValueTracker(.1)
        def belief_mark():
            prob=p.get_value();gain=utility_difference(prob)
            return VGroup(utility_mark(ua,prob),
                          label(f'{prob:.1%}   G = {gain:+.2f}\n{preference(prob).capitalize()}',
                                26).move_to([3.4,-1.5,0]))
        moving=always_redraw(belief_mark);self.add(moving);self.body.add(moving)
        self.event('threshold_crossing',p.animate(rate_func=linear).set_value(.25));moving.clear_updaters(recursive=True)
        negative_mark=utility_mark(ua,1/19)
        negative_label=label('Negative: 5.26% → defer',24,NEGATIVE).move_to([3.4,-2.25,0])
        self.event('negative_decision',FadeIn(negative_mark),FadeIn(negative_label));self.body.add(negative_mark,negative_label)

        self.cue(7,'Equal evidence; unequal utility revisions')
        plot,ua=utility_axes()
        base=VGroup(plot,utility_line(ua),threshold_mark(ua),
                    label('Each positive result adds ln 3',25).move_to([3.4,2,0]))
        self.replace_body('utility_examples',base)
        for i,row in enumerate(examples):
            alpha=ValueTracker(0)
            start=row['prior'];end=row['positive']
            def current(a=alpha,p0=start):
                return utility_mark(ua,binary_update(p0,3**a.get_value()))
            mark=always_redraw(current);self.add(mark);self.body.add(mark)
            arrow=Arrow(ua.c2p(start,utility_difference(start)),ua.c2p(end,utility_difference(end)),buff=0,color=POSITIVE,tip_length=.12)
            self.event(f'patient_{i+1}',alpha.animate(rate_func=linear).set_value(1),GrowArrow(arrow))
            mark.clear_updaters(recursive=True);self.body.add(arrow)
            text=label(f"Patient {i+1}: ΔG {row['utility_change']:+.2f}",27,max_width=5).move_to([3.4,1-i*.8,0])
            self.add(text);self.body.add(text)
        note=label('Revised estimates, not causal health gains',23,MUTED).move_to([3.4,-2,0])
        self.add(note);self.body.add(note)

        self.cue(8,'Hold belief fixed. Change the consequences.')
        plot,ua=utility_axes();cost=ValueTracker(1)
        fixed=DashedLine(ua.c2p(.25,-4),ua.c2p(.25,4),color=MUTED,dash_length=.06)
        def changing_cost():
            c=cost.get_value();threshold=thresholds(4,c)['probability'];gain=utility_difference(.25,4,c)
            labels=notes(['Probability stays 25%',f'Benefit 4; cost {c:.2f}',
                          f'Threshold: {threshold:.1%}',f'G(25%) = {gain:+.2f}',
                          preference(.25,4,c).capitalize()],top=1.9,spacing=.8,size=26)
            return VGroup(utility_line(ua,c),threshold_mark(ua,c),utility_mark(ua,.25,c),labels)
        dynamic=always_redraw(changing_cost)
        self.replace_body('fixed_belief',VGroup(plot,fixed,dynamic))
        self.event('changed_cost',cost.animate(rate_func=linear).set_value(4));dynamic.clear_updaters(recursive=True)

        self.cue(9,'The same decision in different coordinates')
        px=lambda probability:-4+8*probability
        reset=VGroup(label('Reset: B = 4, C = 1',29).move_to([0,2.25,0]),
                     Line([-4,.8,0],[4,.8,0],color=MUTED))
        for probability in (0,.2,.5,1):
            reset.add(label(f'{probability:.0%}',20,MUTED).move_to([px(probability),.45,0]))
        reset.add(DashedLine([px(.2),0,0],[px(.2),1.4,0],color=NEGATIVE),
                  Dot([px(.25),.8,0],color=POSITIVE),
                  label('Threshold 20%',24,NEGATIVE).move_to([px(.2)-.7,-.5,0]),
                  label('Posterior 25%',24,POSITIVE).move_to([px(.25)+1.2,1.6,0]),
                  label('25% > 20%: preferred action is act',29).move_to([0,-1.4,0]),
                  label('Probability available at the decision',24,MUTED).move_to([0,-2.2,0]))
        self.replace_body('reset_consequences',reset)
        ruler=VGroup(label('Natural-log odds: same posterior, same threshold',26,MUTED).move_to([0,2.25,0]),
                     Line([-4,.8,0],[4,.8,0],color=MUTED))
        for z in (-3,-2,-1,0,1):
            ruler.add(label(str(z),20,MUTED).move_to([sx(z),.45,0]))
        xt,xp=sx(-math.log(4)),sx(-math.log(3))
        ruler.add(DashedLine([xt,0,0],[xt,1.4,0],color=NEGATIVE),Dot([xp,.8,0],color=POSITIVE),
                  label('Threshold −ln 4',24,NEGATIVE).move_to([xt-1.2,-.5,0]),
                  label('Posterior −ln 3',24,POSITIVE).move_to([xp+1.6,1.6,0]),
                  label('p > 20%   ⇔   odds > 1:4   ⇔   log odds > −ln 4',29).move_to([0,-1.4,0]),
                  label('Preferred action remains act',28).move_to([0,-2.2,0]))
        self.replace_body('decision_coordinates',ruler)

        self.cue(10,'Two useful representations')
        recap=lines(['Evidence: log odds add ln LR',
                     'Consequences: probabilities weight utilities',
                     'Transform consistently: the decision is unchanged.'],top=1.45,spacing=1.3,size=32)
        self.replace_body('recap',recap)
        self.at(self.cues[-1].start)
        self.finish()
