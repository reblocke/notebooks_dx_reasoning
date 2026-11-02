"""Synthetic test results; expectations remain independent fixture references."""
import json
from pathlib import Path
from .math import binary_update


def story():
    fixture = json.loads((Path(__file__).resolve().parents[1]/'data/test_results_fixtures.json').read_text())['goal_05']
    profiles = {}
    for row in fixture['profiles']:
        se, sp = (row[k]['numerator']/row[k]['denominator'] for k in ('sensitivity', 'specificity'))
        lr_plus, lr_minus = se/(1-sp), (1-se)/sp
        examples = []
        for example in row['examples']:
            prior = example['prior']['numerator']/example['prior']['denominator']
            examples.append({'prior': prior, 'positive': binary_update(prior, lr_plus),
                             'negative': binary_update(prior, lr_minus)})
        profiles[row['id']] = {'sensitivity': se, 'specificity': sp, 'lr_positive': lr_plus,
            'lr_negative': lr_minus, 'examples': examples,
            'counts': {'disease_positive': round(100*se), 'disease_negative': round(100*(1-se)),
                       'no_disease_positive': round(900*(1-sp)), 'no_disease_negative': round(900*sp)}}
    return {'profiles': profiles}
