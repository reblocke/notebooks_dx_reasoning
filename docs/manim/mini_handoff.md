# Mac mini production handoff

The user approved continuing in a **new Mac mini chat**, with the production
checkout and runtime on the external LOCKE STATION APFS volume. The Air chat
remains the historical record. No GitHub publication is required.

## Completion update — 2026-11-01

The approved 01–04 production sequence is complete in this Mini chat. All four
clinical cuts have reviewed preview/final exports, strict version-3 receipts,
native/720p frame reviews, narration/sidecars, QA and independent source snapshots.
After unlocking, all eight clinical files and both host preflight clips played
from beginning to terminal frame at normal speed with intermittent screenshot
inspection. The user accepted pronunciation, clarity and narration/subtitle
timing with “Acceptable”; the session cannot receive audio input. Each manifest
is `reviewed`, with no remaining production gates. Current package evidence is in
`playback_review.json`; the series audit and session record are under
`migration/20261101/production/` outside the checkout. Original pending records
were archived before the metadata update, and media/source snapshots are unchanged.
The transfer-time status and production instructions below are retained as history.

## Authoritative workspace and environment

- Host: `reblocke@Brians-Mac-mini.local` (Apple M4, 16 GiB RAM).
- Checkout: `/Volumes/LOCKE STATION/diagnostic-reasoning/notebooks_dx_reasoning`.
- Branch: `codex/mini-clinical-films`; original base commit:
  `689b6d017c42da28d6815dfe3c7a57933f5e23cc`.
- Preserve the clean older checkout `/Users/reblocke/Research/notebooks_dx_reasoning`.
- Source `scripts/mini_environment.sh` before commands. It verifies volume UUID
  `4F16BA40-1497-4E5E-A6E8-4B8AEEAF4B44` and directs uv downloads, managed Python,
  package caches, Matplotlib cache, and temporary files to the external volume.
- Python 3.12 / Manim CE 0.22.1 is independent of the teaching Python 3.11 setup.
  Recreate it from `animations/uv.lock`; never copy an environment from the Air.
- Require 8 GiB free before setup, 5.25 GiB before each clinical render, and a
  5 GiB reserve throughout. Record internal free space too; the Mini internal
  disk remains constrained. Stop if the external volume is unavailable.

## Read before continuing

Read `AGENTS.md`, `animations/README.md`, `docs/manim/implementation_log.md`, the
shared production contract, all four specifications, and the atlas mathematics
appendix in `docs/manim/diagnostic_reasoning_manim_goals/`. Treat the immutable
bundle as source material. The subsequent clinical revisions below are expressly
authorized changes to duration, labels, ordering, and narration.

Preserve all ongoing notebook repairs, notebook cell IDs, attachments, unrelated
outputs, original films, historical manifests, and snapshots. This repository
uses synthetic teaching examples; do not introduce patient data or clinical
performance claims. Do not run paid models or regenerate historical analyses.

## Status at transfer and approved production order (historical)

Original silent films 01–04 were exported. Their eight preview/final MP4s have
version-3 strict decode/timeline revalidation receipts. Their bytes and historical
manifests must remain unchanged. The canonical fixture SHA-256 is
`d4204afd2e4ee8e8bcac9cd6d5842a4dbe172932a250930516d5f62b1922407b`.

**All four clinical cuts have source and generated narration/sidecars. None has
a reviewed final export.** Rendering was blocked by Air storage, not by an
unresolved scientific choice. Audio generation did not establish pronunciation
or complete playback review. Preserve existing narration WAVs and metadata;
the narration pipeline reuses matching audio rather than synthesizing it again.

| Order | Output slug | Duration | Closing hold |
|---|---|---|---|
| 01 | `01_uncertainty_increases_clinical_v2` | 54 s | 7 s |
| 02 | `02_coordinate_systems_clinical_v2` | 48 s | 5 s |
| 03 | `03_entropy_area_clinical_v2` | 54 s | 6 s |
| 04 | `04_trajectory_atlas_clinical_v2` | 72 s | 7 s |

Complete 01 preview/review/corrections/final/review/finalization before 02, then
03, then 04. The dedicated clinical stories/scenes and README contain the exact
cue timing and commands. Use local Samantha, US English, 160 words/minute, mono
AAC with H.264 video. No music or external voice service.

Films 01/03/04 use heart failure, pneumonia-related effusion, and malignancy,
assuming exactly one cause within the toy model. Keep “Toy model • illustrative
probabilities” visible. Film 01 preserves prior (0.9, 0.05, 0.05), exudative-result
likelihoods (0.1, 0.9, 0.9), and posterior (0.5, 0.25, 0.25). Average branch
entropies, never posterior vectors. Entropy change is after minus before.
Film 02 uses three independent hypothetical pneumonia patients with priors
0.1/0.5/0.9 and LR 3, preserving shared coordinate scales and reciprocal recovery.
Film 03 uses base-2 surprisal, probability-by-surprisal rectangles, and an explicit
reset for the 10% to 1% sweep. Film 04 preserves all 20 recorded states, fixed
likelihoods, finding indices, and encounter windows 0–2, 2–4, and 0–4; continuous
motion connects observations and is not extra evidence. Clinical qualifications
and sources are in `clinical_revision.md` and `coordinate_clinical_revision.md`.

## Verification and resume commands

The two latest review fixes are implemented: version-3 video verification checks
decoded video timestamps/cadence/coverage independently of audio duration, and
source snapshots include local dependencies, fixture, voice config, and lockfile.
Regression tests include corrupt packets, stale receipts, missing audio, timeline
defects, and isolated snapshot imports. Last Air run: 46 animation tests, eight
non-rendering visual checks, 1,972 fixture checks, and 15 immutable payload hashes.
These are historical results; consult the Mini migration receipt for new results.

From the external checkout:

```bash
source scripts/mini_environment.sh
uv sync --project animations --locked --python 3.12
PYTHONPATH=animations uv run --project animations --locked --with pytest python -m pytest -q animations/tests
PYTHONPATH=animations animations/.venv/bin/python -m unittest discover -s animations/visual_checks -p 'test_*.py'
animations/.venv/bin/python docs/manim/diagnostic_reasoning_manim_goals/validation/verify_fixtures.py
git diff --check
animations/.venv/bin/python animations/render.py --goal 01 --cut clinical --quality preview
animations/.venv/bin/python animations/scripts/review_video.py --slug 01_uncertainty_increases_clinical_v2 --quality preview
```

Actually review the complete preview with sound, correct defects, then render
the final and inspect it at 1080p and 720p. Check narration/subtitle alignment,
medical pronunciation, reading time, transitions, fixed scales, and closing hold.
Do not mark a visual probe passed without actual review. If audio playback or
visual access is unavailable, record the limitation and leave that gate pending.
Use version-3 strict receipts for both streams and retain decoder diagnostics.
Finalization commands for all cuts are in `animations/README.md`.

Deliver each cut's preview, final MP4, narration WAV, SRT/VTT, script, timing,
keyframes, QA record, and independent source snapshot/manifest. Record commands,
corrections, actual storage, and remaining gates in the implementation log.
Completion requires reviewed, verified final exports, not source or rendering alone.

## Migration records

Transfer inventories, original status/diffs, command logs, host preflight, and
hash acceptance records live outside the checkout under
`/Volumes/LOCKE STATION/diagnostic-reasoning/migration/20261101/`.
Historical manifests may mention Air paths; preserve them as historical records.
Do not overwrite the original preflight output. Run the Mini host preflight in
a separate scratch copy stored under that migration directory.
