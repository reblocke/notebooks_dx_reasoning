"""Common, fixed atlas geometry and heat-map scale."""
import math
import numpy as np
from .math import entropy, to_barycentric

MAX_H = math.log2(3)


def position(p, center=(-3.3, -1.1), side=3.8):
    xy = to_barycentric(p)
    return np.array([center[0] + side*xy[0], center[1] + side*xy[1], 0.])


def trace_position(index, h, left=1.4, bottom=-1.75, width=4.2, height=1.5):
    if not (0 <= index <= 4 and 0 <= h <= 1.65):
        raise ValueError('trace values out of range')
    return np.array([left + width*index/4, bottom + height*h/1.65, 0.])


def heat_value(p):
    return entropy(p)/MAX_H
