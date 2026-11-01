# Shared production contract for four diagnostic reasoning films

## Mission and completion boundary

Produce four finished, mathematically verified Manim films:

1. The finding that makes you less certain.
2. One piece of evidence, three coordinate systems.
3. Entropy as an area you can see.
4. An atlas of diagnostic trajectories.

The audience is clinicians and quantitative medical researchers who understand probability but may not know log odds, entropy or the probability simplex. Each film must work by itself and also use the same visual language as the other three. The goal is to make the mathematical transformation understandable through motion.

Complete the local implementation, preview renders, numerical checks, visual revision and final exports. A plan, Python scene file, passing numerical tests, or still-image storyboard alone is not completion. Do not add further films, a web application, a notebook redesign, an interactive dashboard, or new clinical estimates.

## Read before implementation

Read the current repository's `AGENTS.md`, current working-tree status and this entire contract, then the selected goal specification and the supplied numerical fixtures. The conceptual source is `reblocke/notebooks_dx_reasoning`. The audited source snapshot was `c87a46b70cb10898397bc931e266fef1c1e2f0c0`, but implementation must work with the current checkout and preserve ongoing notebook repairs.

Build in an additive `animations/` directory or the repository's existing equivalent. If another Codex task is changing the notebooks, use an isolated branch/worktree where available. Do not overwrite, reset, revert, stage or commit unrelated changes. Reuse a corrected mathematical function only if its contract matches this specification and its independent checks pass. Do not execute notebooks to obtain hidden state or import their widget globals.

These films use known, explicit generative examples. They do not depend on the disputed OVR fitting objective and do not need a numerical projection optimizer.

## Decisions Codex may make autonomously

Codex may choose internal classes, component boundaries, animation easing, label placement, readable font substitutions, modest palette adjustments, local dependency tooling and compatible rendering workarounds. It may redistribute beat durations and adjust the total runtime within ±10% of each goal’s nominal duration to improve reading time. Update captions, narration cues and timing metadata together. Preserve all required beats, contiguous timing, and any minimum final hold; the goal-specific time tables are the initial cut, not exact-duration gates.

Preserve the specified probability models, units, required comparisons, narration claims, endpoint values, evidence-event boundaries and fixed comparison scales. A visual preference is not a reason to change a fixture, omit an unresolved endpoint or introduce a new likelihood ratio.

Use the defaults below without asking routine design questions. Record meaningful implementation deviations in the completion report. If a genuine mathematical inconsistency is found, document it precisely, continue unaffected work and do not silently substitute a different scientific claim.

## Rendering and environment defaults

| Item | Required default |
|---|---|
| Library | Manim Community Edition, not ManimGL |
| Initial version target | Manim CE 0.22.1, the stable documentation version checked on October 30, 2026; pin the actual compatible version used |
| Runtime | A separate animation environment, initially Python 3.12; preserve the notebook project's existing runtime and dependencies |
| Renderer | Cairo / CPU-oriented rendering; no GPU requirement |
| Master | MP4, H.264-compatible playback, 1920×1080, 30 frames/s, 16:9 |
| Preview | Approximately 854×480, 15 frames/s |
| Audio | Complete silent film with readable burned-in explanation captions; narration script and timed subtitle sidecars supplied |
| Optional narration | An already available, permitted local voice can be added, but it is not a completion requirement |
| Assets | Original vector geometry, typography and mathematical displays |
| Reproducibility | Pin direct dependencies and record the resolved render environment; seed any incidental randomness |

Use an optional animation dependency group/project rather than adding Manim to the main Binder requirements. Prefer the existing environment manager; `uv` is a suitable default. Check actual fonts, mathematical text rendering and video encoding with one small preflight render.

Use `MathTex` where the environment supports it. If LaTeX is unavailable, render the small set of equations with a tested local math-text/SVG route or carefully grouped Unicode text. Preserve fractions, subscripts, minus signs and log bases. A documented local fallback is acceptable; installing a large system-wide toolchain is not a prerequisite for this project.

The default film is silent and captioned. Do not stall the project waiting for a voice recording or call an external voice/model service. Narration can be added later from the supplied script without changing the mathematics.

## Suggested project structure

Equivalent structures are acceptable if the documented commands and deliverables remain clear.

| Path | Purpose |
|---|---|
| `animations/README.md` | Installation, preflight, render, verification and output instructions |
| `animations/pyproject.toml` and environment lock | Isolated, reproducible animation dependencies |
| `animations/manim.cfg` | Shared rendering defaults |
| `animations/render.py` | One entry point for a selected goal or all goals; resolves paths from its own location |
| `animations/core/math.py` | Pure probability, odds, entropy and geometry functions |
| `animations/core/style.py` | Colors, fonts, layout bounds and shared timing conventions |
| `animations/core/components.py` | Reusable rulers, probability displays, captions, meters and event markers |
| `animations/data/manim_fixtures.json` | Copy of the supplied immutable scientific fixtures |
| `animations/scenes/uncertainty_increases.py` | `UncertaintyIncreases` |
| `animations/scenes/coordinate_systems.py` | `OneEvidenceThreeCoordinates` |
| `animations/scenes/entropy_area.py` | `EntropyAsArea` |
| `animations/scenes/trajectory_atlas.py` | `DiagnosticTrajectoryAtlas` |
| `animations/tests/` | Focused checks of production calculations, fixtures and display mappings |
| `animations/scripts/` | Frame extraction, contact-sheet and media-inspection utilities as needed |
| `animations/output/` | Local renders, captions, stills and QA artifacts, normally ignored by Git |

Document commands executable from the repository root. A suitable interface is:

```bash
uv run --project animations python animations/render.py --goal 01 --quality preview
uv run --project animations python animations/render.py --goal all --quality final
uv run --project animations python -m pytest animations/tests
```

These are the proposed runner interface, not claims about existing repository commands. Implement the interface or document an equally simple alternative. Each goal must be renderable alone, without rendering the others.

## Shared visual language

| Meaning | Encoding |
|---|---|
| Diagnosis A | Blue, initial value `#56B4E9`, always labeled A |
| Diagnosis B | Orange, `#E69F00`, always labeled B |
| Diagnosis C | Purple, `#CC79A7`, always labeled C |
| Binary hypothesis D in goal 02 | Blue; its complement is gray; the three rows are separate examples |
| Background | Deep navy, initially `#111827` |
| Main text | Off-white, `#F3F4F6` |
| Secondary text | Light gray, initially `#B9C1CE` |
| Active event or movement | White outline/arrow; shape and label carry meaning |
| Entropy heat map | One muted sequential palette with a labeled fixed numeric scale |
| Before / after | Hollow circle / filled diamond, plus text labels |

Use color to preserve identity, not to label high entropy as failure or low entropy as success. Do not rely on color alone. Avoid decorative particles, mascots, camera spins, background music and persistent logos.

Use one main claim per beat. A useful initial text hierarchy in Manim is title 44–48, body/captions 30–34, equation 36–40 and labels 26–30. Verify the final raster output at full size and at a 720p viewing scale. Smaller secondary labels are acceptable only where they remain legible.

Use a 14.222×8 scene frame or its exact 16:9 equivalent. Keep essential objects approximately within `x∈[-6.35,6.35]` and `y∈[-3.5,3.5]`. Reserve the upper band for the current claim and the lower band for captions. Keep axes and moving data out of the caption band. The goal-specific layout may adapt these bounds without clipping.

Short captions must explain the scene without audio. Use at most two lines at once and allow adequate reading time, usually at least three seconds for a short statement and longer for equations. Do not print full narration paragraphs over a moving figure.

## Scientific contract

### Fixed diagnostic target

Goals 01, 03 and 04 use the same three abstract categories A, B and C, treated as mutually exclusive and exhaustive. They are not a claim that real patients can have only one disease. Category count and definitions stay fixed during every entropy comparison.

Goal 02 consists of three separate binary examples. Its initial probabilities `0.1,0.5,0.9` must never be normalized together or presented as one differential.

Every fixture is deliberately synthetic. Keep that identification in the opening or a persistent short footer. Do not add clinical disease names or infer clinical sensitivity/specificity without a separately supplied source.

All observed diagnostic updates retain positive prior support for every category. Do not simplify a 90% or 94% label to 100% for dramatic effect: ordinary Bayes cannot restore positive probability to a category assigned exactly zero prior probability. The atlas may still show triangle vertices as static geometric reference points.

### Quantities and units

Use natural logs for log odds and log LRs in goal 02. Use base-2 logs for surprisal, entropy and any KL values. Every axis, meter and formula identifies its quantity and unit.

```text
odds(p) = p / (1-p)
logit(p) = ln(p) - ln(1-p)
binary_update(p, LR) = p*LR / ((1-p) + p*LR)
posterior(pi, L)[j] = pi[j]*L[j] / sum_k(pi[k]*L[k])
surprisal_bits(p) = -log2(p), for p > 0
entropy_bits(p) = -sum_j p[j]*log2(p[j]), with the zero term defined by its limit
```

Only normalized probability distributions enter entropy. Joint masses `pi[j]*L[j]` and unnormalized scores are not posteriors. A sum-to-one check alone is not enough: require finite, nonnegative, one-dimensional vectors with the intended category order.

For internal fixture comparisons, use absolute tolerance `1e-10` unless a documented platform limitation requires a slightly wider numerical tolerance. Display rounding never feeds back into computation.

### Motion is not an extra observation

Evidence arrivals occur at explicitly labeled discrete events. Between endpoint states, motion may illustrate the change. Use the normalized geometric bridge

\[
p_j(\alpha)=
\frac{p_j(0)L_j^{\alpha}}
{\sum_k p_k(0)L_k^{\alpha}},
\qquad 0\leq\alpha\leq1,
\]

when a normalized distribution must be available at every animation frame. Compute bars, point position and entropy from that same vector.

This bridge is an illustration, not evidence that the finding arrives in fractional observations or that wall-clock clinical time passes continuously. Mark discrete observed states clearly. The entropy timeline in goal 04 uses actual step values; any connecting segments are guides between observations.

In the joint-mass teaching scene of goal 01, display the exact unnormalized masses separately instead. Hide the current entropy indicator until normalized probabilities are restored. If a prior-entropy badge remains visible as a reference, label it “Prior entropy, before E”; never attach a normal current-entropy readout to the unnormalized masses.

### Interpretation boundaries

An individual result may raise entropy. Expected entropy reduction is a probability-weighted average over possible outcomes under a stated model. Neither an entropy decrease nor a positive KL divergence certifies truth or clinical usefulness. A reciprocal LR used to reverse a mapping is not automatically the LR of the complementary outcome of the same test.

The atlas paths are selected synthetic branches. They illustrate possible dynamics; they do not estimate the prevalence of such dynamics, compare methods fairly, or establish the composition of existing benchmarks.

## Required deliverables for each goal

Use the slug defined in that goal. For each, deliver:

| Artifact | Requirement |
|---|---|
| `<slug>_1080p30.mp4` | Complete final film with readable burned-in explanatory captions |
| `<slug>_preview.mp4` | Low-cost preview used during review |
| `<slug>.srt` and `<slug>.vtt` | Timed narration/description subtitles aligned to the final cut |
| `<slug>_narration.md` | Complete editable narration, with scene and cue IDs |
| `<slug>_timing.json` | Actual beat/event/caption start and end times |
| `<slug>_keyframes/` | At least the required mathematical states and the final frame as PNGs |
| `<slug>_contact_sheet.png` | Labeled scene/cue keyframes for rapid visual review |
| `<slug>_qa.md` | Numerical checks, visual issues found and corrected, any remaining limitation |
| `<slug>_manifest.json` | Actual Python/Manim versions, renderer, resolution, FPS, duration, fixture hash and command |

SRT and VTT contain the full narration/description track. The MP4 contains only the shorter explanation captions; do not burn both tracks into the same frame or automatically overlay both. Keep these tracks distinct: the film should remain readable with sound off, while the sidecar can carry fuller narration for a later recorded voice. Generate both from a common timing/cue source so they cannot drift independently.

Output paths and binary-commit policy may follow the current repository's conventions. Do not commit caches, virtual environments or large generated videos by default. Local completed exports remain required.

## Verification and stopping criteria

1. Run the supplied fixture oracle independently. Then test the production mathematical functions against the fixtures; the oracle passing by itself does not validate scene code.
2. Render a small preflight scene to verify fonts, equations, colors and video encoding.
3. Render the selected film at preview quality. Extract each prescribed keyframe and at least one mid-transition frame per major transformation.
4. Inspect those frames and view the preview at normal speed where playback is available. Correct clipped labels, ambiguous scales, overlapping captions, distracting motion and insufficient reading time.
5. Render the complete final film. Check duration, resolution, frame rate and the opening/final frames using available media inspection tools. Sample the final at all key mathematical states and check subtitle timing.
6. Record the actual checks and deviations. Run `git diff --check` for the intended source changes. Report completion with file locations and any concrete unresolved item.

Numerical gates include normalized posteriors, endpoint recovery, correct log bases, the specified entropy values, correct branch weights and consistent geometry. Visual gates include fixed comparison scales, readable small probabilities, labels that follow the right objects and no normal-looking display of an undefined quantity.

Use tests that address these mathematical and rendering risks. Do not write tests that merely repeat static narration or assert every prose sentence. After the stated numerical and visual gates pass, stop expanding the scope.

## Sources

- [Manim Community documentation](https://docs.manim.community/en/stable/index.html).
- [Manim configuration and output settings](https://docs.manim.community/en/stable/guides/configuration.html).
- [ValueTracker](https://docs.manim.community/en/stable/reference/manim.mobject.value_tracker.ValueTracker.html) and [TransformMatchingTex](https://docs.manim.community/en/stable/reference/manim.animation.transform_matching_parts.TransformMatchingTex.html).
- [Foundational reasoning notebook, audited source](https://github.com/reblocke/notebooks_dx_reasoning/blob/c87a46b70cb10898397bc931e266fef1c1e2f0c0/display_reasoning.ipynb).
- [Log-odds applet, audited source](https://github.com/reblocke/notebooks_dx_reasoning/blob/c87a46b70cb10898397bc931e266fef1c1e2f0c0/log_odds_evidence_applet.ipynb).
- [Goodfellow, Bengio and Courville, probability and information theory](https://www.deeplearningbook.org/contents/prob.html).
- [MIT Information and Entropy, conditional uncertainty and mutual information](https://ocw.mit.edu/courses/6-050j-information-and-entropy-spring-2008/80c7258fd6bc5780797975eabb6fd747_MIT6_050JS08_textbook.pdf).

These sources support the tools and mathematical definitions. The storyboards, timing, palette and synthetic fixtures are specified design choices.
