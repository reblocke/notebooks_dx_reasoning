"""Goal 03 cue source and fixed entropy-geometry states."""
import json
from pathlib import Path
from .cues import Cue,validate_cues
from .math import bayes_update

FIXTURE=Path(__file__).resolve().parents[1]/'data/manim_fixtures.json'
TEXT=[
 ('A distribution divides belief among possibilities.', 'Start with three possible diagnoses. Half of the probability belongs to A; B and C each have one quarter.'),
 ('At probability one half, A has one bit of surprisal.', 'If A were revealed, its surprisal would be one bit. The rectangle has probability as width and surprisal as height.'),
 ('Less likely categories can be more surprising.', 'B and C each have probability one quarter and surprisal two bits. Width and height represent different quantities.'),
 ('Each area weights a possible surprise by its probability.', 'Multiply probability by surprisal. A contributes half a bit; B and C each contribute another half bit.'),
 ('Entropy is the sum of probability-weighted surprise.', 'Add the three areas. Their total is one and a half bits: the surprise expected across this complete distribution.'),
 ('A rarer possibility is more surprising but narrower.', 'Switch to a separate hypothetical example. As A falls from ten percent to one percent, its rectangle gets taller and narrower. Its contribution falls over these selected values.'),
 ('High surprisal need not mean a large entropy contribution.', 'At one percent, A would be very surprising if revealed, yet its expected contribution is only about zero point zero seven bits. The comparison is limited to these selected examples.'),
 ('Uniform probabilities maximize entropy for fixed categories.', 'Three equal probabilities give the maximum entropy for these fixed categories. A concentrated prior has lower total entropy even though its rare categories have greater surprisal.'),
 ('A synthetic finding can increase the total area.', 'Now observe a finding that is unlikely under A and likely under B or C. It updates the concentrated prior to fifty, twenty-five, twenty-five and increases entropy from about zero point five seven to one point five bits.'),
 ('Entropy is probability-weighted surprise.', 'The total rectangle area summarizes probability-weighted surprise across the full distribution. The scalar entropy alone does not reconstruct the distribution.'),
]


def story():
    f=json.loads(FIXTURE.read_text())['goal_03']
    cues=[Cue(b['beat_id'],b['start'],b['end'],caption,narration)
          for b,(caption,narration) in zip(f['beats'],TEXT)]
    validate_cues(cues,f['nominal_duration_seconds'])
    prior=f['states']['C']['p']; likelihood=f['observed_update']['likelihood']
    result=bayes_update(prior,likelihood)
    return {'fixture':f,'states':f['states'],'cues':cues,'prior':prior,
            'likelihood':likelihood,'posterior':result.posterior}
