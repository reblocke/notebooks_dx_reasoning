"""Fixed-scale probability-by-surprisal rectangle geometry."""
from dataclasses import dataclass
import numpy as np
from .math import distribution


@dataclass(frozen=True)
class RectangleGeometry:
    p: float
    surprisal: float
    contribution: float
    left: float
    width: float
    height: float


def rectangle_geometry(probabilities, *, plot_width, plot_height, max_surprisal):
    p=distribution(probabilities)
    dimensions=np.asarray([plot_width,plot_height,max_surprisal],dtype=float)
    if p.size != 3 or np.any(p<=0):
        raise ValueError('rendered rectangles require three strictly positive probabilities')
    if not np.isfinite(dimensions).all() or np.any(dimensions<=0):
        raise ValueError('plot scales must be finite and positive')
    surprise=-np.log2(p)
    if np.any(surprise>max_surprisal):
        raise ValueError('surprisal exceeds the fixed vertical scale')
    edges=np.concatenate(([0.],np.cumsum(p[:-1])))
    return [RectangleGeometry(float(q),float(h),float(q*h),float(x*plot_width),
                              float(q*plot_width),float(h*plot_height/max_surprisal))
            for q,h,x in zip(p,surprise,edges)]
