# Goal 03: Entropy as an area you can see

## Outcome

Create a standalone film showing that entropy is the total area of probability-weighted surprisal rectangles. A learner should see why an unlikely outcome can have high surprisal but contribute little to expected uncertainty, and why the full distribution is needed to calculate entropy.

- **Nominal duration:** 3 minutes 30 seconds, 210 seconds.
- **Scene class:** `EntropyAsArea`.
- **Artifact slug:** `03_entropy_area`.
- **Source module:** `animations/scenes/entropy_area.py`.
- **Required inputs:** the shared contract and `goal_03` in `manim_fixtures.json`.

Use the shared render, caption, accessibility and completion contract. This is an explanatory geometry film, not an estimator or a clinical demonstration.

## Three take-home points

1. A category's surprisal is `-log2(p)`; its probability and surprisal are different quantities.
2. Its entropy contribution is probability times surprisal.
3. Entropy sums those contributions across the fixed diagnostic categories.

Do not identify surprisal with log odds, log LR or the information supplied by a particular test result. Do not claim that the scalar entropy uniquely determines the probability distribution.

## Mathematical objects

For each category `i`, construct a rectangle whose data-space width is `p_i` and height is `s_i=-log2(p_i)`. Place the three rectangles consecutively on one shared cumulative-probability axis:

```text
x_left(A) = 0
x_left(B) = p_A
x_left(C) = p_A+p_B
width(i) = p_i
height(i) = surprisal_bits(p_i)
area(i) = p_i * surprisal_bits(p_i)
sum(widths) = 1
sum(areas) = entropy_bits(p)
```

The common horizontal unit is probability, dimensionless. The common vertical unit is bits of surprisal. A rectangle's data-space area is therefore a contribution in bits. Pixel area is proportional to it through the same fixed horizontal and vertical scale factors for every rectangle.

### Required distributions

| State | A, B, C | Surprisal of A | Entropy contribution of A | Total entropy |
|---|---|---:|---:|---:|
| R0 | `(.50,.25,.25)` | 1.000000 | 0.500000 | 1.500000 |
| R1 | `(.10,.45,.45)` | 3.321928 | 0.332193 | 1.368996 |
| R2 | `(.01,.495,.495)` | 6.643856 | 0.066439 | 1.070793 |
| U | `(1/3,1/3,1/3)` | 1.584963 | 0.528321 | 1.584963 |
| C | `(.90,.05,.05)` | 0.152003 | 0.136803 | 0.568996 |

Use unrounded numerical fixtures internally. Every distribution remains normalized. R0 is the initial worked example. Introduce R1 as a separate hypothetical example, then sweep continuously from R1 to R2. These are comparisons of hypothetical distributions, not a sequence of clinical observations.

The state ID `C` is an internal mnemonic for the concentrated example. On screen, call that state **Concentrated prior** or `p`; do not use it as a label that could be confused with diagnosis C.

## Layout and visual geometry

Use a fixed rectangle plot spanning cumulative probability 0 to 1 and surprisal 0 to 7.2 bits. Its aspect ratio may be chosen for legibility, but its x and y scales remain fixed during all quantitative comparisons. A narrow 1% rectangle must remain 1% of the total plot width; do not enlarge it to fit its label.

Place diagnosis names, probabilities and narrow-rectangle labels outside the rectangles, with short leader lines when needed. Keep a compact calculation panel to the right or above the plot and a total-entropy indicator below it. Clearly distinguish the rectangle height, `s_i`, from the total-entropy meter, `H`. The latter ranges from 0 to `log2(3)`.

Use the same A/B/C colors as goals 01 and 04. All rectangles use the same opacity and line weight, so color intensity does not imply an additional numerical variable.

## Scene-by-scene storyboard

| Beat | Time | Screen and motion | Required explanation |
|---|---|---|---|
| E01 | 0–15 s | Show R0 as a simple horizontal probability strip with widths 50%, 25%, 25%. Keep the total-width bracket labeled 100%. | “A probability distribution tells us how belief is divided among the possibilities.” |
| E02 | 15–40 s | Select A. A one-bit vertical ruler appears. Reveal a full-height outline and then the fill of A's already-correct rectangle, width 0.5 and height 1. Label the two dimensions separately. | “At probability one half, the surprisal is one bit. This height is surprise if A is revealed.” |
| E03 | 40–65 s | Reveal B and C at their correct heights of 2 bits and widths of 25%, using opacity rather than stretching their heights. Reveal `s_i=-log2(p_i)` after the geometry is visible. | “Less likely categories have greater surprisal. Width and height now encode different quantities.” |
| E04 | 65–90 s | Highlight A's base and height, then its filled area. Show `0.50×1=0.50` bits. Repeat briefly for B and C: `0.25×2=0.50` each. | “Entropy weights each possible surprise by how often that outcome is expected.” |
| E05 | 90–115 s | Highlight the three areas together. Their numerical contributions combine in a compact sum, yielding 1.50 bits. Add the general formula only after the sum. | “The total area is the expected surprise across the whole distribution.” |
| E06 | 115–145 s | Introduce R1 with a labeled crossfade: “A separate example: A starts at 10%.” Then mark a hypothetical distribution sweep and vary R1→R2 continuously. A gets narrower and taller; B and C widen and shorten. Keep the scale fixed and show value cards for A's probability, surprisal and area. | “From ten percent to one percent, making A rarer makes it more surprising. But that larger surprise is weighted by a much smaller probability.” |
| E07 | 145–165 s | Hold R2. Display a three-row comparison of A at 50%, 10%, 1%, using the fixture values. Highlight height increasing while area decreases across these selected examples. | “A rare outcome can be highly surprising and still contribute little to expected uncertainty.” |
| E08 | 165–180 s | Crossfade between separately labeled U and C examples, each with already-correct geometry: U has three equal rectangles; C has one broad low rectangle and two narrow tall ones. Show H=1.585 and H=0.569 on the fixed meter. | “For these fixed categories, the uniform distribution has the greatest entropy.” |
| E09 | 180–200 s | Introduce a synthetic finding E locally. Show prior `p=(.9,.05,.05)` and likelihoods `(P(E given A), P(E given B), P(E given C))=(.1,.9,.9)`. Apply the update to R0 while the probability strip and rectangles change together; show H=0.57→1.50. | “This finding increases uncertainty because it redistributes belief more evenly across the same possibilities.” |
| E10 | 200–210 s | Hold the normalized R0 rectangles and the labeled formula. Keep the final card simple: “Entropy is probability-weighted surprise.” | End on a readable stable frame. |

All boundaries are contiguous and total 210 seconds. Modest timing adjustments follow the shared contract. The final event timing and captions must match the rendered cut.

## Detailed motion rules

For the R1→R2 distribution sweep, interpolate A's probability monotonically from 0.10 to 0.01 and assign B=C=(1-A)/2. Recompute all widths, heights, areas and labels from that single normalized vector. The scene is a parameter sweep, so it does not need an evidence likelihood model. The change from R0 to R1 is a labeled crossfade between examples, with no interpolated numerical claim.

Do not claim that `-p*log2(p)` decreases whenever p decreases. It reaches its maximum at `p=1/e`. A continuous R0→R1 sweep would first increase A's contribution, and total entropy would reach its maximum when A passes through 1/3. The required R1→R2 sweep avoids those turning points. The E07 table compares only the selected endpoints.

For E09, use goal 01's explicit likelihood vector `(.1,.9,.9)` and its normalized geometric bridge. Show that this beat is an observed-finding update, unlike the earlier distribution sweep. Only the endpoints correspond to the before/after observation.

Do not animate widths and heights independently and then use their intended endpoints to drive the area meter. At every displayed frame, the geometry and printed value must agree. Do not use a generic shape morph if it breaks this relationship.

Do not stack, pour or reshape the rectangles while calling the operation area-preserving unless the transformation actually preserves their area throughout. A bracket and a numerical sum are sufficient.

Keep the narrow A label outside the 1% rectangle. Make the tiny width visible through a high-contrast outline and a leader line, not through artificial widening.

## Narration draft

“Start with three possible diagnoses. Half of the probability belongs to A. The other half is shared equally by B and C.

“Suppose the final diagnosis were revealed. Learning A would be less surprising than learning either B or C, because A was more likely to begin with.

“We can measure that surprise. Take the negative base-two logarithm of the probability. A probability of one half gives one bit. A probability of one quarter gives two bits.

“Now give each possibility a rectangle. Its width is its probability. Its height is the surprise of that outcome. The area combines the two.

“For A, one half times one bit contributes half a bit. B contributes another half, and C contributes another half. Add the areas and we obtain one and a half bits.

“That sum is entropy: the surprise we expect before we know which diagnosis will be revealed.

“Now take a separate example in which A has ten percent of the probability. Watch what happens as it falls to one percent. Its rectangle gets taller, but it also gets narrower. At one percent, A would be very surprising if it occurred. Yet it contributes only about seven hundredths of a bit to expected uncertainty.

“The height describes one possible outcome. The total area describes uncertainty across the distribution.

“When the three possibilities are equally likely, total entropy is greatest. When one dominates, total entropy is smaller, even though the remaining rare outcomes would each be surprising.

“Now observe a synthetic finding that is unlikely under A and more likely under B or C. The probabilities move from ninety, five and five percent to fifty, twenty-five and twenty-five. The total rectangle area increases.

“We became less certain because the evidence changed how belief was distributed. Entropy gives that change a precise meaning: probability-weighted surprise.”

This script is editable for timing and clarity without changing the mathematical claims. Do not narrate every decimal.

## Required keyframes

Export E01's probability strip; E03's labeled dimensions; E04's A contribution; E05's sum; E06 at R1 and R2; E07's comparison; E08 at U and C; E09's endpoint; and the final E10 frame. Include a mid-sweep frame with its actual numeric vector in the QA report.

## Acceptance criteria

### Numerical

- Each rectangle width equals its category probability on a common scale, and widths sum to one.
- Each height equals `-log2(p_i)` on the fixed vertical scale.
- The displayed areas and total match independent fixture values within `1e-10` internally and the displayed rounding externally.
- At R2, the A width is 0.01, height approximately 6.643856 and area approximately 0.0664386 bits.
- The uniform distribution has H=`log2(3)` and a point-mass limit has H→0.
- If zero support is exercised in tests, its entropy term is exactly 0 by the limit; do not render an infinite rectangle. The required film itself uses only positive probabilities.
- E09 ends at `(.5,.25,.25)` and H=1.5 after the specified likelihood update.

### Visual and conceptual

- A learner can identify probability, surprisal and entropy contribution from the displayed dimensions and labels.
- No rectangle is widened to improve readability, and no comparison silently changes axis scale.
- Height is never labeled log odds or log LR.
- The formula appears after the area relationship is visible.
- The R1→R2 sweep is not presented as additional evidence arriving; R0→R1 is a clearly labeled switch between examples.
- The end of the film does not imply that H alone can reconstruct the full probability distribution.
- The captioned film is understandable without narration and meets the shared final-export checks.

## Dependencies and autonomous scope

Reuse shared probability displays and entropy calculations. Reuse the goal 01 finding fixture, but render independently if that film is unfinished. Do not expand this goal into coding theory, differential entropy, a clinical data analysis or a new interactive control panel.

The required deliverables are the `03_entropy_area` artifacts in the shared contract, plus focused source tests of the rectangle geometry-to-value mapping.
