"""Pure probability-leaf and clipped natural-log-odds geometry."""
import math
from .math import binary_update, log_odds


def leaf(probability, likelihood_ratio):
    return binary_update(probability, likelihood_ratio)


def logit_point(prior, likelihood_ratio):
    return log_odds(prior), log_odds(leaf(prior, likelihood_ratio))


def clipped_log_line(likelihood_ratio, bounds=(-4, 4)):
    low, high = bounds
    if not (math.isfinite(likelihood_ratio) and likelihood_ratio > 0
            and math.isfinite(low) and math.isfinite(high) and low < high):
        raise ValueError('Finite positive LR and increasing finite bounds required')
    offset = math.log(likelihood_ratio)
    left, right = max(low, low-offset), min(high, high-offset)
    if left > right:
        return None
    return (left, left+offset), (right, right+offset)
