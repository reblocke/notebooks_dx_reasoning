# Clinical revision of “Uncertainty can increase”

## Mini production update — 2026-11-01

The external Mini checkout has produced the 54-second preview and 1080p final,
version-3 strict receipts, inspected frames, sidecars and an independent source
snapshot under `animations/output/01_uncertainty_increases_clinical_v2/`.
The manifest status is now `reviewed`. After the Mini was unlocked, preview and
final played from the beginning to the terminal frame at normal speed with
intermittent screenshot inspection. The user accepted pronunciation, clarity and
narration/subtitle timing with the reply “Acceptable”; this session cannot receive
audio input. The package's `playback_review.json` records that evidence and its
scope. No production gates remain. The original pending records are archived,
and the current evidence and corrections are in `implementation_log.md`; the
Air storage block below is historical.

## Status at source handoff (historical)

The 54-second scene, cue source, local narration pipeline, and strict decode
gate are implemented. **Preview, full-resolution export, normal-speed audio and
visual review, final packaging, and the deliverable video are blocked by free
space.** Source construction and tests do not establish rendered quality.

This user-authorized version changes the original abstract labels, order, silent
audio policy, and nominal 210-second duration. It preserves the original video,
immutable specification bundle, fixture, exact mathematical states, and a
seven-second completed final hold. Its distinct slug is
`01_uncertainty_increases_clinical_v2`.

## Clinical and mathematical framing

In this synthetic teaching model only, the three exhaustive, exclusive causes
of a pleural effusion are heart failure, a pneumonia-related effusion, and
malignancy. E is fluid meeting exudative criteria. Priors `(0.9, 0.05, 0.05)`
and conditional finding probabilities `(0.1, 0.9, 0.9)` are **illustrative
assumptions**, not estimates for clinical diagnosis. Patients can have other
or multiple causes; the three-cause premise is an explicit modeling constraint.

The clinical direction is supported by Porcel and Vives' series of cardiac,
pneumonia-related and neoplastic effusions:
https://journal.chestnet.org/article/S0012-3692%2816%2937039-8/fulltext
Bielsa and colleagues document that cardiac effusions can meet exudative
criteria, with frequencies different from this toy model:
https://pubmed.ncbi.nlm.nih.gov/22372660/
These studies provide context, not the supplied prior or likelihood values.

The observed exudative branch has probability 0.18, posterior `(0.5, 0.25,
0.25)`, and entropy 1.500 bits. The non-exudative branch has probability 0.82
and entropy about 0.107 bits. Starting entropy is about 0.569 bits; weighted
expected posterior entropy is about 0.358 bits. With after-minus-before signs,
observed entropy change is about +0.931 bits and expected entropy change is
about −0.211 bits. Expected information gain is +0.211 bits. The displayed
weighted sum averages the two branch entropies, not posterior vectors.

## Execution and review

The source uses `core/story01_clinical.py`, `scenes/clinical_uncertainty.py`,
and `core/narration.py`. The latter generates locally synthesized Samantha speech
at 160 words/minute, checks each speech interval, writes 48-kHz mono audio, and
creates speech-aligned SRT/VTT from the same cues. The runner produces a separate
narrated H.264/AAC output and records Manim and mux commands and storage.

Follow the commands in `animations/README.md`. Before each run measure current
free space; the clinical runner enforces 5 GiB plus 256 MiB before starting and
monitors the 5 GiB reserve during rendering and muxing. Render sequentially.
Inspect the entire preview with sound at normal speed, pronunciation, captions,
the 18%/82% weights, actual motion and transitions. Correct any defects and
review the replacement preview. Then render and inspect the final in 1080p and
at 720p, including all states and the complete final hold. Only after each
actual visual/audio review set that quality's probe `visual_review` to `passed`;
include observations and any remaining limits in the finalizer's review note.
Check SRT/VTT timing against the audio and caption visibility; finalization also
requires strict full-file decoding of both streams and matching hashes.

## Verification and storage receipt

### Follow-up: narration prepared, render still blocked

On the later authorized cleanup pass, the complete local Samantha narration and
SRT/VTT were generated. The 54-second mono, 48-kHz WAV fully decoded and its
speech intervals match the subtitle timecodes. Its SHA-256 is
`2230efb279b9bdcb3d2d28c4dea56ae0b660ffd5e9f22b3657b5dd0ccd38e0ae`.
This is not a pronunciation, visual, or playback review. Both preview and final
MP4s remain blocked until the 5.25 GiB starting gate is met.

- The supplied validator passed 1,972/1,972 checks; the fixture copies retain
  SHA-256 `d4204afd2e4ee8e8bcac9cd6d5842a4dbe172932a250930516d5f62b1922407b`.
- The strict decode tests reproduced rejection of corrupt H.264 and missing
  required audio; a stale or failed receipt cannot satisfy finalization.
  Eight existing silent preview/final movies passed the new decoder and matched
  their historical manifest hashes. New strict receipts sit beside the videos;
  historical manifests were not changed.
- A two-cue, four-second temporary narration smoke test generated and reused a
  48-kHz mono track with correctly bounded intervals. It is not a review of the
  complete film or voice pronunciation. A no-video scene construction check
  passed frame bounds, 54-second timeline, and seven-second final hold.
- `PYTHONPATH=animations .venv/bin/python -m pytest -q animations/tests`
  passed 26 tests; `PYTHONPATH=animations animations/.venv/bin/python -m unittest
  discover -s animations/visual_checks -p 'test_*.py'` passed six checks.
  `git diff --check` passed. The new scene has not been rendered or inspected
  as a video.
- On 2026-10-31, uv 0.13.6's cache was `/Users/blocke/.cache/uv`.
  `uv cache prune` found no unused entries. With no open uv cache handles,
  `uv cache clean` removed 8,643 downloadable files (319.2 MiB); installed
  environments were preserved. If the animation environment ever needs
  rebuilding, the documented restoration command is `uv sync --project
  animations --locked --python 3.12`, which downloads missing cache entries.
  The fresh guarded retention dry-run found zero
  candidate files. The Playwright cache was empty and only the newest updater
  stage remained. Conda's dry-run listed 94 candidates totaling 0.258 GiB;
  no Conda cleanup was performed because this would not close the shortfall
  and package/environment dependency checks had not been completed.
- Measured free space fluctuated between 2.87 and 4.33 GiB during the work,
  below both the 5 GiB reserve and the clinical runner's 5.25 GiB start gate.
  The preview command exited with the expected storage-block message. Refresh
  the measurement; do not treat these values as a current reservation.
