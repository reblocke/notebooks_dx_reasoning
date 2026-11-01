# Goal 02: One piece of evidence, three coordinate systems

## Purpose and delivery contract

Create a standalone explanatory animation showing the **same binary Bayesian update** in probability, linear odds, and natural-log odds. Follow the package's shared runtime, design, accessibility, verification, and artifact contract. This goal specifies the mathematical content, sequence, and additional visual checks; it does not replace that shared contract.

The animation must make sense without watching another goal first. Introduce likelihood ratio and odds briefly enough that a medically literate viewer can follow the argument without knowing the previous notebook demonstrations.

- **Nominal duration:** 3 minutes 10 seconds, 190 seconds.
- **Permitted total-duration variation:** plus or minus 10%, giving a finished range of 171 to 209 seconds, or 2 minutes 51 seconds to 3 minutes 29 seconds.
- **Artifact slug:** `02_coordinate_systems`.
- **Scene class:** `OneEvidenceThreeCoordinates`.
- **Source module:** `animations/scenes/coordinate_systems.py`.
- **Required fixture key:** `goal_02` in `manim_fixtures.json`.

Deliver the standalone scene and its required review artifacts using the shared naming and output conventions. The implementation should be autonomous within these requirements. Use the simpler validated transition when an optional effect would threaten mathematical or visual clarity.

## Learning objective

After viewing, a learner should be able to explain:

1. Applying the same likelihood ratio to different starting probabilities produces different absolute changes in probability.
2. In odds, that update is multiplication by the same factor, with different absolute movements on a linear odds ruler.
3. In natural-log odds, multiplication becomes addition, so the same LR produces the same signed displacement on a shared linear ruler.
4. These are three representations of the same before-and-after beliefs. They are not three successive pieces of evidence, and equal log-odds movement does not imply equal entropy reduction or KL divergence.

## Mathematical contract

Each row represents a **separate binary starting belief** about a diagnosis `D` versus `not D`. The three initial probabilities are not three diagnoses in one multiclass differential and must never be normalized together.

A finding's likelihood ratio is `R = P(E given D) / P(E given not D)`. It compares how likely that same finding is under the two hypotheses. For `R > 0`, use:

\[
O=\frac{p}{1-p},\qquad O'=R\,O,
\]

\[
p'=\frac{Rp}{1-p+Rp},\qquad
x=\ln O,\qquad x'=x+\ln R.
\]

Here `ln` means the **natural logarithm, base e**. Log-odds coordinates and increments are in natural-log units, or nats. Do not silently substitute base-10 logarithms or bits.

The positive update is `R = 3`. Use these exact before-and-after values:

| Separate starting belief | Probability before | Probability after | Odds before | Odds after | Natural-log odds before | Natural-log odds after |
|---|---:|---:|---:|---:|---|---|
| Example 1: start 10% | `1/10 = 0.1` | `1/4 = 0.25` | `1/9` | `1/3` | `−ln 9 ≈ −2.197224577` | `−ln 3 ≈ −1.098612289` |
| Example 2: start 50% | `1/2 = 0.5` | `3/4 = 0.75` | `1` | `3` | `0` | `ln 3 ≈ 1.098612289` |
| Example 3: start 90% | `9/10 = 0.9` | `27/28 ≈ 0.964285714` | `9` | `27` | `ln 9 ≈ 2.197224577` | `ln 27 ≈ 3.295836866` |

Derived changes:

- Probability: `+0.15`, `+0.25`, and `+9/140 ≈ +0.064285714`, respectively.
- Express those as **15, 25, and approximately 6.43 percentage points**, not relative percentage increases.
- Linear odds: `+2/9`, `+2`, and `+18`, respectively, despite the same multiplication by three.
- Natural-log odds: **`+ln 3 ≈ +1.098612289` in every row**.

For the reverse demonstration, apply the reciprocal update `R = 1/3` to the displayed posteriors. It returns them to the original priors:

- Probability: `0.25 → 0.1`, `0.75 → 0.5`, `27/28 → 0.9`.
- Odds: `1/3 → 1/9`, `3 → 1`, `27 → 9`.
- Natural-log odds: the same signed movement **`−ln 3`** in all three rows.

Present this as the inverse mathematical update. Do not call `1/3` the likelihood ratio of the negative outcome of the original test. In general, a test's negative-result LR is not the reciprocal of its positive-result LR.

## Required visual structure

### Three persistent example rows

Use three horizontally aligned ruler rows labeled **Example 1: start 10%**, **Example 2: start 50%**, and **Example 3: start 90%**. Keep these labels and the row order stable through the animation. They identify separate starting beliefs about the same binary question, not different diagnoses.

Use the shared **D blue** for diagnosis-coded markers and probability elements in every row. If the complement is shown, use **not D gray** consistently. Distinguish the examples by their labels and vertical positions, not by the A/B/C diagnostic palette used in the other films. Row labels and axes can use the shared neutral text and axis styling.

Each representation occupies the main explanatory area in sequence:

1. All three rows use probability rulers.
2. All three rows use linear odds rulers.
3. All three rows use natural-log odds rulers.

Do not put probability, odds, and log odds on different rows and then compare their raw screen distances as if their units matched. The primary comparison is between the three starting beliefs **within one representation**.

Use a clearly distinguishable start marker and updated marker, such as the shared hollow start circle and filled updated diamond, with an arrow joining their coordinates. Keep D blue in every row; use marker shape and text to distinguish before from after. Row identity must remain clear from position and labels without using different diagnosis colors.

### Fixed scales within each representation

Every row in a representation must use the same:

- Numeric domain.
- Axis width and horizontal origin.
- Tick spacing and value-to-screen mapping.
- Camera framing and zoom.

Recommended default domains:

| Representation | Fixed domain for all three rows | Example major ticks |
|---|---|---|
| Probability | `[0, 1]` | `0%, 25%, 50%, 75%, 100%` |
| Linear odds | `[0, 30]` | `0, 5, 10, 15, 20, 25, 30` |
| Natural-log odds | `[−3.5, 3.5]` | Integer ticks `−3` through `3`, with the displayed domain made clear |

The log-odds maximum `ln 27 ≈ 3.2958` fits inside the recommended domain. Leave sufficient space for its callout near the right boundary.

Do not give each example its own axis limits or camera autoscaling. Equal-looking arrows must be a consequence of the coordinate calculation, not a consequence of normalizing each arrow or row separately.

### Make the small odds movement honest and readable

On the odds ruler from 0 to 30, the change `1/9 → 1/3` is genuinely small. Keep that distance small. Use an endpoint callout or separate exact-value card if two marker labels would overlap. A leader line may connect the callout to the actual coordinate. Minimum arrow-length, buffer, or tip defaults must not enlarge the movement or shift the underlying endpoints.

An inset is optional. If used, label it visibly as a magnification with its own numeric domain, keep connectors to the original positions, and do not compare its arrow length against an arrow on the full-range ruler. A numeric callout is preferable to an inset if the inset makes the comparison less clear.

## Beat-by-beat specification

The nominal schedule totals 190 seconds. Individual beat durations may be adjusted for readability, but the finished total must remain within 171 to 209 seconds. Update captions and timing metadata to the actual cut. Preserve enough dwell time to read endpoint values and notice the geometry.

| Time | Objects and action | Required explanatory content and suggested narration |
|---|---|---|
| **0:00–0:14** | Title “One piece of evidence, three coordinate systems.” Introduce three persistent example identities. Show one shared badge `LR = 3`. | “Suppose the same finding multiplies the odds of a diagnosis by three. What changes when we start at ten, fifty, or ninety percent?” Establish that these are three separate binary starting beliefs. |
| **0:14–0:31** | Reveal three aligned probability rulers on `[0,1]`. Place start markers at `0.1`, `0.5`, `0.9`. Show exact start labels and the probability-update formula, with the common LR highlighted. | “First, look at probability. Each row starts with a different belief. The evidence is the same in all three.” Keep the formula subordinate to the rulers. |
| **0:31–0:58** | Animate the updated markers to `0.25`, `0.75`, `27/28`. Retain the start markers. Reveal change labels `+15 pp`, `+25 pp`, `+6.43 pp`. Let the unequal lengths remain visible together. | “Ten percent becomes twenty-five. Fifty becomes seventy-five. Ninety becomes about ninety-six point four. The same likelihood ratio gives different probability changes.” Do not claim that 50% always gives the largest probability change; it is largest only among these three examples. |
| **0:58–1:13** | Show `odds = p / (1 − p)`. Transition the rulers and endpoint labels to the common linear odds domain `[0,30]`. Retain row identities. Use a visible bridge label such as “Same beliefs, new coordinates.” | “Now express exactly those beliefs as odds. We are changing the ruler, not adding another finding.” The before-and-after values must remain identifiable during the transition. |
| **1:13–1:43** | Replay or reveal the same update on the odds rulers: `1/9 → 1/3`, `1 → 3`, `9 → 27`. Add a `×3` tag to each row. Show a small exact-value callout for the first row. | “Every set of odds is multiplied by three. But multiplying small and large numbers gives different distances on a linear ruler.” If a marker replay is used, label it as the same update replayed in odds, not a second application of LR 3. |
| **1:43–1:59** | Show `x = ln(odds)` and `ln(O × 3) = ln O + ln 3`. Transition to aligned natural-log odds rulers on `[−3.5,3.5]`. State “natural log, base e.” | “Take the natural logarithm of the odds. Multiplication becomes addition.” Crossfade or transform between validated coordinate layouts without pretending an unlabeled intermediate axis has a familiar unit. |
| **1:59–2:30** | Place the three pairs at their exact log-odds coordinates. Animate the same update, with arrows of equal physical length on the shared scale. Show `+ln 3 ≈ +1.099` beside each arrow. Hold the completed comparison. | “Now the same evidence moves every marker by the same amount: plus the natural log of three. The equal distance is a property of log-odds coordinates.” An optional comparison bracket may reinforce equality without moving the belief markers to false coordinates. |
| **2:30–2:54** | Change the badge to “Inverse update: `LR = 1/3`.” On the same fixed log-odds rulers, move all updated markers back to their original positions with `−ln 3` arrows. Show compact probability and odds endpoint pairs returning to their starting values. | “Apply the reciprocal update, and every log-odds marker moves back by the same amount. The original probabilities and odds return as well.” Present the inverse relation, not a claim about a clinical test's negative result. |
| **2:54–3:10** | Replace the inverse-update badge with “LR 3: recap.” Hold a compact summary of the original forward update: probability gives unequal changes; odds multiply by three; natural-log odds add `ln 3`. Preserve the three row identities or show their exact before-and-after endpoint cards. Do not animate another evidence application. | “One update, three descriptions. Probability changes are unequal. Odds change by a common multiplier. Log odds change by a common additive shift.” End with a brief qualification: equal log-odds shifts do not imply equal changes in uncertainty. |

## Coordinate transitions

### Required default

Prefer a crossfade or controlled transformation between separately constructed and validated axes. Keep the row labels and before/after identities continuous while updating the axis title, tick labels, endpoint labels, and marker coordinates together.

During the transition, use the explicit message “Changing coordinates” or equivalent. Do not show a probability label on a marker that has already moved to an odds coordinate. Do not bend an axis while retaining labels that imply it is still a fixed linear ruler in the old unit.

At the settled probability, odds, and log-odds keyframes, the mapping must be exactly the declared one. The learning point must remain clear even if every optional morph is removed.

### Optional continuous coordinate morph

A continuous morph is permitted only if its coordinate map is mathematically explicit, strictly increasing on its declared interior probability domain, and exact at the three settled representation keyframes. An interior domain such as `[0.02,0.98]` avoids the divergent probability endpoints when mapping into odds or log odds.

Do not invent a warp solely because it looks smooth, and do not demand a particular interpolation formula. Intermediate frames are transitional coordinates, not another unnamed probability or information metric. Update ticks and labels from the same map as the markers.

If a morph displays the entire interior domain `[0.02,0.98]`, remember that its odds range reaches `49`; a fixed odds display of `[0,30]` does not show that whole mapped interval. Use one explicitly declared adequate domain for all rows, or retain the recommended crossfade. Do not hide the mismatch with per-row zooming or unlabeled clipping.

## Required versus optional content

### Required

- Three separate binary examples starting at `0.1`, `0.5`, and `0.9`.
- Persistent example/start-probability labels, with D blue and not D gray used consistently across rows.
- Exact LR-3 endpoints in all three representations.
- Shared scale across rows within each representation.
- A sequential probability → linear odds → natural-log odds explanation.
- Visible base-e notation and the equal `+ln 3` displacement.
- The reciprocal `1/3` update returning to the initial states.
- Explicit continuity that these are the same beliefs and same update, not compounded repeated findings.
- A concise statement separating equal log-odds movement from equal uncertainty change.
- Readable endpoint labels and truthful rendering of the small linear-odds movement.

### Optional

- A labeled magnified inset for the smallest odds movement.
- An explicitly defined and validated continuous coordinate morph.
- A compact final triptych comparing all three representations. If included, keep a shared scale within each panel and make the different panel units explicit.
- A temporary geometric bracket comparing log-odds arrow lengths, provided its illustrative role cannot be mistaken for moving the belief markers.

Do not add entropy/KL plots, a fourth coordinate system, clinical performance claims, or an additional modeling lesson to this scene. The uncertainty qualification is a boundary on the conclusion, not a new quantitative topic.

## Acceptance criteria

### Mathematical endpoints

Compute positions from the stated equations or exact equivalent fractions, not from manually selected screen coordinates. Use the full-precision `goal_02` fixtures and validate underlying values to an absolute tolerance of `1e-10` before rounding labels. The approximate decimals in the explanatory table are display references and must not become calculation inputs:

- `0.1 → 0.25`, `0.5 → 0.75`, `0.9 → 27/28` under `LR=3`.
- `1/9 → 1/3`, `1 → 3`, `9 → 27` in odds.
- Every natural-log odds difference equals `ln 3`.
- The reciprocal update returns each posterior to its original prior, each posterior odds value to its original odds, and each log-odds coordinate to its original position.
- The three rows are never normalized as a multiclass vector.

### Geometry and labels

For an axis of on-screen width `W`, the default settled keyframes must imply these displacement lengths:

- Probability: `W × (0.15, 0.25, 9/140)`.
- Linear odds on `[0,30]`: `W × ((2/9)/30, 2/30, 18/30)`.
- Natural-log odds on `[−3.5,3.5]`: `W × ln(3)/7` in every row.

The three log-odds arrows must therefore agree to rendering precision, with a target difference below one output pixel when their axis widths agree. Do not force that equality by normalizing arrow lengths independently.

All rulers in a representation share their domain, width, and horizontal origin. There is no per-row camera or axis autoscale. Confirm that the odds value 27 and log-odds value `ln 27` remain within the declared view and that their labels are not clipped. Confirm that the low-odds callout points to the actual small displacement. The three rows retain example/start-probability labels; diagnosis-coded elements use D blue and any complement uses not D gray throughout.

Displayed rounded values must distinguish `27/28 ≈ 0.9643` from certainty. Probability differences use percentage points when expressed on a percentage scale. The log base is explicit.

### Conceptual continuity and limits

- A viewer can trace each starting belief through all three coordinate systems without interpreting the transitions as new evidence.
- The same LR is not claimed to produce equal changes in probability, entropy, KL divergence, diagnostic accuracy, or clinical utility.
- The inverse update is not labeled as the negative-result LR of a clinical test.
- A continuous morph, if included, preserves monotonicity and has correct labeled keyframes; otherwise use the validated crossfade.
- The complete standalone animation lasts 171 to 209 seconds, within 10% of the nominal 190 seconds, and passes the shared review/render contract.

## Implementation decision

Use the recommended fixed domains and the crossfade/transformation approach as the default. The exact mathematical keyframes, shared scales, continuity, and legibility take precedence over a more elaborate morph. No further conceptual decision is needed before implementing this goal within the shared contract.
