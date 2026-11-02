"""Clinical cues, measured-speech segments and the shared scene/review timeline."""
from .cues import Cue, validate_cues
from .story06 import story as mathematical_story

SLUG = '06_beliefs_actions_clinical_v1'
DURATION = 180
FINAL_HOLD = 7

CUES = [('C01',
  0,
  10,
  'Evidence changes belief. Consequences guide action.',
  "The same evidence shifts log odds equally. But what does that mean for a patient's probability, "
  'and for the next decision?'),
 ('C02',
  10,
  25,
  'A leaf plot maps each prior to two possible posteriors.',
  'A leaf plot places the starting probability on the horizontal axis and the updated probability '
  'on the vertical. This hypothetical test has one curve for a positive result and another for a '
  'negative result.'),
 ('C03',
  25,
  43,
  '10% → 25% if positive; 10% → 5.26% if negative.',
  'Start on the diagonal at ten percent. A positive result takes us to twenty-five percent; a '
  'negative result takes us to about five percent. Here, the negative likelihood ratio is one '
  'half. It is not the reciprocal of three.'),
 ('C04',
  43,
  60,
  'Both axes in log odds: the curves become parallel lines.',
  'Now express both axes as log odds. No new evidence has arrived. Each curve becomes a straight '
  'line: the starting log odds plus the log likelihood ratio. Every positive result adds the same '
  'amount.'),
 ('C05',
  60,
  77,
  'Add evidence using the LR conditional on earlier findings.',
  'A different finding now has a likelihood ratio of two, conditional on that first result. Add '
  'its log likelihood ratio and the probability becomes forty percent. Dependent findings need '
  'these conditional ratios, not automatic reuse of standalone values.'),
 ('C06',
  77,
  95,
  'Expected utility difference = p × 4 − (1 − p) × 1.',
  'For the decision, suppose acting rather than deferring is worth four utility units when disease '
  'is present and costs one when it is absent. Probabilities weight those consequences. The result '
  'is the expected utility difference between the two actions.'),
 ('C07',
  95,
  112,
  'With these consequences, act above 20%; defer below.',
  'The actions tie at twenty percent. Below that threshold, deferring has greater expected '
  'utility; above it, acting does. Our ten-percent patient crosses the threshold after a positive '
  'result. A negative result stays below it.'),
 ('C08',
  112,
  132,
  'Same log-odds increment. Different changes in expected utility.',
  'The three starting probabilities receive exactly the same log-odds increment. Yet their '
  'estimated utility differences change by different amounts. Only the first changes the preferred '
  'action. These are revisions to an estimate, not health gains caused by observing the test.'),
 ('C09',
  132,
  150,
  'Same 25% probability. Different consequences, different action.',
  'Keep the probability at twenty-five percent, but increase the cost of acting without disease '
  'from one utility unit to four. The threshold moves to fifty percent. The preferred action '
  'changes because the consequences changed, not because the evidence changed.'),
 ('C10',
  150,
  166,
  '20% ↔ odds 1:4 ↔ log odds −ln 4. Same decision.',
  'Return to the original consequences. The twenty-percent threshold is equally an odds threshold '
  'of one to four, or a log-odds threshold of minus log four. Changing coordinates preserves the '
  'expected utility and the decision.'),
 ('C11',
  166,
  173,
  'Evidence updates belief. Consequences set the threshold.',
  'Log odds add evidence. Probabilities weight consequences.'),
 ('C12',
  173,
  180,
  'Evidence updates belief. Consequences set the threshold.',
  'Either scale gives the same decision.')]

SPEECH_SEGMENTS = {'C01': ['The same evidence shifts log odds equally.',
         "But what does that mean for a patient's probability,",
         'and for the next decision?'],
 'C02': ['A leaf plot places the starting probability on the horizontal axis',
         'and the updated probability on the vertical.',
         'This hypothetical test has one curve for a positive result',
         'and another for a negative result.'],
 'C03': ['Start on the diagonal at ten percent.',
         'A positive result takes us to twenty-five percent; a negative result takes us',
         'to about five percent.',
         'Here, the negative likelihood ratio is one half.',
         'It is not the reciprocal of three.'],
 'C04': ['Now express both axes as log odds.',
         'No new evidence has arrived.',
         'Each curve becomes a straight line:',
         'the starting log odds plus the log likelihood ratio.',
         'Every positive result adds the same amount.'],
 'C05': ['A different finding now has a likelihood ratio of two,',
         'conditional on that first result.',
         'Add its log likelihood ratio and the probability becomes forty percent.',
         'Dependent findings need these conditional ratios,',
         'not automatic reuse of standalone values.'],
 'C06': ['For the decision, suppose acting rather than deferring is worth four utility',
         'units when disease is present and costs one when it is absent.',
         'Probabilities weight those consequences.',
         'The result is the expected utility difference between the two actions.'],
 'C07': ['The actions tie at twenty percent.',
         'Below that threshold, deferring has greater expected utility; above it,',
         'acting does.',
         'Our ten-percent patient crosses the threshold after a positive result.',
         'A negative result stays below it.'],
 'C08': ['The three starting probabilities receive exactly the same log-odds increment.',
         'Yet their estimated utility differences change by different amounts.',
         'Only the first changes the preferred action.',
         'These are revisions to an estimate,',
         'not health gains caused by observing the test.'],
 'C09': ['Keep the probability at twenty-five percent,',
         'but increase the cost of acting without disease from one utility unit to four.',
         'The threshold moves to fifty percent.',
         'The preferred action changes because the consequences changed, not',
         'because the evidence changed.'],
 'C10': ['Return to the original consequences.',
         'The twenty-percent threshold is equally an odds threshold of one to four,',
         'or a log-odds threshold of minus log four.',
         'Changing coordinates preserves the expected utility and the decision.'],
 'C11': ['Log odds add evidence.', 'Probabilities weight consequences.'],
 'C12': ['Either scale gives the same decision.']}

EVENTS = [{'id': 'leaf_axes', 'settled': 10.8, 'start': 10.4},
 {'id': 'leaf_positive', 'settled': 16.2, 'start': 15},
 {'id': 'leaf_negative', 'settled': 18.2, 'start': 17},
 {'id': 'positive_read', 'settled': 28.2, 'start': 27},
 {'id': 'negative_reset', 'settled': 33.4, 'start': 33},
 {'id': 'negative_read', 'settled': 35.2, 'start': 34},
 {'id': 'other_patients', 'settled': 39.4, 'start': 39},
 {'id': 'coordinate_change', 'settled': 44.2, 'start': 43.4},
 {'id': 'log_lines', 'settled': 48.2, 'start': 47},
 {'id': 'log_offsets', 'settled': 52.2, 'start': 51},
 {'id': 'sequence_axes', 'settled': 60.8, 'start': 60.4},
 {'id': 'first_finding', 'settled': 65.2, 'start': 64},
 {'id': 'second_finding', 'settled': 71.2, 'start': 70},
 {'id': 'consequences', 'settled': 77.8, 'start': 77.4},
 {'id': 'utility_line', 'settled': 85.2, 'start': 84},
 {'id': 'threshold', 'settled': 95.8, 'start': 95.4},
 {'id': 'threshold_crossing', 'settled': 101.6, 'start': 100},
 {'id': 'negative_decision', 'settled': 108.4, 'start': 108},
 {'id': 'utility_examples', 'settled': 112.8, 'start': 112.4},
 {'id': 'patient_1', 'settled': 117, 'start': 115},
 {'id': 'patient_2', 'settled': 122, 'start': 120},
 {'id': 'patient_3', 'settled': 127, 'start': 125},
 {'id': 'fixed_belief', 'settled': 132.8, 'start': 132.4},
 {'id': 'changed_cost', 'settled': 141.2, 'start': 138},
 {'id': 'reset_consequences', 'settled': 151.2, 'start': 150.4},
 {'id': 'decision_coordinates', 'settled': 158.2, 'start': 157},
 {'id': 'recap', 'settled': 166.8, 'start': 166.4},
 {'id': 'final_hold', 'settled': 173, 'start': 173}]

KEYFRAMES = [{'id': 'cue_01', 'time': 5.0}, {'id': 'cue_02', 'time': 17.5}, {'id': 'cue_03', 'time': 34.0}, {'id': 'cue_04', 'time': 51.5}, {'id': 'cue_05', 'time': 68.5}, {'id': 'cue_06', 'time': 86.0}, {'id': 'cue_07', 'time': 103.5}, {'id': 'cue_08', 'time': 122.0}, {'id': 'cue_09', 'time': 141.0}, {'id': 'cue_10', 'time': 158.0}, {'id': 'cue_11', 'time': 169.5}, {'id': 'cue_12', 'time': 176.5}]

def story():
    data = mathematical_story()
    cues = [Cue(*row) for row in CUES]
    validate_cues(cues, DURATION)
    data.update(cues=cues, speech_segments=SPEECH_SEGMENTS, events=EVENTS,
                extra_keyframes=KEYFRAMES, final_hold_seconds=FINAL_HOLD)
    return data
