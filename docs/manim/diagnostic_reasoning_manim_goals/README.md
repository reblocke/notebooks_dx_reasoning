# Diagnostic reasoning: autonomous Manim production goals

**Prepared October 30, 2026.** This package specifies four finished explanatory films for implementation by Codex. It contains storyboards, narration, immutable synthetic fixtures, focused acceptance criteria and a runnable fixture oracle. It does not contain rendered films or an implementation of the Manim scenes.

## The four goals

| Goal | Nominal duration | Main visual | Required conclusion |
|---|---:|---|---|
| [01: The finding that makes you less certain](specs/01_uncertainty_increases.md) | 3:30 | Prior, likelihood, joint mass, posterior, then a two-outcome branch tree | A valid observed update can raise entropy while expected information gain remains positive |
| [02: One piece of evidence, three coordinate systems](specs/02_coordinate_systems.md) | 3:10 | The same update on probability, odds and log-odds rulers | A shared LR gives a shared additive displacement in log odds |
| [03: Entropy as an area you can see](specs/03_entropy_area.md) | 3:30 | Rectangles whose widths are probability and heights are surprisal | Entropy is the sum of probability-weighted surprise |
| [04: An atlas of diagnostic trajectories](specs/04_trajectory_atlas.md) | 4:45 | Four paths through a probability triangle, followed by encounter windows | Valid reasoning paths and encounter endpoints have different uncertainty patterns |

The initial cuts total **14 minutes 55 seconds**. Each film may vary by ±10% to improve reading time while preserving required beats and final holds. The fourth goal is the trajectory atlas requested after the first three concepts; it is not an additional standalone film about equal entropy.

## Use this with Codex

1. Make this extracted bundle available to Codex alongside the current `reblocke/notebooks_dx_reasoning` checkout.
2. Use [the all-films goal](prompts/00_build_all_films.md) to commission the complete series, or one of the four individual prompts in `prompts/`.
3. Keep [the shared contract](specs/00_shared_contract.md), the selected goal specification and `data/manim_fixtures.json` together. The atlas additionally uses [its mathematics appendix](specs/05_atlas_mathematics.md).
4. Let Codex complete the local rendering and review workflow. The prompts explicitly authorize routine implementation choices and define completion as verified media exports, not scene code alone.

**Recommended work order:** establish the shared foundation and finish goal 01, then goals 02 and 03, then the atlas. If tasks run in parallel, give each task a separate branch/worktree and explicit ownership of its scene; integrate shared components once. Current notebook corrections take precedence over the old audited snapshot. The films do not require an OVR projection optimizer.

## Package contents

| Folder/file | What it supplies |
|---|---|
| `specs/00_shared_contract.md` | Environment, palette, typography, units, animation semantics, output contract and review gates |
| `specs/01_…04_*.md` | Exact mathematical examples, scene timing, actions, narration, keyframes and acceptance criteria |
| `specs/05_atlas_mathematics.md` | Complete synthetic observation models, geometry, interpolation and window semantics |
| `prompts/` | One master goal and four independently usable Codex goals |
| `data/manim_fixtures.json` | Full-precision values, exact rational probabilities where applicable and the initial cut timing |
| `validation/verify_fixtures.py` | Standard-library numerical oracle; no Manim installation required |
| `validation/fixture_verification.json` | Result of running that oracle on the supplied data |
| `MANIFEST.json` | Package file hashes and authored-version metadata |

From the extracted bundle root, check the supplied fixtures with:

```bash
python3 validation/verify_fixtures.py
```

Optionally write a fresh report:

```bash
python3 validation/verify_fixtures.py --output-report validation/fixture_verification.json
```

The oracle checks the authored mathematical examples, not any future Manim scene or notebook implementation. Codex must separately test production functions and inspect rendered geometry. The animation render commands in the shared contract are a proposed interface for Codex to implement; they are not present in this specification-only package.

## Key decisions already made

- Use Manim Community in an isolated optional animation environment; preserve the existing notebook runtime and Binder dependencies.
- Deliver 1080p/30 fps silent captioned films, fuller narration scripts and subtitle sidecars. Recorded narration is optional.
- Keep all clinical categories abstract and all examples explicitly synthetic. No clinical calibration, utility or benchmark-coverage claim follows from these examples.
- Use base-2 entropy/surprisal and natural-log odds. Keep likelihoods, likelihood ratios, joint masses, posteriors and expectations distinct.
- Use exact frozen likelihood models for the atlas. Continuous transitions illustrate the gap between recorded observations and never add new observations.
- Keep probability, entropy and geometry displays synchronized. Use fixed scales across comparisons and do not enlarge small probabilities to make them visible.
- Finish goal 01, reopening and persistent ambiguity without inventing a final diagnosis. Encounter windows preserve the evidence already incorporated into their starting beliefs.

## Specification priority and references

Respect the user's task and current repository instructions. Within this bundle, the shared contract controls global production policy; the selected goal controls its specific content; the full-precision fixtures control numerical reference values. Rounded prose labels are display approximations. Flag a genuine contradiction instead of silently replacing a scientific claim.

The [shared source list](specs/00_shared_contract.md#sources) identifies the Manim documentation, mathematical references and audited notebook snapshot. These specifications are newly authored design decisions; the synthetic fixtures are not copied clinical results or estimates from the manuscript.
