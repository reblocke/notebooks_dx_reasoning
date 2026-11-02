"""What does this result mean? Denominators before algebra."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (VGroup, FadeIn, FadeOut, RoundedRectangle, Line, Circle, Dot,
                   Arrow, ValueTracker, always_redraw, linear)
from core.components import label, MUTED, fade_replace
from core.teaching_scene import TeachingScene, lines
from core.cohort_components import cohort_panel, people, selected_destinations, DISEASE, NO_DISEASE
from core.math import binary_update
from core.story05_clinical import story


class ClinicalTestResults(TeachingScene):
    def construct(self):
        data=story(); self.setup_story(data,'What does this test result mean?')
        intro=lines(['POSITIVE RESULT', '“99% specific”', 'Probability of the condition now?',
                     'Starting assumption: 10% pretest probability'],top=1.6,spacing=.9,size=32)
        intro[0].set_color(DISEASE)
        self.add(intro);self.body=intro

        self.cue(1,'Change the denominator')
        population=cohort_panel('B',.02,.99)
        self.replace_body('population',population)
        affected=people(2,DISEASE,(-3,-.35));unaffected=people(9,NO_DISEASE,(3,-.35))
        counts=VGroup(label('2 positive',25,DISEASE).move_to([-3,-.95,0]),
                      label('9 positive',25,NO_DISEASE).move_to([3,-.95,0]))
        self.event('positive_marks',FadeIn(affected),FadeIn(unaffected),FadeIn(counts))
        self.body.add(affected,unaffected,counts)
        frame=RoundedRectangle(width=5.7,height=1.3,corner_radius=.12,color=DISEASE).move_to([0,-.75,0])
        tag=label('POSITIVE RESULTS  •  one mark = one person',22,DISEASE).move_to([0,-1.6,0])
        all_people=list(affected)+list(unaffected)
        self.event('positive_regroup',FadeOut(counts),FadeIn(frame),FadeIn(tag),
                   *[m.animate.move_to(pos) for m,pos in zip(all_people,selected_destinations(11))])
        self.body.remove(counts);self.body.add(frame,tag)
        posterior=label('2 / (2 + 9) = 2/11 ≈ 18.2%',32).move_to([0,-2.12,0])
        self.event('positive_posterior',FadeIn(posterior));self.body.add(posterior)

        self.cue(2,'Compare rates, then update odds')
        rates=lines(['SPIN?  High specificity + positive ⇒ rule in?',
                     'LR+ = (2/100) / (9/900) = 2',
                     'Positive-result rates: 2% / 1% = 2'],top=2.15,spacing=.85,size=31)
        rates[0].set_color(MUTED);rates[0].scale(.8)
        self.replace_body('positive_lr',rates)
        odds=lines(['Pretest odds 1:9  ×  2  =  post-test odds 2:9',
                    'Probability: 10% → 18.2%',
                    '2/9 is posterior odds.  The likelihood ratio is 2.'],top=-.7,spacing=.73,size=29)
        odds[-1].set_color(MUTED);odds[-1].scale(.83)
        self.event('positive_odds',FadeIn(odds));self.body.add(odds)

        self.cue(3,'Reset: a different test, a negative result')
        population=cohort_panel('A',.99,.02)
        population_footer = population[-1]
        self.replace_body('reset_population',population)
        affected=people(1,DISEASE,(-3,-.35));unaffected=people(18,NO_DISEASE,(3,-.35))
        counts=VGroup(label('1 negative',25,DISEASE).move_to([-3,-1.18,0]),
                      label('18 negative',25,NO_DISEASE).move_to([3,-1.18,0]))
        self.event('negative_marks',FadeIn(affected),FadeIn(unaffected),FadeIn(counts))
        self.body.add(affected,unaffected,counts)
        frame=RoundedRectangle(width=5.7,height=1.1,corner_radius=.12,color=DISEASE).move_to([0,-.62,0])
        tag=label('NEGATIVE RESULTS  •  19 people',23,DISEASE).move_to([0,-1.42,0])
        self.event('negative_regroup',FadeOut(counts),FadeIn(frame),FadeIn(tag),
                   *[m.animate.move_to(pos) for m,pos in zip(list(affected)+list(unaffected),selected_destinations(19))])
        self.body.remove(counts);self.body.add(frame,tag)
        formula=label('LR− = (1/100) / (18/900) = 0.5',28).move_to([0,-1.92,0])
        self.event('negative_lr',FadeIn(formula));self.body.add(formula)
        answer=label('Odds 1:9 → 1:18     Disease probability 1/19 ≈ 5.3%',25).move_to([0,-2.38,0])
        # Replace the original footnote so the negative-result denominators stay legible.
        self.event('negative_posterior',FadeOut(population_footer),FadeIn(answer),
                   fade_replace(population[0],label('SNOUT? High sensitivity + negative ⇒ rule out?',23,max_width=11).move_to([0,2.35,0])))
        self.body.add(answer)

        self.cue(4,'Both test characteristics determine the LR')
        self.replace_body('general_positive',lines([
            'Positive result', 'LR+ = sensitivity / (1 − specificity)',
            'Compare P(+ | condition) with P(+ | no condition)'],top=1.5,spacing=1,size=32))
        self.replace_body('general_negative',lines([
            'Negative result', 'LR− = (1 − sensitivity) / specificity',
            'Compare P(− | condition) with P(− | no condition)'],top=1.5,spacing=1,size=32))
        self.replace_body('general_update',lines([
            'Pretest odds × likelihood ratio = post-test odds',
            'Probability = odds / (1 + odds)',
            'Sensitivity and specificity describe results given disease status.'],top=1.2,spacing=1.15,size=31))

        self.cue(5,'The starting probability matters')
        rulers=VGroup(label('Test C: sensitivity 80%, specificity 92%  •  LR+ = 10',26,MUTED).move_to([0,2.25,0]))
        examples=data['profiles']['C']['examples']
        for i,row in enumerate(examples):
            y=.8-i*1.6
            rulers.add(label(f"Start {row['prior']:.0%}",23,MUTED).move_to([-5.4,y,0]),
                       Line([-4,y,0],[4,y,0],color=MUTED),
                       Circle(radius=.07,color=DISEASE,stroke_width=2).move_to([-4+8*row['prior'],y,0]))
            for p in (0,.25,.5,.75,1):
                x=-4+8*p
                rulers.add(Line([x,y-.06,0],[x,y+.06,0],color=MUTED),
                           label(f'{p:.0%}',18,MUTED).move_to([x,y-.3,0]))
        self.replace_body('strong_starts',rulers)
        progress=ValueTracker(0)
        def moving():
            group=VGroup()
            for i,row in enumerate(examples):
                y=.8-i*1.6;p=row['prior'];q=binary_update(p,10**progress.get_value())
                group.add(Dot([-4+8*q,y,0],radius=.07,color=DISEASE),
                          label(f'{q:.1%}',27,DISEASE).move_to([5.2,y,0]))
                if q>p+1e-8:
                    group.add(Arrow([-4+8*p,y,0],[-4+8*q,y,0],buff=0,color=DISEASE,tip_length=.12))
            return group
        dynamic=always_redraw(moving);self.add(dynamic);self.body.add(dynamic)
        self.event('strong_update',progress.animate(rate_func=linear).set_value(1))
        dynamic.clear_updaters(recursive=True)
        summary=label('Same ×10 odds multiplier  •  different post-test probabilities',26).move_to([0,-2.3,0])
        self.event('strong_endpoints',FadeIn(summary));self.body.add(summary)

        self.cue(6,'Three questions to carry forward')
        recap=lines(['1   Ask the post-result question', '2   Compare both result rates',
                     '3   Update the pretest odds'],top=1.4,spacing=1.1,size=34)
        recap.add(label('Both test characteristics matter. The starting probability matters.',24,MUTED).move_to([0,-2.25,0]))
        self.replace_body('recap',recap)
        self.event('final_hold',fade_replace(self.caption,self.caption_label(self.cues[-1].caption)))
        self.finish()
