"""Fixed-width rulers for the three independent binary examples."""
import math
import numpy as np
from manim import VGroup, Line, Arrow, Circle, Square, LEFT
from .components import label, MUTED, WHITE
from .math import axis_coordinate, binary_update, probability_odds, log_odds

BLUE='#56B4E9'
WIDTH=7.0
LEFT_EDGE=-3.5
DOMAINS={'probability': (0,1), 'odds': (0,30), 'log_odds': (-3.5,3.5)}
TICKS={'probability': [0,.25,.5,.75,1], 'odds': [0,5,10,15,20,25,30],
       'log_odds': [-3,-2,-1,0,1,2,3]}


def coordinate(probability, kind):
    if kind=='probability': return probability
    if kind=='odds': return probability_odds(probability)
    if kind=='log_odds': return log_odds(probability)
    raise ValueError('unknown coordinate system')


def screen_x(probability,kind):
    return axis_coordinate(coordinate(probability,kind),DOMAINS[kind],width=WIDTH,left=LEFT_EDGE)


def update_arrow(before,after,kind,y):
    """No buffer: the actual arrow endpoints are the actual belief coordinates."""
    a,b=screen_x(before,kind),screen_x(after,kind)
    return Arrow([a,y,0],[b,y,0],buff=0,color=BLUE,stroke_width=3,tip_length=.12,
                 max_tip_length_to_length_ratio=.25,max_stroke_width_to_length_ratio=4)


def ruler_rows(examples, kind, *, show_after=False, row_labels=None):
    """Return static axes and true-size before/after marks on a common domain."""
    group=VGroup()
    for i,example in enumerate(examples):
        y=1.38-i*1.22
        row_label = row_labels[i] if row_labels is not None else f"Start {example['prior']:.0%}"
        group.add(label(row_label,25,color=MUTED,max_width=3).move_to([-5.18,y,0]))
        group.add(Line([LEFT_EDGE,y,0],[LEFT_EDGE+WIDTH,y,0],color=MUTED,stroke_width=2))
        for t in TICKS[kind]:
            x=axis_coordinate(t,DOMAINS[kind],width=WIDTH,left=LEFT_EDGE)
            group.add(Line([x,y-.055,0],[x,y+.055,0],color=MUTED,stroke_width=1.4))
            tick=f'{t:.0%}' if kind=='probability' else f'{t:g}'
            group.add(label(tick,18,color=MUTED).move_to([x,y-.22,0]))
        x=screen_x(example['prior'],kind)
        group.add(Circle(radius=.085,stroke_width=2.5,color=BLUE,fill_opacity=0).move_to([x,y,0]))
        if show_after:
            group.add(update_arrow(example['prior'],example['posterior'],kind,y))
            x_after=screen_x(example['posterior'],kind)
            group.add(Square(side_length=.15,color=BLUE,fill_opacity=1).rotate(math.pi/4).move_to([x_after,y,0]))
    return group


def dynamic_marks(examples,kind,alpha,*,inverse=False):
    """All rows share alpha; the bridge is a visual interpolation, not more evidence."""
    group=VGroup()
    for i,example in enumerate(examples):
        y=1.38-i*1.22
        current=binary_update(example['prior'],3**alpha)
        before=example['posterior'] if inverse else example['prior']
        if abs(current-before)>1e-12:
            group.add(update_arrow(before,current,kind,y))
        x=screen_x(current,kind)
        group.add(Square(side_length=.15,color=BLUE,fill_opacity=1).rotate(math.pi/4).move_to([x,y,0]))
    return group
