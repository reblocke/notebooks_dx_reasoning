"""Clinical cues, measured-speech segments and the shared scene/review timeline."""
from .cues import Cue, validate_cues
from .story05 import story as mathematical_story

SLUG = '05_test_results_clinical_v1'
DURATION = 175
FINAL_HOLD = 7

CUES = [('C01',
  0,
  15,
  'What does a positive result mean?',
  'A positive result is back. The test is ninety-nine percent specific. What is the chance of the '
  'condition now? We need to know what that percentage actually describes.'),
 ('C02',
  15,
  40,
  'Among 11 positive results, 2 have the condition.',
  'Start with a thousand people: one hundred with the condition, nine hundred without it. These '
  'numbers are illustrative. This test detects only two of the hundred affected people. One '
  'percent of the nine hundred unaffected people also test positive: nine people. Among the eleven '
  'positive results, only two have the condition, about eighteen percent.'),
 ('C03',
  40,
  65,
  'LR+ = 2: a positive result doubles the odds.',
  'Specificity asks how often people without the condition test negative. Our question is how '
  'often a positive result comes from someone with the condition. Compare the positive-result '
  'rates: two percent divided by one percent. The positive likelihood ratio is two. It doubles the '
  'odds, from one to nine to two to nine.'),
 ('C04',
  65,
  100,
  'LR− = 0.5: a negative result halves the odds.',
  'Reset to the original population and consider a different test. Its sensitivity is ninety-nine '
  'percent, but its specificity is only two percent. A negative result occurs in one of the '
  'hundred affected people, and eighteen of the nine hundred unaffected people. The negative '
  'likelihood ratio is one percent divided by two percent: one half. A negative result halves the '
  'odds. One of nineteen negative results has the condition, about five percent.'),
 ('C05',
  100,
  125,
  'Pretest odds × likelihood ratio = post-test odds.',
  'Sensitivity and specificity describe results conditional on disease status. Each likelihood '
  'ratio compares the probability of the observed result with and without the condition. Use both '
  'rates. Then multiply the pretest odds by the likelihood ratio, and convert back to probability. '
  'Likelihood ratios tell us how to update the odds.'),
 ('C06',
  125,
  155,
  'The same LR can end at different probabilities.',
  'Now consider a stronger positive result, with likelihood ratio ten. Starting at one percent, '
  'the probability becomes about nine percent. Starting at fifty percent, it becomes about '
  'ninety-one percent. The same evidence produces different final probabilities because the '
  'starting beliefs differ. The likelihood ratio alone does not tell us what action to take.'),
 ('C07',
  155,
  168,
  'Question → result rates → probability update.',
  'Ask the right conditional question. Compare the result rates in both groups. Combine the '
  'likelihood ratio with your pretest odds to update the probability.'),
 ('C08',
  168,
  175,
  'Whether to act depends on the clinical decision.',
  'Whether that probability is enough to act depends on the clinical decision.')]

SPEECH_SEGMENTS = {'C01': ['A positive result is back.',
         'The test is ninety-nine percent specific.',
         'What is the chance of the condition now?',
         'We need to know what that percentage actually describes.'],
 'C02': ['Start with a thousand people: one hundred with the condition,',
         'nine hundred without it.',
         'These numbers are illustrative.',
         'This test detects only two of the hundred affected people.',
         'One percent of the nine hundred unaffected people also test positive:',
         'nine people.',
         'Among the eleven positive results, only two have the condition,',
         'about eighteen percent.'],
 'C03': ['Specificity asks how often people without the condition test negative.',
         'Our question is how often a positive result comes from someone',
         'with the condition.',
         'Compare the positive-result rates: two percent divided by one percent.',
         'The positive likelihood ratio is two.',
         'It doubles the odds, from one to nine to two to nine.'],
 'C04': ['Reset to the original population and consider a different test.',
         'Its sensitivity is ninety-nine percent,',
         'but its specificity is only two percent.',
         'A negative result occurs in one of the hundred affected people,',
         'and eighteen of the nine hundred unaffected people.',
         'The negative likelihood ratio is one percent divided by two percent: one half.',
         'A negative result halves the odds.',
         'One of nineteen negative results has the condition, about five percent.'],
 'C05': ['Sensitivity and specificity describe results conditional on disease status.',
         'Each likelihood ratio compares the probability of the observed result with',
         'and without the condition.',
         'Use both rates.',
         'Then multiply the pretest odds by the likelihood ratio, and convert back',
         'to probability.',
         'Likelihood ratios tell us how to update the odds.'],
 'C06': ['Now consider a stronger positive result, with likelihood ratio ten.',
         'Starting at one percent, the probability becomes about nine percent.',
         'Starting at fifty percent, it becomes about ninety-one percent.',
         'The same evidence produces different final probabilities',
         'because the starting beliefs differ.',
         'The likelihood ratio alone does not tell us what action to take.'],
 'C07': ['Ask the right conditional question.',
         'Compare the result rates in both groups.',
         'Combine the likelihood ratio with your pretest odds to update the probability.'],
 'C08': ['Whether that probability is enough to act depends on the clinical decision.']}

EVENTS = [{'id': 'population', 'settled': 15.8, 'start': 15.4},
 {'id': 'positive_marks', 'settled': 19.8, 'start': 19},
 {'id': 'positive_regroup', 'settled': 25.6, 'start': 24},
 {'id': 'positive_posterior', 'settled': 31.4, 'start': 31},
 {'id': 'positive_lr', 'settled': 40.8, 'start': 40.4},
 {'id': 'positive_odds', 'settled': 48.4, 'start': 48},
 {'id': 'reset_population', 'settled': 66.2, 'start': 65.4},
 {'id': 'negative_marks', 'settled': 72.8, 'start': 72},
 {'id': 'negative_regroup', 'settled': 78.6, 'start': 77},
 {'id': 'negative_lr', 'settled': 84.4, 'start': 84},
 {'id': 'negative_posterior', 'settled': 91.4, 'start': 91},
 {'id': 'general_positive', 'settled': 100.8, 'start': 100.4},
 {'id': 'general_negative', 'settled': 110.8, 'start': 110.4},
 {'id': 'general_update', 'settled': 117.8, 'start': 117.4},
 {'id': 'strong_starts', 'settled': 125.8, 'start': 125.4},
 {'id': 'strong_update', 'settled': 136, 'start': 134},
 {'id': 'strong_endpoints', 'settled': 136.4, 'start': 136},
 {'id': 'recap', 'settled': 155.8, 'start': 155.4},
 {'id': 'final_hold', 'settled': 168, 'start': 167.6}]

KEYFRAMES = [{'id': 'cue_01', 'time': 7.5}, {'id': 'cue_02', 'time': 27.5}, {'id': 'cue_03', 'time': 52.5}, {'id': 'cue_04', 'time': 82.5}, {'id': 'cue_05', 'time': 112.5}, {'id': 'cue_06', 'time': 140.0}, {'id': 'cue_07', 'time': 161.5}, {'id': 'cue_08', 'time': 171.5}]

def story():
    data = mathematical_story()
    cues = [Cue(*row) for row in CUES]
    validate_cues(cues, DURATION)
    data.update(cues=cues, speech_segments=SPEECH_SEGMENTS, events=EVENTS,
                extra_keyframes=KEYFRAMES, final_hold_seconds=FINAL_HOLD)
    return data
