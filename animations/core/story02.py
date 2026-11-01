"""Goal 02's separate binary examples and synchronized cues."""
import json
from pathlib import Path
from .cues import Cue, validate_cues
from .math import binary_update, probability_odds, log_odds

FIXTURE=Path(__file__).resolve().parents[1]/'data/manim_fixtures.json'
TEXT=[
 ('The same finding acts on three separate starting beliefs.', 'Consider three separate binary examples, starting at ten, fifty, and ninety percent. In each, the same finding multiplies the odds by three.'),
 ('Each row uses the same probability ruler.', 'First put each starting probability on an identical ruler from zero to one. These are separate examples, not three categories of one differential.'),
 ('The same LR produces different probability changes.', 'Ten percent becomes twenty-five percent. Fifty becomes seventy-five. Ninety becomes about ninety-six point four percent. The changes are fifteen, twenty-five, and about six point four three percentage points.'),
 ('Changing coordinates does not add evidence.', 'Now describe the same beliefs using odds. Probability divided by one minus probability gives odds. Changing the ruler is not a new finding.'),
 ('Each set of odds is multiplied by three.', 'The same update is one ninth to one third, one to three, and nine to twenty-seven in odds. On a common linear scale the smallest movement is genuinely very small.'),
 ('The natural log turns multiplication into addition.', 'Take the natural logarithm, base e, of the odds. Multiplying odds by three adds the natural logarithm of three to log odds.'),
 ('Every log-odds shift has the same length.', 'On the common log-odds ruler, all three examples move by the same distance: plus natural log three, approximately one point zero nine nine.'),
 ('The inverse mathematical update returns each start.', 'Apply the reciprocal likelihood ratio, one third, as a mathematical inverse. Each marker returns to its original log odds, odds and probability. This is not a claim about a test negative result.'),
 ('Equal log-odds shifts need not mean equal uncertainty changes.', 'One forward update has three descriptions. Probability changes differ, odds multiply by three, and natural-log odds all increase by log three. Equal shifts do not imply equal changes in uncertainty.'),
]


def story():
    f=json.loads(FIXTURE.read_text())['goal_02']
    lr=float(f['likelihood_ratio'])
    examples=[]
    for fixture in f['examples']:
        p=float(fixture['p_before']);q=binary_update(p,lr)
        examples.append({'prior':p,'posterior':q,'odds_before':probability_odds(p),
                         'odds_after':probability_odds(q),'log_before':log_odds(p),
                         'log_after':log_odds(q),'inverse':binary_update(q,1/lr)})
    cues=[Cue(b['beat_id'],b['start'],b['end'],caption,narration)
          for b,(caption,narration) in zip(f['beats'],TEXT)]
    validate_cues(cues,f['nominal_duration_seconds'])
    return {'fixture':f,'examples':examples,'lr':lr,'cues':cues}
