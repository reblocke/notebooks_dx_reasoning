"""Small reusable visual components with fixed scales and explicit labels."""
from manim import (VGroup, Text, Line, Rectangle, Square, LEFT, RIGHT, UP,
                   DOWN, UpdateFromAlphaFunc)

FONT = 'Arial'
BG = '#111827'
WHITE = '#F3F4F6'
MUTED = '#C6CFDA'
COLORS = ('#56B4E9', '#E69F00', '#CC79A7')


def label(value, size=30, color=WHITE, max_width=None):
    obj = Text(str(value), font=FONT, font_size=size, color=color, line_spacing=.85)
    if max_width is not None and obj.width > max_width:
        obj.scale_to_fit_width(max_width)
    return obj


def fade_replace(mobject, target):
    """Fade out, switch at zero opacity, then fade in without deforming glyphs."""
    before, after = mobject.copy(), target.copy()

    def update(obj, alpha):
        obj.become(before if alpha < .5 else after)
        obj.fade(1 - abs(2*alpha - 1))

    return UpdateFromAlphaFunc(mobject, update)


def probability_chart(title, probabilities, *, width=4.2, selected=None):
    """Three horizontal bars; physical lengths are exactly probability times width."""
    g = VGroup()
    g.add(label(title, 28, max_width=width+1.6).move_to(UP*1.22))
    x0 = -width/2
    for i, (name, p, color) in enumerate(zip('ABC', probabilities, COLORS)):
        y = .58-i*.48
        g.add(label(name, 27, color).move_to([x0-.34,y,0]))
        g.add(Line([x0,y,0],[x0+width,y,0],stroke_width=7,color='#374151'))
        if p > 0:
            bar = Rectangle(width=width*float(p),height=.16,stroke_width=0,fill_color=color,
                            fill_opacity=.25 if selected is not None else 1)
            bar.move_to([x0+width*float(p)/2,y,0]);g.add(bar)
            if selected is not None and selected[i] > 0:
                selected_mass = float(p) * float(selected[i])
                overlay = Rectangle(width=width*selected_mass,height=.16,stroke_width=0,
                                    fill_color=color,fill_opacity=1)
                overlay.move_to([x0+width*selected_mass/2,y,0]);g.add(overlay)
        display = f'{100*p:.2f}%' if 0 < p < .01 or .98 < p < 1 else f'{100*p:.0f}%'
        g.add(label(display, 25, max_width=.9).move_to([x0+width+.55,y,0]))
    axis_y=-.82
    g.add(Line([x0,axis_y,0],[x0+width,axis_y,0],color=MUTED,stroke_width=1.5))
    for value in (0,.5,1):
        x=x0+width*value
        g.add(Line([x,axis_y-.06,0],[x,axis_y+.06,0],color=MUTED,stroke_width=1.5))
        g.add(label(f'{value:.0%}',20,color=MUTED).move_to([x,axis_y-.25,0]))
    return g


def card(title, value, subtitle='', width=5.0):
    box=Rectangle(width=width,height=1.25,stroke_color='#526075',stroke_width=1.5,fill_color='#1F2937',fill_opacity=1)
    heading=label(title,25,color=MUTED,max_width=width-.25).move_to(UP*.32)
    content=label(value,32,max_width=width-.25).move_to(DOWN*.15 if not subtitle else DOWN*.05)
    g=VGroup(box,heading,content)
    if subtitle: g.add(label(subtitle,20,color=MUTED,max_width=width-.2).move_to(DOWN*.42))
    return g
