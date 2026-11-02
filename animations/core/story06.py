"""Leaf, conditional finding and decision calculations with explicit inputs."""
import json
from pathlib import Path
from .leaf_plots import leaf, logit_point
from .decision_math import utility_difference, thresholds


def story():
    data = json.loads((Path(__file__).resolve().parents[1]/'data/beliefs_actions_fixtures.json').read_text())['goal_06']
    value = lambda row: row['numerator']/row['denominator']
    se, sp = value(data['sensitivity']), value(data['specificity'])
    lp, lm = se/(1-sp), (1-se)/sp
    examples = []
    for row in data['examples']:
        p = value(row['prior']); qp, qm = leaf(p, lp), leaf(p, lm)
        examples.append({'prior': p, 'positive': qp, 'negative': qm,
            'log_positive': logit_point(p, lp), 'log_negative': logit_point(p, lm),
            'utility_prior': utility_difference(p), 'utility_positive': utility_difference(qp),
            'utility_negative': utility_difference(qm),
            'utility_change': utility_difference(qp)-utility_difference(p)})
    second = data['conditional_finding']
    conditional_lr = value(second['disease_probability'])/value(second['no_disease_probability'])
    return {'sensitivity': se, 'specificity': sp, 'lr_positive': lp, 'lr_negative': lm,
            'examples': examples, 'conditional_lr': conditional_lr,
            'sequential_posterior': leaf(examples[0]['positive'], conditional_lr),
            'thresholds': [thresholds(row['benefit'], row['cost']) for row in data['utilities']]}
