"""Fixed-scale atlas views. Paths and entropy traces use identical state vectors."""
import math
import numpy as np
from manim import Group, VGroup, ImageMobject, Polygon, Line, Dot, Rectangle
from .components import COLORS, WHITE, MUTED, label
from .math import entropy
from .atlas_geometry import MAX_H, position, trace_position


def heatmap(side=3.8, center=(-3.3,-1.1)):
    # One fixed 0..log2(3) scale; outside triangle is transparent.
    n=720; h=int(round(n*math.sqrt(3)/2)); yy,xx=np.mgrid[0:h,0:n]
    a=1-yy/(h-1); x=xx/(n-1)-.5
    b=(1-a)/2-x; c=(1-a)/2+x
    inside=(b>=0)&(c>=0)
    probs=np.stack([a,b,c]); safe=np.maximum(probs,1e-300)
    H=-np.sum(np.where(probs>0,probs*np.log2(safe),0),axis=0)/MAX_H
    H=np.clip(H,0,1)
    low=np.array([28,45,67]); high=np.array([94,115,137])
    rgb=low[None,None,:]*(1-H[:,:,None])+high[None,None,:]*H[:,:,None]
    rgba=np.zeros((h,n,4),dtype=np.uint8);rgba[:,:,:3]=rgb.astype(np.uint8);rgba[:,:,3]=inside*255
    im=ImageMobject(rgba).stretch_to_fit_width(side).stretch_to_fit_height(side*math.sqrt(3)/2)
    im.move_to([center[0],center[1]+side*math.sqrt(3)/4,0])
    return im


def triangle(side=3.8, center=(-3.3,-1.1), names=True):
    vertices=[position(p,center,side) for p in ([1,0,0],[0,1,0],[0,0,1])]
    border=Polygon(*vertices,color=MUTED,stroke_width=2,fill_opacity=0)
    group=Group(heatmap(side,center),border)
    if names:
        for i,(v,off) in enumerate(zip(vertices,([0,.22,0],[-.22,-.15,0],[.22,-.15,0]))):
            group.add(label('ABC'[i],22,COLORS[i]).move_to(v+off))
    return group


def trace_axes(left=1.4,bottom=-1.75,width=4.2,height=1.5,small=False):
    g=VGroup(Line([left,bottom,0],[left+width,bottom,0],color=MUTED),
             Line([left,bottom,0],[left,bottom+height,0],color=MUTED))
    size=13 if small else 18
    for i in range(5):
        x=left+width*i/4;g.add(label(str(i),size,MUTED).move_to([x,bottom-.16,0]))
    if not small:
        g.add(label('Observed finding index',18,MUTED).move_to([left+width/2,bottom-.42,0]),
              label('H (bits)',18,MUTED).move_to([left+.15,bottom+height+.25,0]),
              label('1.65',15,MUTED).move_to([left-.25,bottom+height,0]),
              label('0',15,MUTED).move_to([left-.2,bottom,0]))
    return g


def path(states,center=(-3.3,-1.1),side=3.8,first=0,last=4,small=False):
    g=VGroup()
    for i in range(4):
        g.add(Line(position(states[i],center,side),position(states[i+1],center,side),color=WHITE,stroke_width=3 if first<=i<last else 1,stroke_opacity=1 if first<=i<last else .25))
    for i,p in enumerate(states):
        point=position(p,center,side); active=first<=i<=last
        g.add(Dot(point,radius=.055 if small else .075,color=WHITE,fill_opacity=1 if active else .3))
        if not small:g.add(label(str(i),15,WHITE).move_to(point+[.12,.12,0]))
    return g


def trace(states,left=1.4,bottom=-1.75,width=4.2,height=1.5,first=0,last=4,small=False):
    g=VGroup(); coords=[trace_position(i,entropy(p),left,bottom,width,height) for i,p in enumerate(states)]
    for i in range(len(states)-1):
        g.add(Line(coords[i],coords[i+1],color=WHITE,stroke_width=2 if first<=i<last else 1,stroke_opacity=1 if first<=i<last else .25))
    for i,p in enumerate(coords):g.add(Dot(p,radius=.035 if small else .055,color=WHITE,fill_opacity=1 if first<=i<=last else .3))
    return g


def bars(p):
    g=VGroup()
    for i,(name,value) in enumerate(zip('ABC',p)):
        y=1.62-i*.43; x=1.65; width=3.35
        g.add(label(name,22,COLORS[i]).move_to([1.26,y,0]),Line([x,y,0],[x+width,y,0],color='#374151',stroke_width=9),
              Line([x,y,0],[x+width*value,y,0],color=COLORS[i],stroke_width=9),label(f'{100*value:.1f}%',20).move_to([5.55,y,0]))
    g.add(label(f'Live H = {entropy(p):.3f} bits',22).move_to([3.6,.08,0]))
    return g


def legend():
    g=VGroup()
    for i in range(30):
        x=-5.05+i*3.5/30
        color=tuple((np.array([28,45,67])+(np.array([94,115,137])-np.array([28,45,67]))*i/29)/255)
        from manim import rgb_to_color
        g.add(Rectangle(width=3.5/30+.005,height=.12,stroke_width=0,fill_color=rgb_to_color(color),fill_opacity=1).move_to([x,-1.6,0]))
    g.add(label('H: 0',16,MUTED).move_to([-5.0,-1.85,0]),label('log₂(3) bits',16,MUTED).move_to([-1.72,-1.85,0]))
    return g
