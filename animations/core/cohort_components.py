"""Count boxes are aggregates; every selected marker represents one person."""
from manim import VGroup, Circle, Line, RoundedRectangle
from .components import label, MUTED

DISEASE = '#56B4E9'
NO_DISEASE = '#C6CFDA'


def person(color):
    return VGroup(Circle(radius=.065, color=color, fill_opacity=1, stroke_width=0).shift([0,.09,0]),
                  Line([0,.01,0],[0,-.12,0],color=color,stroke_width=4),
                  Line([-.075,-.04,0],[.075,-.04,0],color=color,stroke_width=3))


def people(count, color, center, columns=10):
    marks = VGroup()
    for i in range(count):
        cols = min(count, columns)
        marks.add(person(color).move_to([center[0]+(i%columns-(cols-1)/2)*.38,
                                        center[1]-(i//columns)*.38,0]))
    return marks


def cohort_panel(test, se, sp):
    group = VGroup(label(f'Different test: {test}' if test=='A' else f'Test {test}',30).move_to([0,2.35,0]),
                   label(f'Sensitivity {se:.0%}     Specificity {sp:.0%}',27,MUTED).move_to([0,1.82,0]))
    for x,title,count,color in [(-3,'Condition present',100,DISEASE),(3,'Condition absent',900,NO_DISEASE)]:
        box=RoundedRectangle(width=4.5,height=1.15,corner_radius=.12,color=color,stroke_width=2).move_to([x,.78,0])
        group.add(box,label(title,27,color).move_to([x,1.02,0]),label(f'{count} people',30,color).move_to([x,.55,0]))
    group.add(label('Aggregate count boxes  •  1,000 people  •  pretest probability 10%',22,MUTED).move_to([0,-2.55,0]))
    return group


def selected_destinations(total):
    return [((i%10-(min(total,10)-1)/2)*.4, -.55-(i//10)*.4, 0) for i in range(total)]
