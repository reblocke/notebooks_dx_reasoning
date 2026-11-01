"""Short clinical teaching cut; all numbers come from the original fixture."""
from .cues import Cue, validate_cues
from .story01 import story as original_story
from .voice_config import VOICE, VOICE_RATE

SLUG = '01_uncertainty_increases_clinical_v2'

CLINICAL_CUES = [
    (0, 9, 'Weight each possible change by its probability.',
     'Entropy measures diagnostic uncertainty. Expected change averages what each possible result would do, weighted by how likely it is.'),
    (9, 19, 'Assume one of these three causes.',
     'Take a simplified pleural effusion: heart failure, pneumonia, or malignancy. Heart failure starts at ninety percent. These numbers are illustrative.'),
    (19, 26, 'Exudative fluid fits the alternatives better.',
     'Exudative fluid occurs in ten percent of heart failure cases, but ninety percent under either alternative.'),
    (26, 34, 'Condition on the observed exudative result.',
     'Multiply prior by likelihood, then normalize. The posterior becomes fifty, twenty-five, twenty-five percent.'),
    (34, 39, 'This result increases diagnostic uncertainty.',
     'Uncertainty rises from about point five seven to one point five bits.'),
    (39, 47, 'Average across both possible outcomes.',
     'Non-exudative fluid concentrates the differential. Weighting both outcomes predicts about point two one bits less uncertainty.'),
    (47, 54, 'Less uncertainty on average; more after this result.',
     'A test can reduce uncertainty on average, yet increase it for this case.'),
]


def story():
    data = original_story()
    data['cues'] = [Cue(f'C{i:02d}', start, end, caption, narration)
                    for i, (start, end, caption, narration) in enumerate(CLINICAL_CUES, 1)]
    validate_cues(data['cues'], 54)
    return data
