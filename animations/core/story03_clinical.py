"""Faster narrated clinical framing of the frozen entropy-area fixture."""
from .cues import Cue, validate_cues
from .story03 import story as original_story

SLUG = '03_entropy_area_clinical_v2'
CLINICAL_CUES = [
    (0, 6, 'Entropy is expected surprise.', 'Entropy is the surprise we expect if the cause were revealed.'),
    (6, 14, 'Probability × surprise = area.', 'For heart failure at fifty percent, surprise is one bit. Probability times surprise gives half a bit.'),
    (14, 22, 'Add the three areas.', 'Pneumonia and malignancy each contribute another half bit. Add the areas: one point five bits of entropy.'),
    (22, 32, 'A rarer cause can contribute less.', 'In a separate example, heart failure falls from ten percent to one. Surprise rises, but its narrow rectangle contributes less.'),
    (32, 39, 'Equal probabilities maximize entropy.', 'Equal probabilities maximize entropy. Concentrating belief on one cause reduces it.'),
    (39, 48, 'An exudative result can increase entropy.', 'Our hypothetical exudative fluid result spreads belief across the causes. Entropy rises from point five seven to one point five bits.'),
    (48, 54, 'Entropy is probability-weighted surprise.', 'Entropy summarizes uncertainty. The same total can describe different beliefs.'),
]


def story():
    data = original_story()
    data['cues'] = [Cue(f'C{i:02d}', start, end, caption, narration)
                    for i, (start, end, caption, narration) in enumerate(CLINICAL_CUES, 1)]
    validate_cues(data['cues'], 54)
    return data
