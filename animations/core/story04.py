"""Frozen synthetic atlas models, Bayes-derived states and synchronized cues."""
import json
from pathlib import Path
import numpy as np
from .cues import Cue, validate_cues
from .math import bayes_update, entropy

FIXTURE = Path(__file__).resolve().parents[1] / 'data/manim_fixtures.json'
TEXT = [
 ('Encounters can begin and end with different uncertainty.', 'A diagnostic encounter may begin with a working diagnosis, and may end before the question is resolved.'),
 ('Each point is one distribution over A, B, and C.', 'The corners represent three fixed possibilities. The center gives them equal probability. The bars show the same distribution as the point.'),
 ('The background shows entropy; markers record findings.', 'Entropy is highest at the center and zero at a corner. Marker zero is the prior. Markers one through four follow observed findings; motion only illustrates transitions.'),
 ('Successive findings concentrate support on A.', 'In this synthetic vignette, each finding increases support for A. Entropy falls as the distribution concentrates.'),
 ('Findings can appropriately reopen a differential.', 'A different vignette starts with ninety percent on A. Findings favor the alternatives and uncertainty rises.'),
 ('The leading diagnosis changes, though endpoint entropy agrees.', 'Support shifts from A to B. Initial and final entropy agree even though the beliefs differ; the intermediate uncertainty changes.'),
 ('Several possibilities can remain plausible.', 'In another independent vignette, the findings move probabilities but leave substantial ambiguity.'),
 ('Four constructed paths follow explicit probability models.', 'These are four independently constructed examples, not a comparison of methods or estimates of clinical frequency.'),
 ('An encounter can show only a segment of a longer path.', 'The first part of substitution increases entropy; the later part decreases it. A middle starting belief already includes earlier findings.'),
 ('Follow the evidence. The encounter need not end in certainty.', 'The direction of uncertainty should follow the evidence. An encounter need not end in certainty.'),
]


def story():
    fixture = json.loads(FIXTURE.read_text())['goal_04']
    cues = [Cue(b['beat_id'], b['start'], b['end'], *text) for b, text in zip(fixture['beats'], TEXT)]
    validate_cues(cues, fixture['nominal_duration_seconds'])
    cases = {}
    for case in fixture['cases']:
        p = np.asarray(case['states'][0]['p'], float)
        states = [p]
        likelihoods = [np.asarray(f['p_observed_given_d'], float) for f in case['findings']]
        for likelihood in likelihoods:
            p = bayes_update(p, likelihood).posterior
            states.append(p)
        for actual, target in zip(states, case['states']):
            if not np.allclose(actual, target['p'], atol=1e-10, rtol=0) or abs(entropy(actual)-target['entropy_bits']) > 1e-10:
                raise ValueError('Frozen likelihoods do not reproduce atlas fixture')
        cases[case['case_id']] = {'states': states, 'likelihoods': likelihoods}
    return {'fixture': fixture, 'cues': cues, 'cases': cases}
