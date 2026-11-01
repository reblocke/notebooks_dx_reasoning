"""Faster narrated clinical framing of the frozen trajectory atlas."""
from .cues import Cue, validate_cues
from .story04 import story as original_story

SLUG = '04_trajectory_atlas_clinical_v2'
CLINICAL_CUES = [
    (0, 6, 'Uncertainty can follow different paths.', 'Uncertainty can fall, rise, or stay high as findings arrive.'),
    (6, 16, 'One point represents one distribution.', 'Each point divides belief among our three causes of pleural effusion. The center is most uncertain; corners concentrate on one cause.'),
    (16, 24, 'Convergence: support concentrates.', 'Four hypothetical findings concentrate belief on heart failure. The markers show observations; motion only connects them.'),
    (24, 32, 'Reopening: uncertainty increases.', 'A separate patient starts with heart failure favored. This time, the findings reopen the differential.'),
    (32, 40, 'Substitution: the leading cause changes.', 'Here, pneumonia replaces heart failure as the leader. Initial and final entropy match, although the beliefs differ.'),
    (40, 48, 'Ambiguity can persist.', 'In another patient, all three causes remain plausible. Updating does not guarantee a clear diagnosis.'),
    (48, 53, 'Four hypothetical paths; shared scales.', 'These are different hypothetical paths, not measures of clinical success.'),
    (53, 57, 'States 0–2: uncertainty rises.', 'The first encounter window shows uncertainty rising.'),
    (57, 61, 'States 2–4: uncertainty falls.', 'Earlier evidence is included. Now uncertainty falls.'),
    (61, 65, 'States 0–4: no net entropy change.', 'Across the full path, entropy ends where it began.'),
    (65, 72, 'Follow the evidence; certainty is not required.', 'Follow the evidence. A diagnostic encounter need not end in certainty.'),
]


def story():
    data = original_story()
    data['cues'] = [Cue(f'C{i:02d}', start, end, caption, narration)
                    for i, (start, end, caption, narration) in enumerate(CLINICAL_CUES, 1)]
    validate_cues(data['cues'], 72)
    return data
