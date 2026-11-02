# Goal 05: What does this test result mean?

## Implementation target

Create a complete narrated Manim teaching film about sensitivity, specificity, and result-specific likelihood ratios. The audience is clinicians and medical trainees who recognize SPIN and SNOUT but need a clearer account of how an observed result changes disease probability.

The audited base is `reblocke/notebooks_dx_reasoning`, branch `codex/mini-clinical-films`, commit [`5e924fbcf6e5af4c2eb3c6be0000499489bedfcc`](https://github.com/reblocke/notebooks_dx_reasoning/tree/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc). Read [the repository style audit](00_repository_style_audit.md), repository `AGENTS.md`, and `animations/README.md` before implementation. Work additively from the actual checkout; preserve accepted films and unrelated changes.

| Item | Required value |
|---|---|
| Slug | `05_test_results_clinical_v1` |
| Scene | `animations/scenes/clinical_test_results.py` |
| Scene class | `ClinicalTestResults` |
| Mathematical story | `animations/core/story05.py` |
| Clinical cues | `animations/core/story05_clinical.py` |
| New fixture | `animations/data/test_results_fixtures.json`, key `goal_05` |
| Output directory | `animations/output/05_test_results_clinical_v1/` |
| Nominal duration | 175 seconds; allowed total 157.5–192.5 seconds |
| Closing hold | At least 7 seconds with the completed composition stationary |
| Audio | Narrated by default; local Samantha at 160 words/minute, measured per cue |

This document specifies future implementation. It does not claim that goal 05 commands, source, fixtures, or rendered artifacts already exist.

## Conceptual approach and learning objective

Three approaches are plausible: begin with Bayes' theorem, demonstrate a denominator change in a population, or compare probability updates on rulers. Use the population approach first. It makes the clinician's question visible before introducing the algebra. Reuse two simple groups and gather the people with the observed result. Then explain the LR as a comparison of result rates. Finish with two starting probabilities receiving the same stronger LR.

The central claim is: **sensitivity and specificity describe results conditional on disease status; the clinician's post-result question concerns disease conditional on the result. Both test characteristics determine the result-specific LR, and the prior determines the resulting probability.** Clinical action additionally depends on the consequences of the decision.

SPIN abbreviates the high-specificity, positive-result, rule-in heuristic; SNOUT abbreviates the high-sensitivity, negative-result, rule-out heuristic. Demonstrate why a high value alone is insufficient. Sensitivity and specificity remain useful, and LRs re-express their information. The examples establish mathematical possibility, without suggesting that these extreme test profiles are common or empirically calibrated [1].

The viewer should retain three points:

1. Identify which conditional probability answers the question after a result.
2. Compare the observed result's rates in both disease groups to obtain its LR.
3. Apply the LR to pretest odds, then consider whether the updated probability supports the clinical action [2].

Keep the story focused. ROC curves, confidence intervals, serial tests, multiclass projection, entropy, and KL divergence are outside this film's teaching objective.

## Exact mathematical fixtures and terminology

Let `D` denote the target condition and `not D` its complement. These are mutually exclusive and exhaustive in this binary teaching model. Let `+` and `−` denote the two possible results of a specified test. Use probabilities internally on `[0,1]`, integer people for counts, and explicit `%` labels for displayed percentages. Odds and LRs are dimensionless. No logarithm is required.

$$
Se=P(+\mid D),\qquad Sp=P(-\mid\neg D),
$$

$$
LR_+=\frac{Se}{1-Sp},\qquad LR_-=\frac{1-Se}{Sp},
$$

$$
O_{\rm pre}=\frac{p}{1-p},\quad O_{\rm post}=O_{\rm pre}L,
\quad q=\frac{pL}{1-p+pL}.
$$

The two cohort demonstrations are **different tests**, each beginning with 1,000 people: 100 with the condition and 900 without it, hence `p=0.10`. Reset to this original population between demonstrations. Do not apply their LRs sequentially.

### High specificity: Test B

Set `Se=0.02`, `Sp=0.99`. The observed result is positive.

| Group | Positive | Negative | Total |
|---|---:|---:|---:|
| Condition present | 2 | 98 | 100 |
| Condition absent | 9 | 891 | 900 |
| Total | 11 | 989 | 1,000 |

$$
LR_+=\frac{2/100}{9/900}=2,\qquad
q_+=\frac{2}{11}=0.181818181818\ldots
$$

Display **10% → 18.2%** and **odds 1:9 → 2:9**. The opposite-result LR, retained for validation but unnecessary on screen, is `LR−=98/99`.

### High sensitivity: Test A

Set `Se=0.99`, `Sp=0.02`. The observed result is negative.

| Group | Positive | Negative | Total |
|---|---:|---:|---:|
| Condition present | 99 | 1 | 100 |
| Condition absent | 882 | 18 | 900 |
| Total | 981 | 19 | 1,000 |

$$
LR_-=\frac{1/100}{18/900}=\frac12,\qquad
q_-=\frac{1}{19}=0.052631578947\ldots
$$

Display **10% → 5.3%** and **odds 1:9 → 1:18**. Here the opposite-result LR is `LR+=99/98`. The displayed 5.3% is disease probability after a negative result; NPV would instead be `18/19`, approximately 94.7%.

### Stronger result, different baselines: Test C

A separate synthetic test has `Se=0.80`, `Sp=0.92`, so `LR+=10` exactly. Its unshown `LR−=5/23`. Use this coherent rate pair in the fixture even if only the positive LR appears on screen.

| Pretest probability | Pretest odds | LR+ | Post-test odds | Exact posterior | Display |
|---|---:|---:|---:|---:|---:|
| 1% | 1:99 | 10 | 10:99 | `10/109` | 9.2% |
| 50% | 1:1 | 10 | 10:1 | `10/11` | 90.9% |

The conditional test rates are held fixed in this demonstration. In clinical use, the relevant population and test definition must support that transfer; no claim of universal transportability is intended.

### Fixture and denominator contract

Store each profile's ID, description, synthetic provenance, sensitivity, specificity, observed result, prior, and applicable integer counts. Store exact expected fractions as numerator/denominator pairs and full-precision numerical references. Describe units, allowed ranges, and the absence of missing values in a short codebook in `animations/data/README.md`. Use this film's separate `test_results_fixtures.json` so implementing goal 06 later cannot change goal 05's approved fixture identity. Leave `animations/data/manim_fixtures.json` unchanged.

Compute counts and posteriors independently in tests using rational arithmetic. Full-precision comparisons use absolute tolerance `1e-10`; rounded display strings must match their stated precision. Display rounding must never feed subsequent calculations.

The decisive distinction is that **2/9 is posterior odds, whereas (2/100)/(9/900) is LR+**. Likewise, **1/18 is posterior odds, whereas (1/100)/(18/900) is LR−**. Preserve the different denominators on screen when deriving the LRs. Do not divide raw selected counts and label that quotient a likelihood ratio.

Both first tests satisfy `Se+Sp=1.01`, so they provide evidence in the usual direction. Describe the updates as doubling or halving odds, without declaring that these changes are always clinically unhelpful. Neither 18.2% nor 5.3% receives a universal action verdict. Also avoid suggesting that LR− is generally the reciprocal of LR+.

## Storyboard, captions, and narration

Use the following eight contiguous `Cue` records as the starting script. Captions are short authored text; full narration belongs in speech-aligned SRT/VTT and editable Markdown. Measure the actual Samantha speech before locking timing. Beat lengths may be redistributed within the allowed total, with scene events, cues, sidecars, and review samples updated together. Choose a frame-compatible duration for both 15-fps preview and 30-fps final.

### C01, 0–15 seconds: the post-result question

**Caption:** “What does a positive result mean?”

**Visual:** Show a positive-result card and “99% specific.” Display “SYNTHETIC EXAMPLE” and the question “Probability of the condition after this result?” Establish the 10% pretest assumption before calculating anything. Do not show 99% in the posterior position.

**Narration:** “A positive result is back. The test is ninety-nine percent specific. What is the chance of the condition now? We need to know what that percentage actually describes.”

### C02, 15–40 seconds: gather the positive results

**Caption:** “Among 11 positive results, 2 have the condition.”

**Visual:** Introduce Test B, with both rates visible. Two count boxes show 100 with and 900 without the condition. Reveal their positive counts, 2 and 9. Gather exactly 11 single-person marks into a bounded positive-result group; preserve disease-status colors. Reveal `2/(2+9)=18.2%` only after the grouping is clear. The original group counts remain available for the next comparison.

**Narration:** “Start with a thousand people: one hundred with the condition, nine hundred without it. These numbers are illustrative. This test detects only two of the hundred affected people. One percent of the nine hundred unaffected people also test positive: nine people. Among the eleven positive results, only two have the condition, about eighteen percent.”

### C03, 40–65 seconds: quantify the positive evidence

**Caption:** “LR+ = 2: a positive result doubles the odds.”

**Visual:** Briefly label “SPIN?” with “High specificity + positive ⇒ rule in?” Retain the 100 and 900 denominators while showing `(2/100)/(9/900)=2`. Then show `1:9 × 2 = 2:9` as an odds update and the corresponding `10% → 18.2%`. Use a layout that does not confuse multiplying odds with multiplying probability.

**Narration:** “Specificity asks how often people without the condition test negative. Our question is how often a positive result comes from someone with the condition. Compare the positive-result rates: two percent divided by one percent. The positive likelihood ratio is two. It doubles the odds, from one to nine to two to nine.”

### C04, 65–100 seconds: test the negative-result shortcut

**Caption:** “LR− = 0.5: a negative result halves the odds.”

**Visual:** Reset visibly to the original 100/900 population. Label “Different test: A,” sensitivity 99%, specificity 2%, and “SNOUT? High sensitivity + negative ⇒ rule out?” Reveal that heuristic label separately if needed to avoid crowding. Gather the negative results: 1 with the condition and 18 without. Show `(1/100)/(18/900)=0.5`, then `1:9 → 1:18` and `1/19=5.3%`. Keep the 19-person group distinct from the discarded positive group.

**Narration:** “Reset to the original population and consider a different test. Its sensitivity is ninety-nine percent, but its specificity is only two percent. A negative result occurs in one of the hundred affected people, and eighteen of the nine hundred unaffected people. The negative likelihood ratio is one percent divided by two percent: one half. A negative result halves the odds. One of nineteen negative results has the condition, about five percent.”

### C05, 100–125 seconds: connect the quantities

**Caption:** “Pretest odds × likelihood ratio = post-test odds.”

**Visual:** Introduce `LR+=Se/(1−Sp)` and `LR−=(1−Se)/Sp` sequentially. Highlight both contributing rates in each. Resolve to the central odds equation, followed by `probability = odds/(1+odds)`. Show only the current explanation prominently; avoid an equation wall.

**Narration:** “Sensitivity and specificity describe results conditional on disease status. Each likelihood ratio compares the probability of the observed result with and without the condition. Use both rates. Then multiply the pretest odds by the likelihood ratio, and convert back to probability. Likelihood ratios tell us how to update the odds.”

### C06, 125–155 seconds: the starting point matters

**Caption:** “The same LR can end at different probabilities.”

**Visual:** Introduce “Stronger positive result: Test C, LR+ = 10.” Show separate starts of 1% and 50%, ending at 9.2% and 90.9%. If positions or lengths encode probabilities, both rows use the same fixed 0–100% scale. Label the same multiplier on each row, while allowing different physical probability displacements. No risk-threshold bands or automatic treatment verdicts.

**Narration:** “Now consider a stronger positive result, with likelihood ratio ten. Starting at one percent, the probability becomes about nine percent. Starting at fifty percent, it becomes about ninety-one percent. The same evidence produces different final probabilities because the starting beliefs differ. The likelihood ratio alone does not tell us what action to take.”

### C07, 155–168 seconds: consolidate

**Caption:** “Question → result rates → probability update.”

**Visual:** Build three concise takeaway lines: “Ask the post-result question”; “Compare both result rates”; “Update the pretest odds.” Retain a small reminder that the numerical examples are synthetic. Complete the transition into the final composition by 168 seconds, including the final caption.

**Narration:** “Ask the right conditional question. Compare the result rates in both groups. Combine the likelihood ratio with your pretest odds to update the probability.”

### C08, 168–175 seconds: completed closing hold

**Caption:** “Whether to act depends on the clinical decision.”

**Visual:** Hold the completed takeaway composition without motion for at least seven seconds. The caption is fully visible at the hold's start; schedule its fade immediately beforehand. Speech may occupy part of this stationary hold, followed by silence. Do not truncate the final frame or append a disruptive end animation.

**Narration:** “Whether that probability is enough to act depends on the clinical decision.”

## Manim implementation and repository integration

Reuse `core/components.py`: Arial, `BG=#111827`, `WHITE=#F3F4F6`, `MUTED=#C6CFDA`, `label`, and `fade_replace`. Follow `clinical_uncertainty.py` and `clinical_coordinates.py` for short captions, stable layout, and fade-based text replacement. Disease-status colors must remain consistent when a person receives a positive or negative result. Encode result separately with grouping or a plus/minus badge. Count boxes need no area encoding; any chart that does encode counts must be proportional. Explicitly distinguish aggregate count boxes from the one-person marks in selected groups.

Use the existing mathtext/SVG fallback if a fraction needs typesetting; do not add a system TeX requirement. Start with Manim `font_size` values near 40 for titles, 28 for captions, and 23–27 for explanatory text, adjusting after review at native resolution and 720p. These are authoring parameters, not guaranteed raster pixel heights. Avoid squeezing a full table, formula derivation, and patient group into the same frame.

Keep `story05.py` free of rendering and notebook execution. Reuse suitable binary helpers from `core/math.py`, with independent rational tests. `story05_clinical.py` supplies `SLUG`, `Cue` objects, and `story()`. Derive labels, narration metadata, timing, and fixtures from these explicit sources; do not import notebook state.

The audited infrastructure currently supports goals 01–04. Implement the necessary bounded extensions:

1. Add goal `05` routing in `animations/render.py`. Goal 05 must select the narrated clinical scene by default. Preserve old goals' default behavior; explicitly supplied incompatible cuts should fail clearly. Both the documented explicit `--cut clinical` route and goal 05's default route must select this same film.
2. Extend `clinical_timing` and `apply_clinical_timing` with actual goal 05 events, endpoint samples, speech intervals, and closing-hold timing. Eliminate accidental fallthrough into goal 04's routing or timing.
3. Extend `core/provenance.py` to freeze the new fixture, both story modules, scene, and all used dependencies before rendering. The movie must run from that frozen source snapshot, with narration and sidecars bound by hash.
4. Update `scripts/finalize_film.py` to validate and record the fixture actually used by goal 05. Its existing hardcoded legacy fixture path/hash must remain valid for old films. The new film's manifest must identify its new fixture path/hash, matching preview/final producer inputs, commands, streams, review status, and source snapshot.
5. Add focused goal 05 tests and update the animation README and implementation log with actual execution evidence. Extend existing regression tests only where routing, fixture selection, or provenance changes create a concrete risk.

Use the locked animation Python 3.12/Manim environment, Cairo, preview 854×480 at 15 fps, and final 1920×1080 at 30 fps. Reuse `core/narration.py` and `voice_config.py`. Measure every generated speech interval; shorten wording or redistribute beats if it overruns. Never silently speed speech up, clip it, or replace the narrated deliverable with a silent film. Regenerate mismatched narration and sidecars through an explicit inspected workflow.

On the designated Mini, follow the existing environment and storage instructions. Maintain the monitored 5 GiB reserve and 256 MiB clinical starting headroom; render sequentially. A resource block must be reported accurately, with source and checks retained.

## Acceptance and retained evidence

The narrow checks must establish:

- All two-by-two counts, marginals, rate reconstructions, both LRs per test, and selected posteriors agree with independent exact arithmetic. Test C has the stipulated coherent rates and both exact endpoints.
- Count-based Bayes and odds-based Bayes agree. Explicit regression assertions distinguish `2/9` from `2` and `1/18` from `1/2`; none is mislabeled.
- Cue coverage is contiguous, speech fits measured windows, total duration is permitted, and the stationary completed hold lasts at least seven seconds. Sidecars match actual speech intervals.
- Goal 05 routes to narrated output and snapshots its own fixture. Tampered frozen source or fixture files, an incorrect declared fixture identity, changed packaged audio or sidecars, and mismatched preview/final producer inputs fail verification. Later edits to the live checkout cannot change or replace the captured producer inputs. Legacy goal routing and fixture identity remain intact.
- Actual Manim objects have correct selected-person counts and shared probability geometry; scene construction alone is insufficient visual evidence.

Retain keyframes for the initial question, original groups, the positive group, LR+ denominators, reset, negative group, LR− denominators, update equation, both strong-LR endpoints, and final hold. Capture each important regrouping immediately before, during, and after its transition using actual event times. Inspect every retained frame at native and 720p sizes for clipping, overlaps, misleading grouping, tiny text, and inconsistent colors.

Review the complete preview with sound before final rendering, correct defects, then review the final at normal speed with sound. Record pronunciation, intelligibility, subtitle alignment, reading time, and end-of-film behavior. Follow the repository's version-3 strict-decode and provenance gates. Frames and decoding cannot establish a listening pass. If a required review cannot be performed, record it as pending and report the precise remaining gate; never inherit the previous films' acceptance.

Retain the slug-prefixed preview MP4, `_1080p30.mp4`, narration WAV and audio receipt, narration Markdown, SRT/VTT, timing JSON, preview/final probes and strict-decode receipts, storage records, reviewed keyframes/contact sheet, QA, manifest, and frozen source snapshot. A source-only implementation is not the completed film.

## Ready-to-paste autonomous Codex goal

```text
Implement and complete Goal 05 from
docs/manim/new_video_goals_20261101/05_sensitivity_specificity_and_likelihood_ratios.md.
Read its sibling 00_repository_style_audit.md, AGENTS.md, and animations/README.md.
Use the actual working checkout; preserve unrelated work and accepted films.

Create the narrated ClinicalTestResults scene with slug
05_test_results_clinical_v1. Follow the specified exact synthetic fixtures,
eight-cue storyboard, short captions, Arial/dark style, local Samantha narration,
175-second nominal runtime with permitted ±10% adjustment, and completed final
hold of at least seven seconds. Keep LR denominators distinct from posterior
odds, reset between the two tests, and preserve the clinical action qualification.

Add the goal_05 fixture in animations/data/test_results_fixtures.json and
its codebook. Preserve animations/data/manim_fixtures.json. Add story05.py,
story05_clinical.py, and scenes/clinical_test_results.py. Extend goal routing,
clinical timing, fixture-aware finalization, and render-time source provenance
for this goal. Goal 05 is narrated by default; old goal behavior remains stable.

Implement the focused mathematical, cue/audio, routing/provenance, and actual
Manim checks. Measure synthesized speech and synchronize all timing changes.
Use the existing environment/storage guard and render sequentially. After the
new route is implemented, run:

animations/.venv/bin/python animations/render.py --goal 05 --cut clinical --quality preview
animations/.venv/bin/python animations/scripts/review_video.py --slug 05_test_results_clinical_v1 --quality preview

Review the entire preview with sound and its required keyframes; fix defects.
Then render and review the final using the same commands with --quality final.
Finalize with the extended existing finalizer, slug 05_test_results_clinical_v1,
scene clinical_test_results.py, and an actual review note. Do not invent passes.
Retain all required movies, audio, sidecars, fixtures, verification evidence,
manifest, QA, and producer-source snapshots in the specified output directory.

Continue through the authorized implementation, rendering, and review work.
Report exact artifact paths, actual runtime, checks performed, and any remaining
resource or review blocker. Do not publish or overwrite accepted artifacts.
```

## Scientific sources

**[1]** Pewsner D, Battaglia M, Minder C, Marx A, Bucher HC, Egger M. Ruling a diagnosis in or out with “SpPIn” and “SnNOut”: a note of caution. *BMJ*. 2004;329:209–213. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC487735/). DOI: `10.1136/bmj.329.7459.209`. Supports the companion-rate and post-test-probability qualifications.

**[2]** Pauker SG, Kassirer JP. The threshold approach to clinical decision making. *N Engl J Med*. 1980;302:1109–1117. [Primary-paper abstract](https://pubmed.ncbi.nlm.nih.gov/7366635/). DOI: `10.1056/NEJM198005153022003`. Supports decision thresholds determined by clinical consequences.

All numerical test profiles, counts, and baseline comparisons above are constructed teaching fixtures, calculated from the stated assumptions. They are not performance estimates taken from either paper.
