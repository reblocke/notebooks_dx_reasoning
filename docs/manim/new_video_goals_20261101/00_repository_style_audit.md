# New diagnostic reasoning films: repository audit and shared implementation notes

Prepared November 1, 2026. These notes accompany two new Manim goals:

- [05: Sensitivity, specificity, and the evidence in a result](05_sensitivity_specificity_and_likelihood_ratios.md).
- [06: Log odds for evidence, probability for consequences](06_log_odds_for_evidence_probability_for_consequences.md).

## Audited source and scope

Repository: [`reblocke/notebooks_dx_reasoning`](https://github.com/reblocke/notebooks_dx_reasoning). The current video work is on `codex/mini-clinical-films`, audited at commit **`5e924fbcf6e5af4c2eb3c6be0000499489bedfcc`**. The default branch still points to the earlier notebook snapshot. Start future implementation from the current video branch or its successor, then read current repository instructions and changes before editing.

This audit inspected source, clinical revision documents, production instructions, and recorded review findings. The accepted MP4 files are absent from the tracked tree. Their output directories and detailed media review records live on the production Mac mini. The films were not replayed during this audit. The latest repository handoff records completed preview/final playback and the user's acceptance of narration clarity and timing. Recommendations below are grounded in the inspected implementation and those records; they are not a new visual or listening acceptance.

The [current animation README](https://github.com/reblocke/notebooks_dx_reasoning/blob/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc/animations/README.md) and [Mini handoff](https://github.com/reblocke/notebooks_dx_reasoning/blob/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc/docs/manim/mini_handoff.md) supersede historical production-status paragraphs. The accepted clinical cuts run **54, 48, 54, and 72 seconds**, with closing holds of 7, 5, 6, and 7 seconds. They use local narration, unlike the original long silent films.

## Connection to the existing notebook

The inspected [`display_reasoning.ipynb`](https://github.com/reblocke/notebooks_dx_reasoning/blob/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc/display_reasoning.ipynb) already defines `leaf_plot`, `odds_leaf_plot`, and `log_odds_leaf_plot`. Its probability leaf plots a family of hypothetical finding strengths, including LRs from 1/8 through 8; later examples use natural-log weights. The proposed second film develops that existing visual argument and adds an explicit consequence calculation.

Two details matter when adapting those functions. First, the notebook's `odds_leaf_plot` uses logarithmic axes. Plotting odds on logarithmic axes and plotting log odds on linear axes give equivalent geometry up to log-base scaling; they are not additional evidence updates. Second, a family of hypothetical LRs is not automatically a set of mutually exclusive outcomes of one test. The new film specifies sensitivity 60% and specificity 80%, giving a coherent positive/negative pair of 3 and 0.5. The animation should use pure helpers with explicit fixtures rather than executing notebook state.

## What to carry forward

| Observed choice or documented correction | Why it matters for these goals | Implementation requirement |
|---|---|---|
| A clinical question opens the scene; a small synthetic model supplies the numbers | The audience knows what the calculation is answering | Start 05 with a patient's positive result; start 06 with the separate questions of belief and action. Keep hypothetical test performance and utilities labeled |
| Short captions and fuller spoken explanation share a `Cue` source | The picture remains readable while speech supplies the argument | Reuse `core/cues.py` and `core/narration.py`; measure synthesized speech rather than relying only on word counts |
| Stable visual zones, dark background, Arial, restrained colors | Viewers can follow changing content without relearning the layout | Reuse `core/components.py`: target Manim `font_size` values of about 40 for titles, 25 for subtitles, 28 for captions, and 23–27 for supporting labels; inspect actual raster sizes after width fitting |
| `fade_replace` replaced distorted text morphs | Intermediate glyph deformation made otherwise correct scenes difficult to read | Fade text through zero opacity; use numerical updaters only for quantities intentionally changing continuously |
| View changes became sequential fades after overlapping numbers were found | A new coordinate system or population can otherwise look like an extra update | Clearly label resets, coordinate changes, changed payoffs, and new tests; remove obsolete objects before the new view becomes dominant |
| Tiny odds movements and 1% rectangles keep their true dimensions | Enlarged marks would change the mathematical claim | Use external labels and leaders. Never normalize arrow lengths or rescale each example separately |
| A sweep previously displayed its endpoint label too early | A printed number can contradict the geometry even when both endpoints are correct | Compute the position, label, odds, and utility from one current state; reveal endpoint-only callouts after settling |
| Whole-percent rounding produced a 101% displayed total | Rounded labels can create a false probability model | Use sufficient decimal precision, explicit approximation signs, and exact fractions in reference data |
| An initial hold was added before the rare-probability sweep | Motion is easier to interpret when the start is visible | Plan start, movement, settled result, and final hold explicitly; clear updaters at exact endpoints |
| Important qualifications were added to the sound-off recap | Speech alone can leave a misleading visual conclusion | Show the conditional question and LR-versus-posterior distinction in 05; show evidence updating versus expected consequences in 06 |

Source evidence: [clinical coordinates scene](https://github.com/reblocke/notebooks_dx_reasoning/blob/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc/animations/scenes/clinical_coordinates.py), [clinical entropy scene](https://github.com/reblocke/notebooks_dx_reasoning/blob/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc/animations/scenes/clinical_entropy_area.py), [shared components](https://github.com/reblocke/notebooks_dx_reasoning/blob/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc/animations/core/components.py), [fixed rulers](https://github.com/reblocke/notebooks_dx_reasoning/blob/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc/animations/core/rulers.py), and the clinical correction entries in the [implementation log](https://github.com/reblocke/notebooks_dx_reasoning/blob/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc/docs/manim/implementation_log.md).

The new subjects need more explanation than a single coordinate transformation. Nominal runtimes are 175 seconds for 05 and 180 seconds for 06, with concise captions and a 7-second completed closing hold. Preserve the revised films' economy of presentation. Do not fill the additional time with repeated definitions, dense prose panels, or decorative motion. A 60-second continuation of the existing coordinate film is an optional adaptation documented in 06.

## Reusable production components

| Existing path | Reuse for the new films |
|---|---|
| `animations/core/components.py` | Palette, Arial labels, legible width fitting, cards, `fade_replace` |
| `animations/core/rulers.py` | Fixed probability/log-odds mapping and truthful arrow endpoints |
| `animations/core/math.py` | Validated binary updating, probability odds, and natural-log odds |
| `animations/core/cues.py` | Contiguous unique cue IDs and short-caption/full-narration structure |
| `animations/core/narration.py` | Local speech generation, measured intervals, reuse of matching audio, aligned sidecars |
| `animations/core/voice_config.py` | Current Samantha voice and 160-words/minute starting rate |
| `animations/core/provenance.py` | Frozen source/configuration/data/audio inputs before rendering |
| `animations/scripts/review_video.py` | Strict decoding, actual video timestamps, frame sampling, contact sheets |
| `animations/scripts/finalize_film.py` | Separate frame/playback/listening gates and verified packaging |
| `scripts/mini_environment.sh` | Approved production volume, runtime/cache paths, and storage constraints on the Mini |

The verified project uses Python 3.12 and Manim CE 0.22.1 with Cairo, independently of the notebook environment. Keep its lockfile and use its documented mathtext/SVG fallback if needed. Do not install a new animation stack or an external voice service for these goals.

On the production Mini, follow the current external-volume instructions. Do not imitate its filesystem layout on another host or silently disable its storage guard. Source and numerical work can continue without the production host; recording unavailable playback or listening as pending remains mandatory.

## Integration work required before the new commands exist

The inspected runner supports goals 01–04 only. Merely adding 05 or 06 to argument parsing would be incorrect: its final dispatch branch currently selects film 04. The new prompts therefore commission explicit integration, not just a new Scene class.

1. **Register both new goals explicitly.** Add goal, cut, slug, story, scene class, duration, final hold, events, and keyframe metadata. Keep all existing registrations and behavior intact. A small metadata table is acceptable; a broad pipeline rewrite is outside scope.
2. **Keep scientific fixtures separate for each film.** Add `animations/data/test_results_fixtures.json` for 05 and `animations/data/beliefs_actions_fixtures.json` for 06. Separate files let either goal be implemented first without changing the other film's approved fixture identity. Preserve `animations/data/manim_fixtures.json` and its existing hash. Each new reference file must be included in its film's production math checks, render snapshots, and manifest. If an accepted scientific fixture later changes, create a new versioned candidate and retain the earlier producer snapshot.
3. **Respect the story split.** Current provenance expects `core/storyNN.py` and, for narrated cuts, `core/storyNN_clinical.py`. Use the first for scientific data and the second for the film's `Cue` list, or make an equally explicit dependency registration. Do not leave nonexistent inferred paths.
4. **Extend timing selection.** `clinical_timing` and `apply_clinical_timing` need the correct new events, speech intervals, transition samples, and closing hold. Never fall through to atlas timing. Selected goal metadata must determine every output field.
5. **Extend frozen-source dependencies.** Include the new scene, both story modules, new fixture file, and any cohort, leaf-plot, or decision-math modules. Verify that the snapshot imports and renders without importing the live checkout. The existing producer snapshot is an input to rendering, not a copy assembled afterward.
6. **Extend finalization's fixture identity.** The current finalizer checks and reports one legacy fixture path/hash. Make selection explicit for 05/06 and report the actual new fixture identity bound to their producer snapshots. Preserve the old guard for 01–04. Do not validate a new film against an unrelated old fixture or weaken the identity check to a current-file hash compared with itself.
7. **Retain narration reuse rules.** If the new cue source changes after narration is generated, make a clearly versioned new candidate or preserve the old candidate before regeneration. Do not change words while reusing a mismatched audio hash. Preview and final must use the same approved producer inputs.
8. **Run focused new checks and existing relevant gates.** Check new probability arithmetic, count denominators, leaf mappings, utilities, thresholds, cue timing, source isolation and fixture routing. Preserve the existing animation regressions. Notebook analyses do not need rerunning for new animation-only work.

These requirements come from the inspected [runner](https://github.com/reblocke/notebooks_dx_reasoning/blob/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc/animations/render.py), [provenance module](https://github.com/reblocke/notebooks_dx_reasoning/blob/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc/animations/core/provenance.py), and [finalizer](https://github.com/reblocke/notebooks_dx_reasoning/blob/5e924fbcf6e5af4c2eb3c6be0000499489bedfcc/animations/scripts/finalize_film.py).

## Review and completion

Use the established sequence: render the complete preview, inspect meaningful states and transitions, correct concrete issues, inspect the replacement preview, then render and review the final. The log records premature final launches that had to be superseded. The corrected preview must actually be inspected before the final launch.

Review at native 1080p and at 720p. Inspect every mathematical endpoint, selected midpoints, conditional-denominator changes, coordinate transitions, and the whole closing hold. Review the complete film at normal speed with sound. A reviewer unable to hear audio must record that limitation and rely on a genuine listening review rather than infer pronunciation from a transcript. Avoid double captions from player-generated transcription.

Retain strict version-3 video/audio receipts. A prior 54-second preview had 809 frames rather than 810, despite apparently correct audio/container duration. Check video-frame timestamps, cadence, and full duration independently of audio. Do not weaken the verifier to accommodate a short render.

For each new film, completion requires the final 1920×1080/30-fps H.264/AAC MP4, preview, narration WAV and script, SRT/VTT, actual timing, keyframes, contact sheet, QA report, bound source snapshot and manifest. Keep data and source tracked according to current project policy; retain large rendered artifacts in the established output location. Record actual review evidence and any unresolved gate. Do not call an unrendered source file, a decoded movie, or an assembly with pending listening a completed film.

## Scientific boundaries shared by both goals

The examples are deliberately synthetic. Disease labels provide a clinical frame; they do not turn invented sensitivity, specificity, or utility values into clinical estimates. Use binary mutually exclusive states for these two films. Keep disease status, test result, posterior probability, evidence strength, and preferred action visually distinct.

Log odds turn multiplication by result-specific likelihood ratios into addition. Probabilities directly weight fixed state-conditional utilities; the binary utility difference is affine in disease probability. Both coordinates represent the same beliefs and yield the same action when transformed consistently. Neither log-odds distance nor leaf-plot area is automatically information gain, clinical benefit, or the expected value of a test.

The literature references and full mathematical contracts are in the individual goals. The storyboards, timing choices, worked numbers, and proposed layout are new design decisions.

## Verification performed for these specifications

The synthetic two-by-two tables, both result LRs for each test, selected posteriors, leaf endpoints, conditional second-finding update, and utility differences were checked with independent exact rational arithmetic. Probability, odds, and log-odds decision criteria were also compared across 99 interior probabilities for each of the two utility settings. The nominal scripts were checked for contiguous cue coverage and the specified final hold. Actual synthesized speech timing remains an implementation acceptance requirement.

The Goal 06 reference plate was generated from the stated formulas and visually inspected after correcting an overflowing note and a crowded annotation. Its [PNG](assets/06_leaf_logodds_utility_reference.png), [SVG](assets/06_leaf_logodds_utility_reference.svg), and [reproducible generator](assets/make_reference_figure.py) accompany the goals. It is a mathematical design reference, not a rendered Manim scene. No new video or narration has been implemented or reviewed in this specification pass.
