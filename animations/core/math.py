"""Pure calculations for fixed synthetic diagnostic models.

All probabilities entering entropy are normalized diagnostic distributions;
likelihoods and unnormalized joint masses have distinct return types.
"""
from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class Update:
    joint: np.ndarray
    evidence_probability: float
    posterior: np.ndarray


def distribution(values):
    p = np.asarray(values, dtype=float)
    if p.ndim != 1 or p.size < 1 or not np.isfinite(p).all() or np.any(p < 0):
        raise ValueError('probabilities must be a finite, nonnegative vector')
    if not np.isclose(p.sum(), 1, atol=1e-12, rtol=0):
        raise ValueError('probabilities must sum to one')
    return p.copy()


def entropy(values):
    p = distribution(values)
    positive = p[p > 0]
    return float(-np.sum(positive * np.log2(positive)))


def bayes_update(prior, likelihood):
    p = distribution(prior)
    likelihood = np.asarray(likelihood, dtype=float)
    if likelihood.shape != p.shape or not np.isfinite(likelihood).all() or np.any(likelihood < 0):
        raise ValueError('likelihoods must be a finite nonnegative vector matching the prior')
    with np.errstate(under='ignore', over='ignore', invalid='ignore'):
        joint = p * likelihood
        total = float(joint.sum())
    if not np.isfinite(total) or total <= 0:
        raise ValueError('evidence has zero or unrepresentable probability')
    posterior = joint / total
    return Update(joint=joint, evidence_probability=total, posterior=distribution(posterior))


def expected_posterior_entropy(prior, event_likelihood):
    p = distribution(prior)
    likelihood = np.asarray(event_likelihood, dtype=float)
    if likelihood.shape != p.shape or not np.isfinite(likelihood).all() or np.any(likelihood < 0) or np.any(likelihood > 1):
        raise ValueError('binary event likelihoods must be between zero and one')
    # A zero-probability branch contributes zero and has no posterior entropy.
    value = 0.0
    for row in (likelihood, 1-likelihood):
        mass = float(np.dot(p, row))
        if mass > 0:
            value += mass * entropy(bayes_update(p, row).posterior)
    return value


def binary_update(probability, lr):
    p, lr = float(probability), float(lr)
    if not math.isfinite(p) or not 0 <= p <= 1 or not math.isfinite(lr) or lr <= 0:
        raise ValueError('probability must be in [0,1] and LR finite and positive')
    if p in (0,1):
        return p
    # Logistic coordinates avoid overflow in p*LR for the accepted domain.
    z = log_odds(p) + math.log(lr)
    return 1/(1+math.exp(-z)) if z >= 0 else math.exp(z)/(1+math.exp(z))


def probability_odds(probability):
    p = float(probability)
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError('probability must be finite and in [0,1]')
    return math.inf if p == 1 else p/(1-p)


def log_odds(probability):
    p = float(probability)
    if not math.isfinite(p) or not 0 < p < 1:
        raise ValueError('log odds require a probability in (0,1)')
    return math.log(p) - math.log1p(-p)


def bridge(prior, likelihood, alpha):
    p = distribution(prior)
    lr = np.asarray(likelihood, dtype=float)
    alpha = float(alpha)
    if (lr.shape != p.shape or not np.isfinite(lr).all() or np.any(lr <= 0)
            or not math.isfinite(alpha) or not 0 <= alpha <= 1):
        raise ValueError('bridge requires matching positive likelihoods and alpha in [0,1]')
    active = p > 0
    z = np.full(len(p), -np.inf)
    z[active] = np.log(p[active]) + alpha * np.log(lr[active])
    weights = np.exp(z - np.max(z))
    return distribution(weights / weights.sum())


def to_barycentric(values):
    p = distribution(values)
    if p.size != 3:
        raise ValueError('simplex geometry requires three probabilities')
    return np.array([(p[2]-p[1])/2, math.sqrt(3)*p[0]/2])


def from_barycentric(coordinates):
    xy = np.asarray(coordinates, dtype=float)
    if xy.shape != (2,) or not np.isfinite(xy).all():
        raise ValueError('coordinates must be a finite pair')
    x, y = xy
    a = 2*y/math.sqrt(3)
    p = np.array([a, (1-a)/2-x, (1-a)/2+x])
    if np.any(p < -1e-12):
        raise ValueError('point lies outside the simplex')
    p[np.abs(p) < 1e-15] = 0
    return distribution(p)


def axis_coordinate(value, domain, *, width, left):
    """Map a value to a fixed linear screen ruler without row-wise rescaling."""
    value, width, left = float(value), float(width), float(left)
    bounds = np.asarray(domain, dtype=float)
    if (bounds.shape != (2,) or not np.isfinite(bounds).all() or bounds[0] >= bounds[1]
            or not np.isfinite([value, width, left]).all() or width <= 0
            or value < bounds[0] or value > bounds[1]):
        raise ValueError('value, domain and ruler width must be finite and in range')
    return float(left + width * (value-bounds[0])/(bounds[1]-bounds[0]))
