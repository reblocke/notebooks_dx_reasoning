# Goal 04: An atlas of diagnostic trajectories

## Outcome

Create a standalone film showing that diagnostic reasoning can follow different valid paths through probability space, and that a clinical encounter may show only a segment of a longer path.

This is the fourth film in the requested series. It is the trajectory atlas from the brainstorming discussion, not the separate proposed film about equal entropy and different beliefs. The substitution vignette may use that distinction briefly within the atlas.

- **Nominal duration:** 4 minutes 45 seconds, 285 seconds.
- **Scene class:** `DiagnosticTrajectoryAtlas`.
- **Artifact slug:** `04_trajectory_atlas`.
- **Source module:** `animations/scenes/trajectory_atlas.py`.
- **Required inputs:** the shared contract, `goal_04` in `manim_fixtures.json`, and the atlas mathematics appendix.

Use the shared visual and delivery contract. Reuse tested probability, entropy and labeling components, but keep this film renderable without rendering the others.

## Learning objective

The viewer should be able to:

1. Read a three-diagnosis distribution as a point in a triangle.
2. Distinguish convergence, reopening, substitution and persistent ambiguity in the specified examples.
3. Explain why the appropriate direction of uncertainty change depends on the evidence.
4. Recognize that a visible encounter window can start with substantial prior information and end before diagnosis is resolved.

These are illustrative patterns, not a validated classifier of cases or a claim about the frequency of reasoning patterns in a dataset.

## Exact vignette states

All vectors are ordered A, B, C. Each row is a different synthetic vignette with its own initial prior. They are not competing algorithms applied to the same patient.

| Vignette | Initial state | After E1 | After E2 | After E3 | After E4 |
|---|---|---|---|---|---|
| Convergence | `(1/3,1/3,1/3)` | `(.55,.28,.17)` | `(.72,.18,.10)` | `(.86,.09,.05)` | `(.94,.04,.02)` |
| Reopening | `(.90,.05,.05)` | `(.78,.12,.10)` | `(.65,.20,.15)` | `(.50,.25,.25)` | `(.38,.34,.28)` |
| Substitution | `(.80,.10,.10)` | `(.65,.25,.10)` | `(.40,.50,.10)` | `(.20,.70,.10)` | `(.10,.80,.10)` |
| Persistent ambiguity | `(.40,.35,.25)` | `(.35,.30,.35)` | `(.28,.40,.32)` | `(.36,.29,.35)` | `(.33,.36,.31)` |

| Vignette | Entropy sequence, bits |
|---|---|
| Convergence | `1.584963 → 1.423180 → 1.118731 → 0.715879 → 0.382543` |
| Reopening | `0.568996 → 0.978854 → 1.278898 → 1.500000 → 1.573847` |
| Substitution | `0.921928 → 1.236160 → 1.360964 → 1.156780 → 0.921928` |
| Persistent ambiguity | `1.558872 → 1.581291 → 1.569026 → 1.578620 → 1.582232` |

The fixture file supplies fixed class-conditional likelihoods for every finding. Runtime must calculate the path from the initial prior and those likelihoods. The stored states are independent reference targets, not arbitrary animation coordinates.

The likelihoods were deliberately constructed to create these examples. The complete conditional-independent binary-observation models also specify every complementary outcome. Their branch probabilities are synthetic design quantities and should not be presented as clinical frequencies.

## Visual layout

Use one primary triangle, a compact A/B/C probability display beside it, and an entropy-versus-finding-index plot below or to the side. Keep the arrangement stable while vignettes change.

The triangle has fixed vertices:

\[
A=(0,\sqrt3/2),\quad B=(-1/2,0),\quad C=(1/2,0).
\]

The displayed point is the probability-weighted average of those vertices. Use only uniform scaling and translation for layout so the triangle remains equilateral. Labels and diagnosis colors never reorder when the leading diagnosis changes.

Use a muted entropy heat map with one fixed scale from 0 to `log2(3)=1.5849625007` bits. The uniform centroid has the highest entropy; vertices have zero entropy. The trajectories themselves stay inside the triangle with nonzero probability for every category.

Keep the active path white or another neutral high-contrast color. Distinguish the four vignette panels by their titles, not by reassigning diagnosis colors to path types. Use numbered state markers 0–4 and a small finding card E1, E2, E3 or E4 at each observed update.

The entropy plot has a fixed vertical domain `[0,1.65]` bits and horizontal ticks `0,1,2,3,4` labeled **Observed finding index**. Use actual state markers and clearly identified guide segments. Do not label that horizontal axis elapsed time.

## Scene-by-scene storyboard

| Beat | Time | Screen and motion | Required explanation |
|---|---|---|---|
| A01 | 0–15 s | Title and three small examples: a concentrated differential, an open differential and a changed leading diagnosis. | “Diagnostic encounters can begin and end with different degrees of uncertainty.” |
| A02 | 15–45 s | Build the A/B/C triangle from three labeled vertices. Show a point at the centroid with bars `(1/3,1/3,1/3)`, then at `(.8,.1,.1)` and `(.1,.8,.1)`. Keep bars synchronized. | “Every point is one probability distribution over the same three possibilities.” |
| A03 | 45–65 s | Introduce the entropy heat map and its fixed color bar. Reveal the five-position finding-index plot. Show the legend: “0: prior. 1–4: after findings. Motion illustrates transitions.” | “The background shows uncertainty. Marker zero is the initial belief; the other markers follow the four observations.” |
| A04 | 65–100 s | Run convergence. Present each E card once, move through the corresponding geometric bridge, settle at the exact state, add its entropy marker, and hold. End at A=.94. | “Here, successive findings concentrate support on A.” |
| A05 | 100–135 s | Reset visibly to a new vignette, not a new observation. Start near A at `(.9,.05,.05)` and run reopening. End near the interior at `(.38,.34,.28)`. | “Here, findings challenge the working diagnosis. The appropriate posterior becomes less certain.” |
| A06 | 135–170 s | Reset to substitution. Travel from near A toward B through the specified intermediate states. Hold the initial/final H labels side by side after the final step. | “The leading diagnosis changes. Initial and final entropy agree, even though the beliefs differ.” |
| A07 | 170–205 s | Reset to persistent ambiguity. Show modest shifts among all three possibilities. Keep every entropy marker near the top of the shared scale. End unresolved. | “The available findings can leave several possibilities plausible.” |
| A08 | 205–235 s | Arrange four equally sized summary panels with the same triangle orientation and entropy scale. Show one path and a small entropy trace per panel. Use labels Convergence, Reopening, Substitution, Persistent ambiguity. | “These are four possible realized paths, constructed under explicit probability models.” |
| A09 | 235–270 s | Enlarge substitution. First highlight states 0–2, then states 2–4, then the full 0–4 path. Keep excluded history visible but muted. A rectangular window on the entropy trace identifies the included indices. | “An encounter may show only a segment. Its starting beliefs may already include earlier evidence.” |
| A10 | 270–285 s | Return to the four path endpoints. Keep reopening and ambiguity unresolved. Final text: “Follow the evidence. The encounter need not end in certainty.” Hold at least 7 seconds. | Close on the diversity of valid paths, without ranking lower entropy as better. |

The proposed timeline totals 285 seconds. Modify pacing only within the shared allowance and update all timing/caption exports.

## Event animation within each vignette

For each finding:

1. Display the current normalized probability vector and its entropy.
2. Introduce the specified E card and label it **Observed finding**. In the main film, do not overwhelm the viewer with the full likelihood table.
3. Use `normalize(p * L**alpha)` for the illustrative movement, with a single alpha driving the triangle dot and any live probability/entropy readouts.
4. Settle at the exact Bayes posterior, add the numbered state marker and update the recorded entropy plot.
5. Hold the endpoint long enough to see which probabilities changed. Then introduce the next finding.

During motion, the live entropy badge may show the current interpolated vector's entropy, but the plotted record must distinguish actual endpoints. Default to discrete entropy markers with guides added after each observed endpoint. Do not draw a separately interpolated H curve and imply it is the entropy of a different intermediate vector.

The four displays show selected observed branches. They need not decrease entropy at each step. Goal 01 explains the separate expectation over all possible outcomes.

## Encounter-window sequence

Use substitution for all three windows; do not create new data:

| Window | Starting state | Ending state | What this selected segment shows |
|---|---|---|---|
| States 0–2 | `(.8,.1,.1)`; H≈0.921928 | `(.4,.5,.1)`; H≈1.360964 | Uncertainty increases while A loses dominance |
| States 2–4 | `(.4,.5,.1)`; H≈1.360964 | `(.1,.8,.1)`; H≈0.921928 | Uncertainty decreases as B gains support |
| States 0–4 | `(.8,.1,.1)` | `(.1,.8,.1)` | Substitution with zero net entropy change |

Keep original finding indices visible. When showing states 2–4, label state 2 **Starting beliefs already include E1 and E2**. The visible events are E3 and E4. Do not restart from the original prior or renormalize over visible categories.

Use a window or highlight on the timeline and matching path segments, rather than a camera zoom that silently changes quantitative axes. Keep all three diagnosis labels and the same heat-map range.

This is a proposed lens on encounter boundaries. It does not establish where clinicians actually begin or end their reasoning, and it does not claim a particular benchmark lacks any of these patterns.

## Narration draft

“A diagnostic encounter does not always start with an open question. Sometimes a working diagnosis is already in place. Sometimes the encounter ends before that question is resolved.

“To show these differences, put three possible diagnoses at the corners of a triangle. A point near A gives A most of the probability. The center divides probability equally. The bars beside the triangle show the exact same distribution.

“The background shows entropy. It is highest at the center and lowest at a corner. This is uncertainty, not a score for whether the reasoning is correct.

“First, convergence. The evidence repeatedly supports A. Its probability rises, and entropy falls.

“Now start with a different vignette. A begins at ninety percent. Each new finding fits the alternatives better than that confident starting belief would suggest. The differential reopens. Uncertainty rises because the evidence warrants it.

“In the third vignette, support shifts from A to B. The path passes through a more ambiguous state. At the end, the uncertainty is the same as at the beginning, but the leading diagnosis has changed.

“The fourth vignette remains ambiguous. The findings move the probabilities, yet none of the three possibilities comes to dominate. The example ends without a single confident answer.

“These are four constructed paths under explicit probability models. They show that a sequence of valid updates can have different uncertainty patterns.

“Now look at only part of the substitution path. The first segment looks like reopening: A loses support and uncertainty increases. The later segment looks like convergence: B gains support and uncertainty decreases.

“The complete path contains both. If our encounter begins in the middle, its starting probabilities already contain the earlier evidence.

“A useful account of diagnostic reasoning must describe these different starting points, transitions and stopping points. The direction of uncertainty change should follow the evidence. An encounter need not end in certainty.”

Codex may shorten or polish the narration to fit the scene timing, preserving these claims and the synthetic-model qualification.

## Required keyframes

Export the centroid and the two concentrated example states; heat-map/legend introduction; every recorded state for each vignette; the four-panel comparison; each of the three encounter windows; and the final hold.

The final contact sheet may use one row per vignette with states 0–4 and a separate window-comparison row. Keep its labels at a readable size. The montage is a QA artifact, not necessarily a film frame.

## Acceptance criteria

### Mathematical

- Every recorded posterior is recomputed from the fixed initial prior and stored class-conditional likelihoods and matches the reference fixture.
- The four paths satisfy their stated endpoint and entropy-pattern checks.
- Substitution starts with A=.8 and ends with B=.8; initial and final entropy agree, while the intermediate entropy is not constant.
- Every entropy calculation uses the same fixed A/B/C target and base-2 units.
- The triangle map and inverse recover the fixture probabilities, and all rendered path states lie inside the triangle.
- The heat-map vertices have H=0 and centroid H=`log2(3)`; all panels use that same fixed range.
- The same alpha drives all live representations in a transition.
- Window selection preserves state vectors, diagnostic categories, scales and hidden-prefix information.

### Visual and interpretive

- The triangle is explained before the audience is asked to interpret moving paths.
- Bars make the probability meaning readable throughout the first walkthrough and each path's endpoint.
- No category reorders or changes identity when the leading diagnosis changes.
- The movie clearly resets between different synthetic vignettes.
- State markers and finding indices distinguish observations from illustrative motion.
- Four-panel comparisons use matched geometry and scales; there is no automatic rescaling that exaggerates the small ambiguity movements.
- The three windows show one unchanged underlying substitution path.
- The end leaves reopening and ambiguity unresolved.
- Captions and narration do not claim that lower entropy is always better, that Euclidean path length measures information, or that the examples estimate real-world frequencies.

## Dependencies and autonomous scope

Use shared components from goals 01–03 where available. The atlas should not require all earlier films to be finished: its own introduction defines the triangle and uncertainty display.

The full model and fixture validation rules are in the atlas mathematics appendix. A renderer may cache a deterministic heat-map mesh rather than recomputing it every frame. Choose a mesh resolution that produces smooth, stable gradients at 1080p and verify boundaries; avoid a new visualization framework.

Deliver the `04_trajectory_atlas` artifact set in the shared contract. The production source, numerical fixtures, captions, manifests and rendered evidence must agree before reporting completion.
