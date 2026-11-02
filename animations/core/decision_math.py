"""Incremental utility of act versus defer in the stated binary toy model."""
import math


def validate_payoffs(benefit, cost):
    if not all(math.isfinite(x) and x > 0 for x in (benefit, cost)):
        raise ValueError('Benefit and cost must be finite positive magnitudes')


def utility_difference(probability, benefit=4, cost=1):
    validate_payoffs(benefit, cost)
    if not math.isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError('Probability must be in [0,1]')
    return probability*benefit-(1-probability)*cost


def thresholds(benefit=4, cost=1):
    validate_payoffs(benefit, cost)
    odds = cost/benefit
    return {'probability': cost/(benefit+cost), 'odds': odds, 'log_odds': math.log(odds)}


def preference(probability, benefit=4, cost=1):
    threshold = thresholds(benefit, cost)['probability']
    return 'indifferent' if probability == threshold else ('act' if probability > threshold else 'defer')
