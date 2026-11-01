"""Goal 01's cue source and independent model-derived display values."""
import json
from pathlib import Path
from .cues import Cue, validate_cues
from .math import bayes_update, entropy, expected_posterior_entropy

FIXTURE = Path(__file__).resolve().parents[1] / 'data/manim_fixtures.json'

TEXT = [
 ('One diagnosis begins at 90%.', 'Our synthetic model starts with three exclusive diagnoses. A has ninety percent of the probability, while B and C each have five percent.'),
 ('Entropy measures uncertainty across A, B and C.', 'One binary finding has two possible outcomes: present and absent. Before observing it, entropy across the three diagnoses is about zero point five seven bits.'),
 ('E is more likely under B and C than under A.', 'We observe E present. In this model it occurs in ten percent of A cases and ninety percent of B or C cases. These are conditional likelihoods, not a distribution over diagnoses.'),
 ('Joint masses total 0.18; they are not yet normalized.', 'Multiply the prior probability of each diagnosis by the probability of E under that diagnosis. The three joint masses total zero point one eight, the probability of observing E.'),
 ('Among outcomes with E, the posterior is 50%, 25%, 25%.', 'Condition on the observed E by dividing each joint mass by the total zero point one eight. The posterior is fifty percent A, twenty-five percent B, and twenty-five percent C.'),
 ('After this finding, diagnostic uncertainty is higher.', 'The normalized posterior is more spread out. Its entropy is one point five bits, compared with approximately zero point five seven bits before E.'),
 ('The finding supports a wider differential.', 'This is the posterior supported by the stipulated synthetic model after E. The diagnosis remains unresolved, with substantial probability on all three possibilities.'),
 ('Rewind: consider both possible outcomes.', 'Now rewind to before the outcome was known. This is a change of perspective, not a new observation. What was the finding expected to do to uncertainty?'),
 ('E spreads the posterior. Its absence concentrates it.', 'E has an eighteen percent probability and leads to the fifty, twenty-five, twenty-five posterior. E absent has an eighty-two percent probability and would yield approximately ninety-eight point seven eight percent A and zero point six one percent each for B and C.'),
 ('Average the branch entropies: expected uncertainty falls.', 'Weight each possible posterior entropy by the probability of that outcome. Expected posterior entropy is about zero point three five eight bits, so expected information gain is positive, about zero point two one one bits.'),
 ('Our observed branch increased uncertainty.', 'We observed E, the branch with higher entropy. Positive expected information gain does not mean that every possible outcome reduces uncertainty.'),
 ('The diagnosis remains unresolved after E.', 'A valid update can widen the differential. The final posterior is fifty percent A and twenty-five percent each for B and C; the diagnosis remains unresolved.'),
]


def story():
    fixture = json.loads(FIXTURE.read_text())['goal_01']
    prior = fixture['prior']
    likelihood = fixture['branches'][0]['likelihood']
    observed = bayes_update(prior, likelihood)
    absent = bayes_update(prior, [1-v for v in likelihood])
    expected = expected_posterior_entropy(prior, likelihood)
    cues = [Cue(row['beat_id'], row['start'], row['end'], caption, narration)
            for row, (caption, narration) in zip(fixture['beats'], TEXT)]
    validate_cues(cues, fixture['nominal_duration_seconds'])
    return {'prior': prior, 'likelihood': likelihood, 'observed': observed,
            'absent': absent, 'prior_h': entropy(prior),
            'observed_h': entropy(observed.posterior), 'absent_h': entropy(absent.posterior),
            'expected_h': expected, 'expected_gain': entropy(prior)-expected,
            'cues': cues, 'fixture': fixture}
