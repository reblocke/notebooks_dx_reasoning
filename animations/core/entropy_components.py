"""Manim adapters for fixed, undistorted surprisal rectangles."""
from manim import VGroup, Line, Rectangle, Dot, LEFT
from math import pi
from .components import label, COLORS, WHITE, MUTED
from .entropy_geometry import rectangle_geometry

X0,Y0=-5.45,-1.1
PLOT_WIDTH,PLOT_HEIGHT,MAX_SURPRISAL=6.8,3.6,7.2


def rectangles(probabilities, categories=(0,1,2)):
    data=rectangle_geometry(probabilities,plot_width=PLOT_WIDTH,plot_height=PLOT_HEIGHT,max_surprisal=MAX_SURPRISAL)
    objects=VGroup()
    for i in categories:
        r=data[i]
        box=Rectangle(width=r.width,height=r.height,stroke_color=COLORS[i],stroke_width=2,
                      fill_color=COLORS[i],fill_opacity=.58)
        box.move_to([X0+r.left+r.width/2,Y0+r.height/2,0])
        objects.add(box)
    return objects


def axes():
    group=VGroup(Line([X0,Y0,0],[X0+PLOT_WIDTH,Y0,0],color=WHITE,stroke_width=2),
                 Line([X0,Y0,0],[X0,Y0+PLOT_HEIGHT,0],color=WHITE,stroke_width=2))
    for v in (0,.25,.5,.75,1):
        x=X0+PLOT_WIDTH*v
        group.add(Line([x,Y0-.05,0],[x,Y0+.05,0],color=MUTED,stroke_width=1.5))
        group.add(label(f'{v:.0%}',19,color=MUTED).move_to([x,Y0-.25,0]))
    for v in (0,1,2,4,6,7.2):
        y=Y0+PLOT_HEIGHT*v/MAX_SURPRISAL
        group.add(Line([X0-.05,y,0],[X0+.05,y,0],color=MUTED,stroke_width=1.5))
        group.add(label(f'{v:g}',19,color=MUTED).move_to([X0-.27,y,0]))
    group.add(label('Cumulative probability',23,color=MUTED).move_to([X0+PLOT_WIDTH/2,Y0-.65,0]))
    group.add(label('Surprisal (bits)',23,color=MUTED).rotate(pi/2).move_to([-6.25,Y0+PLOT_HEIGHT/2,0]))
    return group


def entropy_meter(h):
    from math import log2
    x0,y=-5.25,-2.42
    width=6.2
    return VGroup(label(f'Entropy H = {h:.3f} bits',23).move_to([-2.15,-2.16,0]),
                  Line([x0,y,0],[x0+width,y,0],color='#374151',stroke_width=6),
                  Line([x0,y,0],[x0+width*h/log2(3),y,0],color=WHITE,stroke_width=6),
                  label('0',18,color=MUTED).move_to([x0,y-.23,0]),
                  label('log₂(3)',18,color=MUTED).move_to([x0+width,y-.23,0]))


def probability_strip(probabilities, *, left=1.65, y=-1.45, width=4.2):
    """A separate normalized strip whose segment lengths share one scale."""
    from .math import distribution
    p=distribution(probabilities)
    if len(p)!=3: raise ValueError('three categories required')
    group=VGroup(); offset=0
    for value,color in zip(p,COLORS):
        if value>0:
            segment=Rectangle(width=width*value,height=.16,stroke_color=color,stroke_width=1,
                              fill_color=color,fill_opacity=.8)
            segment.move_to([left+width*(offset+value/2),y,0]);group.add(segment)
        offset+=value
    return group


def rare_a_leader(probabilities):
    """Call out the true narrow A rectangle without widening it."""
    r=rectangle_geometry(probabilities,plot_width=PLOT_WIDTH,plot_height=PLOT_HEIGHT,max_surprisal=MAX_SURPRISAL)[0]
    if r.p > .02:
        return VGroup()
    x=X0+r.width/2; y=Y0+r.height
    return VGroup(Line([x,y,0],[x+.55,y,0],color=WHITE,stroke_width=1.5),
                  label(f'A {100*r.p:.1f}%',20,color=WHITE).move_to([x+.95,y,0]))
