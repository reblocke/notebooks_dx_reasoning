"""Truthful probability/logit axes and single-decision utility geometry."""
from manim import Axes, VGroup, Line, DashedLine, Dot, Arrow
from .components import label, MUTED
from .leaf_plots import leaf, clipped_log_line
from .decision_math import utility_difference, thresholds

POSITIVE = '#56B4E9'
NEGATIVE = '#E69F00'


def leaf_axes(log=False):
    domain = [-4,4,2] if log else [0,1,.25]
    axes=Axes(x_range=domain,y_range=domain,x_length=4.5,y_length=4.5,
              tips=False,axis_config={'color':MUTED,'include_ticks':False}).move_to([-2.25,-.05,0])
    ticks = [-4,-2,0,2,4] if log else [0,.25,.5,.75,1]
    group=VGroup(axes)
    low = domain[0]
    for t in ticks:
        text=f'{t:g}' if log else f'{t:.0%}'
        group.add(label(text,18,MUTED).move_to(axes.c2p(t,low)+[0,-.2,0]),
                  label(text,18,MUTED).move_to(axes.c2p(low,t)+[-.37,0,0]))
    group.add(label('Pretest log odds X' if log else 'Pretest probability p',22,MUTED).move_to([-2.25,-2.85,0]),
              label('Post-test log odds Y' if log else 'Post-test probability q',22,MUTED).rotate(1.5707963267948966).move_to([-5.45,-.05,0]))
    group.add(DashedLine(axes.c2p(low,low),axes.c2p(domain[1],domain[1]),color=MUTED,dash_length=.08))
    return group,axes


def result_curve(axes, lr, log=False):
    color = POSITIVE if lr>1 else NEGATIVE
    if log:
        ends=clipped_log_line(lr)
        line=Line(axes.c2p(*ends[0]),axes.c2p(*ends[1]),color=color,stroke_width=3)
        if lr<1:
            return DashedLine(line.get_start(),line.get_end(),color=color,dash_length=.09,stroke_width=3)
        return line
    curve=axes.plot(lambda p: leaf(p,lr),x_range=[0,1,.01],color=color,stroke_width=3,use_smoothing=False)
    if lr<1:
        from manim import DashedVMobject
        return DashedVMobject(curve,num_dashes=36)
    return curve


def leaf_guide(axes,p,lr):
    q=leaf(p,lr);color=POSITIVE if lr>1 else NEGATIVE
    return VGroup(Dot(axes.c2p(p,p),radius=.055,color=MUTED),
                  Arrow(axes.c2p(p,p),axes.c2p(p,q),buff=0,color=color,stroke_width=3,tip_length=.08),
                  DashedLine(axes.c2p(p,q),axes.c2p(0,q),color=color,dash_length=.06),
                  Dot(axes.c2p(p,q),radius=.06,color=color))


def utility_axes():
    axes=Axes(x_range=[0,1,.2],y_range=[-4,4,2],x_length=6,y_length=4,
              tips=False,axis_config={'color':MUTED,'include_ticks':False}).move_to([-1.8,-.15,0])
    group=VGroup(axes)
    for p in (0,.2,.5,1):
        group.add(label(f'{p:.0%}',19,MUTED).move_to(axes.c2p(p,-4)+[0,-.2,0]))
    for gain in (-4,-2,0,2,4):
        group.add(label(f'{gain:g}',19,MUTED).move_to(axes.c2p(0,gain)+[-.3,0,0]))
    group.add(label('Probability available at the decision',23,MUTED).move_to([-1.8,-2.8,0]),
              label('Act minus defer: utility units',22,MUTED).move_to([-1.8,2.28,0]))
    return group,axes


def utility_line(axes,cost=1):
    return Line(axes.c2p(0,-cost),axes.c2p(1,4),color=POSITIVE,stroke_width=3)


def utility_mark(axes,p,cost=1):
    return Dot(axes.c2p(p,utility_difference(p,4,cost)),radius=.075,color=NEGATIVE)


def threshold_mark(axes,cost=1):
    t=thresholds(4,cost)['probability']
    return VGroup(DashedLine(axes.c2p(t,-4),axes.c2p(t,4),color=NEGATIVE,dash_length=.08),
                  Dot(axes.c2p(t,0),radius=.065,color=NEGATIVE))
