# Goal 01: The finding that makes you less certain

## Goal and production contract

Create a self-contained mathematical animation showing how a valid Bayesian update can increase uncertainty about a diagnosis, while the finding's expected information gain before observing its outcome remains positive.

The viewer should leave able to distinguish these two statements:

1. After this particular finding, the differential is more uncertain.
2. Before its outcome was known, observing this binary finding was expected to reduce diagnostic uncertainty.

Use a completely synthetic three-diagnosis model. The film should end with the observed finding E and the unresolved posterior `(0.50, 0.25, 0.25)`. It should not reveal a true diagnosis or add a later finding that resolves the case.

**Nominal duration:** 3 minutes 30 seconds, including the final hold. The storyboard below totals 210 seconds. The finished film may vary by ±10%, from 189 to 231 seconds. Redistribute beat durations as needed for clarity, update timing metadata and captions together, and retain a completed final-frame hold of at least 7 seconds.

**Artifact slug:** `01_uncertainty_increases`.

**Scene class:** `UncertaintyIncreases`.

**Scene source:** `animations/scenes/uncertainty_increases.py`.

Inherit rendering settings, typography, palette, class colors, accessibility, caption and audio policy, software environment, and technical verification from the [shared production contract](00_shared_contract.md), particularly its rendering, visual-language, scientific-contract, and verification sections. Follow its [required deliverables](00_shared_contract.md#required-deliverables-for-each-goal) using the artifact slug above. Reuse the shared components described in its [suggested project structure](00_shared_contract.md#suggested-project-structure), including `animations/core/components.py`, where available. Do not duplicate those global requirements here.

Implement the specified mathematical states and communication goals autonomously. Layout, easing, camera moves, and narration wording may be adjusted for clarity within the stated timing and constraints. No additional clinical facts, external datasets, generative illustrations, or model calls are needed.

## Mathematical contract

### Synthetic model

The diagnosis variable D has three mutually exclusive, exhaustive categories: A, B, and C. Use abstract labels throughout. There is exactly one diagnosis in this model, but its identity is never revealed.

E is a binary finding. Its two outcomes are **E present** and **E absent**, denoted E and `not E`. Absence is an observed outcome, not missing information or an unperformed test.

| Quantity | Exact definition | Supplied decimal reference |
|---|---|---|
| Prior `p` | `(9/10, 1/20, 1/20)` | `(0.9, 0.05, 0.05)` |
| Finding likelihoods | `P(E \| A), P(E \| B), P(E \| C)` | `(0.1, 0.9, 0.9)` |
| E joint masses | `p * likelihood(E)` | `(0.09, 0.045, 0.045)` |
| `P(E)` | Sum of the E joint masses | `0.18` |
| `qE = P(D \| E)` | `(1/2, 1/4, 1/4)` | `(0.5, 0.25, 0.25)` |
| Absence likelihoods | `(0.9, 0.1, 0.1)` | `(0.9, 0.1, 0.1)` |
| Absence joint masses | `(0.81, 0.005, 0.005)` | `(0.81, 0.005, 0.005)` |
| `P(not E)` | Sum of the absence joint masses | `0.82` |
| `qnot = P(D \| not E)` | `(81/82, 1/164, 1/164)` | `(0.987804878, 0.00609756, 0.00609756)` |

The likelihood values are three conditional probabilities under different diagnoses. They are not a probability distribution over diagnoses and are not likelihood ratios. Do not normalize this likelihood row by its own sum.

The product `p * likelihood(E)` contains **joint masses** `P(D, E)`. It totals 0.18. Do not label that intermediate row a posterior or a probability distribution over diagnoses. Do not calculate or display entropy for it. Normalize by its total to obtain the posterior:

\[
P(D_i\mid E)=\frac{P(D_i)P(E\mid D_i)}{P(E)}.
\]

### Entropy and expected information

Use Shannon entropy over the three diagnosis categories, with base-2 logarithms and units of bits:

\[
H(r)=-\sum_i r_i\log_2 r_i.
\]

| Quantity | Definition | Supplied decimal reference |
|---|---|---:|
| Prior entropy | `H(p)` | `0.568995594` bits |
| Entropy after E | `H(qE)` | `1.5` bits |
| Entropy after absence | `H(qnot)` | `0.107212368` bits |
| Expected posterior entropy | `0.18 H(qE) + 0.82 H(qnot)` | `0.357914141` bits |
| Expected information gain | `H(p) - expected posterior entropy` | `0.211081452` bits |

Derive values at full precision from the exact model. Compare production calculations with the independent full-precision fixtures using the shared absolute tolerance of `1e-10`. The supplied table's abbreviated decimals are reference targets, not replacement inputs; compare against those printed references within `1e-8` bits so their final approximate digit does not dictate calculation or formatting. That looser reference check does not replace the full-precision fixture comparison. For ordinary screen labels, use approximately `0.569`, `1.500`, `0.107`, `0.358`, and `0.211` bits. Mark displayed rounded values as approximate where an equality would otherwise imply exactness.

For the observed E branch, entropy increases by approximately `0.931004406` bits. This is an increase in posterior uncertainty. The positive `0.211081452` bits is an expectation over both possible outcomes before observing which occurs.

The expectation averages **branch entropy values**:

\[
\mathbb E[H(D\mid\text{outcome})]
=0.18(1.5)+0.82(0.107212368\ldots)
\approx0.358\text{ bits}.
\]

Do not average the posterior probability vectors and then calculate entropy. That different calculation returns the prior entropy in this model and would obscure the point of this film.

## Visual grammar

- Give A, B, and C consistent class colors from the shared palette. Keep color assignment stable through every transformation and branch.
- Use a probability chart with a clearly labeled fixed 0 to 1 scale for the prior and normalized posteriors. A stacked bar or three aligned bars is acceptable if the exact proportions remain legible.
- Show the likelihoods in their own explicitly conditional row. Show the multiplication results in a separate region labeled **Joint masses: diagnosis and E**. A collecting tray or bracket can show their total of 0.18.
- Use a visually explicit normalization step labeled **Divide by P(E) = 0.18**. The destination is labeled **Posterior after observing E** and totals one.
- Display entropy only beside a normalized diagnostic distribution or as an explicitly labeled historical or expected quantity. Hide the current entropy readout while displaying or rescaling joint masses.
- Distinguish an observed trajectory from a hypothetical branch tree using labels and framing, not color alone. The branch view must visibly begin with a rewind to before the outcome was known.
- Treat movements, fills, rescaling and count transitions as illustrations between discrete computed states. They do not represent extra observations or gradual arrival of fractional evidence. A brief, readable caption can establish: **Animated transitions connect computed states.**
- Prefer meaningful labels and restrained motion. Avoid success/failure icons, a victorious diagnosis, or a green/red verdict on the entropy change.

## Scene-by-scene storyboard

Narration below is suggested. The listed scene times are nominal; redistribute them within the overall duration range and update the actual timing metadata, captions, and narration cues together. Captions must communicate the same substantive points with sound off. A mathematical label alone is not a substitute for an explanatory caption.

### Scene 1. A confident starting point

**Time:** 00:00 to 00:12. **Duration:** 12 seconds.

**Screen and motion:** Introduce A, B and C and build the prior chart to 90%, 5% and 5%. Label it **Before observing E**. Place a small persistent **Synthetic example** label. Hold the completed prior for the final few seconds.

**Caption:** “One diagnosis begins at 90%.”

**Suggested narration:** “Our starting model puts ninety percent of the probability on diagnosis A. B and C each receive five percent.”

**State:** `p`. Do not introduce a true diagnosis or a patient outcome.

### Scene 2. Define the question

**Time:** 00:12 to 00:30. **Duration:** 18 seconds.

**Screen and motion:** Retain the prior chart. Introduce a neutral finding card marked E, with two possible outcomes, **present** and **absent**. Add a compact model label: **Three exclusive diagnoses; one binary finding**. Reveal the prior entropy badge, `H = 0.569 bits`, explicitly attached to the prior chart.

**Caption:** “Entropy measures uncertainty across A, B and C.”

**Suggested narration:** “We will observe one binary finding. Before its outcome is known, uncertainty across these three possibilities is about point five seven bits.”

**State:** `p`. The entropy measure is introduced as uncertainty, without a claim about error, accuracy or decision quality.

### Scene 3. The finding fits the alternatives better

**Time:** 00:30 to 00:48. **Duration:** 18 seconds.

**Screen and motion:** Reveal a conditional likelihood row aligned with A, B and C: `P(E | A) = 0.10`, `P(E | B) = 0.90`, `P(E | C) = 0.90`. Visually connect each likelihood to its diagnosis. Mark the finding card **Observed: E present**. Keep the prior and likelihood row distinct.

**Caption:** “E is more likely under B and C than under A.”

**Suggested narration:** “We observe E. Under this model, E occurs in ten percent of A cases and ninety percent of B or C cases.”

**State:** The observed outcome is now fixed as E. The likelihood row is not a posterior distribution. The prior entropy may remain only as a clearly labeled **Before E** badge.

### Scene 4. Collect the joint masses

**Time:** 00:48 to 01:08. **Duration:** 20 seconds.

**Screen and motion:** Select the E fraction within each prior mass: one tenth of A and nine tenths of each alternative. Move or copy those selected portions into the joint-mass region. Show the three short calculations in alignment:

`0.90 × 0.10 = 0.090`

`0.05 × 0.90 = 0.045`

`0.05 × 0.90 = 0.045`

Bracket the selected masses and reveal **P(E) = 0.18**. The unselected mass may fade into the background but must not appear to become zero probability.

**Caption:** “These joint masses total 0.18. They have not yet been normalized.”

**Suggested narration:** “Multiply the prior mass by how likely E is within each diagnosis. The selected masses total point one eight, the model's probability of observing E.”

**State:** Joint masses only. Show no entropy readout for these values. If the normalization chart is already visible, leave it blank until the next scene.

### Scene 5. Normalize within the observed branch

**Time:** 01:08 to 01:28. **Duration:** 20 seconds.

**Screen and motion:** Pass the selected masses through a visible **÷ 0.18** step into the posterior chart. Scale their proportions to fill one probability unit. Settle at **A 50%, B 25%, C 25%**, with an explicit total of 100%. Keep the mapping of each colored mass easy to follow. Show the equation `qE = (0.09, 0.045, 0.045) / 0.18 = (0.50, 0.25, 0.25)` once the motion settles.

**Caption:** “Among outcomes with E, the posterior is 50%, 25%, 25%.”

**Suggested narration:** “Now condition on E by dividing by its total probability. A has half of the posterior probability. B and C share the other half.”

**State:** End at `qE`. The intermediate rescaling is illustrative. Do not introduce entropy until the normalized endpoint is established.

### Scene 6. Uncertainty increases

**Time:** 01:28 to 01:47. **Duration:** 19 seconds.

**Screen and motion:** Place a small prior chart beside the settled posterior chart. Add their entropy labels: **Before E: 0.569 bits** and **After E: 1.500 bits**. Reveal a comparison bar or meter that makes the increase apparent. If using an entropy axis, its upper bound for three diagnoses is `log2(3)`, not one bit. The displayed endpoint values must correspond to the two normalized distributions.

**Caption:** “After this finding, diagnostic uncertainty is higher.”

**Suggested narration:** “The posterior is more spread out. Its entropy is one and a half bits, higher than before we observed the finding.”

**State:** `p` and `qE` compared. The numerical readouts are endpoint quantities, not an entropy calculation on the earlier joint masses.

### Scene 7. Hold the unresolved result

**Time:** 01:47 to 02:02. **Duration:** 15 seconds.

**Screen and motion:** Return emphasis to `qE`. Keep A largest, with B and C each clearly substantial. Place **Diagnosis remains unresolved** beneath the chart. Allow several seconds with minimal motion so viewers can absorb that this is the result of the update.

**Caption:** “The finding supports a wider differential.”

**Suggested narration:** “This is the posterior supported by the model after E. The evidence leaves us with a wider differential and an unresolved diagnosis.”

**State:** `qE`. No confirmation marker, winner, or next finding appears.

### Scene 8. Rewind to the decision before the outcome

**Time:** 02:02 to 02:14. **Duration:** 12 seconds.

**Screen and motion:** Use a clear rewind cue and label **Before the outcome was known**. Move the observed E scene into a small historical thumbnail and restore the prior chart as the root of a branch tree. The rewind must read as a change of perspective, not as new evidence that reverses the posterior.

**Caption:** “Rewind: consider both possible outcomes.”

**Suggested narration:** “Now rewind to before we knew the outcome. What was observing this finding expected to do to our uncertainty?”

**State:** Prior-predictive branch view rooted at `p`.

### Scene 9. Show the two possible posteriors

**Time:** 02:14 to 02:37. **Duration:** 23 seconds.

**Screen and motion:** Open two branches from the prior:

- **E present: probability 0.18**, leading to `(0.50, 0.25, 0.25)` and **H = 1.500 bits**.
- **E absent: probability 0.82**, leading to `(81/82, 1/164, 1/164)` and **H ≈ 0.107 bits**.

Use rounded percentage labels for the second posterior, approximately 98.78%, 0.61%, 0.61%. Keep its tiny alternative masses geometrically accurate; use external labels or callouts for legibility instead of exaggerating their heights. Branch probabilities and within-branch diagnosis probabilities must have distinct labels.

**Caption:** “E spreads the posterior. Its absence concentrates it.”

**Suggested narration:** “E has an eighteen percent chance in this model. Its absence has an eighty-two percent chance and would leave a much more concentrated posterior.”

**State:** Two separately normalized counterfactual outcome posteriors. The absence branch is a possible outcome, not the outcome experienced earlier.

### Scene 10. Average the branch entropies

**Time:** 02:37 to 03:00. **Duration:** 23 seconds.

**Screen and motion:** Copy the two branch probability labels and entropy values into a weighted-average calculation:

`0.18 × 1.500 + 0.82 × 0.107212… ≈ 0.358 bits`.

The terms may become two labeled contribution segments, approximately 0.270 and 0.088 bits, that combine into the expected posterior entropy. Keep the posterior charts intact; do not merge or average their probability bars. Compare **Prior entropy: 0.569** with **Expected posterior entropy: 0.358**, then reveal the difference:

**Expected information gain ≈ 0.211 bits**.

**Caption:** “Average the branch entropies: expected uncertainty falls.”

**Suggested narration:** “Weight each possible posterior's entropy by the chance of that outcome. Expected uncertainty is about point three six bits, so expected information gain is positive.”

**State:** Expectation over outcomes, not a third realized posterior. The comparison is informational, not a statement of clinical benefit or cost effectiveness.

### Scene 11. Return to the outcome actually observed

**Time:** 03:00 to 03:15. **Duration:** 15 seconds.

**Screen and motion:** Highlight the E-present branch and label it **Our observed outcome**. Fade the absence branch and expectation calculation into clearly secondary context. Enlarge the actual posterior `(0.50, 0.25, 0.25)` with **H = 1.500 bits**. Maintain the same class colors and values as before the rewind.

**Caption:** “Our observed branch increased uncertainty.”

**Suggested narration:** “We observed the branch with higher uncertainty. A positive expected information gain does not require every possible outcome to reduce entropy.”

**State:** `qE`. Do not replace it with the expected entropy number or the posterior from the absence branch.

### Scene 12. End with the open differential

**Time:** 03:15 to 03:30. **Duration:** 15 seconds.

**Screen and motion:** Settle into a simple final frame: **Observed: E**, the posterior **A 50%, B 25%, C 25%**, and **Uncertainty: 1.500 bits**. The final sentence reads **A valid update can widen the differential.** Add **Diagnosis remains unresolved** as the secondary line. Hold the completed final state for at least the last 7 seconds.

**Caption:** “The diagnosis remains unresolved after E.”

**Suggested narration:** “A valid update can widen the differential. Here, that wider uncertainty is exactly what the stipulated model supports after E.”

**State:** End at `qE`. No answer reveal, new clue, diagnostic success icon or later certainty is permitted.

## Required claims

- All values describe a synthetic probability model with three exclusive, exhaustive diagnoses.
- Bayes updating uses the prior and the finding likelihoods. Joint masses are normalized before being interpreted as the posterior distribution over diagnoses.
- The observed E outcome raises diagnostic entropy from approximately 0.569 to 1.500 bits.
- Before observing the outcome, the probability-weighted mean posterior entropy is approximately 0.358 bits, giving positive expected information gain of approximately 0.211 bits.
- Expected information gain is an average over possible outcomes; this film's realized outcome is E.
- The model supports the posterior update. The film establishes no empirical calibration, clinical accuracy or decision utility.
- Animated transitions illustrate relationships between discrete computed states. The rewinding and branch changes are changes of viewpoint, not additional findings.

## Forbidden claims and visual implications

- Do not call `(0.09, 0.045, 0.045)` a probability distribution over diagnoses, a posterior, or an entropy-bearing intermediate state.
- Do not call `(0.1, 0.9, 0.9)` likelihood ratios or normalize it as if it were the prior or posterior.
- Do not imply that E makes B or C the most likely diagnosis. A remains the largest individual posterior category.
- Do not imply that a more concentrated distribution is automatically more accurate, or that increasing entropy is diagnostic failure.
- Do not call the observed entropy change a KL divergence, a surprisal, or the expected information gain. Those quantities are not interchangeable. No extra KL or surprisal display is needed in this film.
- Do not describe `0.358 bits` as the uncertainty of the case after E. It is the expected posterior entropy before knowing the outcome.
- Do not represent missing data as the E-absent branch.
- Do not average posterior vectors and present the entropy of that average as expected posterior entropy.
- Do not convert the absence branch into a later observation or resolve the diagnosis at the end.

## Acceptance criteria

### Mathematical checks

- Prior, likelihoods, joint masses, outcome probabilities and both normalized posteriors match the exact model above.
- The joint masses for E total 0.18; those for absence total 0.82; each normalized posterior totals one within the shared numerical tolerance.
- All entropies are calculated only from normalized diagnostic distributions using `log2`.
- Production entropy and expectation calculations agree with the independent full-precision fixtures within the shared absolute tolerance of `1e-10`.
- The separate comparison against the supplied table's abbreviated decimal references uses `1e-8` bits; it does not relax the full-precision fixture check.
- The expectation calculation uses `0.18 H(qE) + 0.82 H(qnot)`, and information gain uses prior entropy minus that expectation.

### Visual and narrative checks

- The 12 actual scene intervals are contiguous, do not overlap, and total between 189 and 231 seconds around the nominal 210-second target. Timing metadata, captions, and narration cues agree with the final cut.
- On a sound-off review, a viewer can identify the prior, the observed outcome, the joint-mass step, the normalization, the uncertainty increase, the rewind, the two outcome branches, and the expected-versus-observed distinction.
- Likelihoods, joint masses, posterior probabilities, branch probabilities and entropy values are visibly distinguished by labels and placement.
- No entropy label is associated with an unnormalized intermediate row or with the likelihood row.
- Intermediate animation frames do not introduce a claim of additional observations. Historical values remain labeled as historical when present.
- The small probabilities on the absence branch retain their correct relative sizes and have legible labels.
- Entropy comparison and branch weighting have readable holds; equations are not revealed and removed too quickly to follow.
- The final frame contains exactly the observed E posterior `(0.50, 0.25, 0.25)` and an unresolved diagnosis. The final completed frame holds for at least 7 seconds.
- Verify representative frames at the prior, joint-mass tray, normalized E posterior, branch tree, weighted entropy calculation and final hold using the shared QA workflow.

## Implementation suggestions

Calculate named states once from the exact model, then use those immutable values as animation targets. Keep probability calculations separate from visual interpolation. This avoids recomputing entropy from whatever temporary geometry happens to be on screen.

Reusable objects could include a diagnosis probability chart, a conditional-likelihood row, a joint-mass collection region, an entropy badge, and a two-outcome branch group. Reuse the same posterior chart values when returning from the branch tree to the observed result.

Keep the normalization and weighted-expectation sequences visually distinct. The first changes the denominator from all possible outcomes to the observed E branch. The second weights two already computed entropy values by outcome probabilities. The film should make both operations clear without requiring a detailed derivation of entropy itself.

Use the [shared production contract](00_shared_contract.md) for output production and required artifacts, with the slug `01_uncertainty_increases`. This specification adds no requirement for extra panels, interactive controls, clinical data, external illustrations or additional films.
