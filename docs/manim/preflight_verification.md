# Repair and animation preflight verification — 2026-10-31

**P0 and P1 passed.** The four films and shared production mathematics/cues remain
unimplemented. Reuse the isolated environment and continue at P2 in the
[implementation log](implementation_log.md).

## Repairs and preservation

- Both numerical regressions and the two registered widget failures were reproduced
  before repairs. `JUPYTER_PREFER_ENV_PATH=1 .venv/bin/python -m pytest -q tests/unit tests/notebooks`
  passed **45 tests**: 39 numerical and six notebook tests, including all five fresh
  Python 3.11 kernels. The rational oracle covers 20,825 category/count combinations.
- The actual common-reference callback reports a numerical-range error and emits
  no normal plot for lost prior support. Genuine zeros and representable tiny
  priors retain their contracts. Arbitrary-probability signatures and the fitting
  method are unchanged.
- The applet boundary figure was inspected: end log-odds −1.5, probability 18.2%,
  category Unlikely. Its plotted endpoint and table agree. Foundational cell 52
  and applet cells 4/9 are the only changed cells; other cells, IDs, attachments
  and outputs match the entry snapshot. Executed notebooks were temporary.
- The BMI retention CLI passed all **13 synthetic E2E tests**. Its real plan found
  no candidates; apply removed zero files and verified **9,849 protected hashes**.
  No clinical fits, source preparation or scientific report refits occurred.
- All captured companion-repository files remained byte-identical. Existing
  unrelated notebook and BMI work was preserved. Python syntax and both repositories'
  `git diff --check` passed. No standalone lint tool is configured for this change;
  seven existing SciencePlots deprecation warnings remain in the notebook tests.

## Storage

The setup gate was measured at **8.113 GiB free** (required ≥8 GiB).
The minimum sampled free space across successful preview/final renders was
**7.712 GiB**, and the final measurement was **6.644 GiB** (required ≥5 GiB).
Rendering sampled free space every 0.5 seconds; setup has before/after measurements,
not a continuous peak-storage measurement. These values are timestamped snapshots.

`uv cache prune` found nothing unused. Supported `uv cache clean`, inactive
Playwright browser removal and deletion of the verified obsolete updater stage
were sufficient. No Conda package cleanup was needed. The installed app, newest
pending updater, configured Codex runtime, environments and research material were
retained; no unrelated processes were stopped. Playwright browsers will download
again when needed; exact per-project restoration commands and client versions are
in [storage_preflight_receipt.json](storage_preflight_receipt.json).

## Animation checks and actual commands

```bash
uv sync --project animations --python 3.12
uv lock --project animations
uv run --project animations --locked python animations/render.py --goal preflight --quality preview
uv run --project animations --locked python animations/render.py --goal preflight --quality final
.venv/bin/python docs/manim/diagnostic_reasoning_manim_goals/validation/verify_fixtures.py --output-report /tmp/dx-fixture-verification.json
```

Python **3.12.16**, Manim CE **0.22.1**, Matplotlib **3.11.2**, Cairo renderer.
Direct dependencies and the resolved environment are pinned. Arial was confirmed
through Pango. A real MathTex probe failed because `latex` is absent; local
Matplotlib SVG math is the permitted fallback. An unsupported shape import was
corrected before rendering. Preview inspection found opaque white equation
backgrounds; transparent SVG output fixed them and was re-rendered/reviewed.
Fractions, subscripts, minus signs and natural/base-2 logs are readable.

Both silent exports are **12.000 seconds**, H.264/yuv420p. Preview: **854×480,
15 fps**; final: **1920×1080, 30 fps**. `ffprobe` checked streams, dimensions,
frame rate and duration; `ffmpeg -v error -i <export> -f null -` fully decoded both
without errors. Samples at 3, 6 and 11.9 seconds were extracted; mid-transition
and final states were inspected, including 1080p and 720p viewing scales.
Normal-speed playback was not observed; no such check is claimed.

Local deliverables:

- [Preview](../../animations/output/preflight/preflight_preview.mp4)
- [1080p export](../../animations/output/preflight/preflight_final.mp4)
- [720p review frame](../../animations/output/preflight/final_720p.png)
- [Manifest, source hashes and storage samples](preflight_manifest.json)
- [Fresh fixture oracle](execution_fixture_verification.json): **1,972/1,972**;
  all 15 original manifest payload hashes also match. Source bundle unchanged.

This clears the bounded setup/preflight gate, not acceptance of any film. Continue
with shared production math, geometry, cue/subtitle export and goal 01; then goals
02, 03 and the atlas. Recheck available space before each render and maintain the
5 GiB reserve. The current runner supports only `--goal preflight`; add the film
dispatch as each implementation is completed. Do not replace working sources from
HEAD or repeat cleanup without a fresh eligibility check.
