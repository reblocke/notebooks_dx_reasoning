"""A short clinical framing of the original separate binary examples."""
from .cues import Cue, validate_cues
from .story02 import story as original_story

SLUG = '02_coordinate_systems_clinical_v2'

CLINICAL_CUES = [
    (0, 8, 'One finding; three starting beliefs.',
     'The same evidence can change probability by different amounts. Compare three patients being evaluated for pneumonia.'),
    (8, 16, 'A hypothetical positive test has LR = 3.',
     'Our hypothetical positive test is three times as likely with pneumonia as without it: likelihood ratio three.'),
    (16, 23, 'The probability changes are different.',
     'Ten percent becomes twenty-five; fifty becomes seventy-five; ninety becomes about ninety-six.'),
    (23, 30, 'The same update triples the odds.',
     'Odds compare pneumonia with no pneumonia. The finding triples those odds in every patient.'),
    (30, 38, 'Natural-log odds add the same amount.',
     'Natural log odds turn multiplication into addition: the same shift, plus log three.'),
    (38, 43, 'The inverse returns each starting belief.',
     'An inverse factor of one third returns every start.'),
    (43, 48, 'One update, three descriptions.',
     'Equal shifts do not mean equal changes in uncertainty.'),
]


def story():
    data = original_story()
    data['cues'] = [Cue(f'C{i:02d}', start, end, caption, narration)
                    for i, (start, end, caption, narration) in enumerate(CLINICAL_CUES, 1)]
    validate_cues(data['cues'], 48)
    return data
