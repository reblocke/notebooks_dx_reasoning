# Diagnostic-reasoning animation production

## New full-length clinical films: 05 and 06

The new specifications and implementation addendum are in
`../docs/manim/new_video_goals_20261101/`. Goal 05 explains result denominators and
likelihood ratios (175 seconds); goal 06 connects leaf plots, natural-log evidence
and expected consequences (180 seconds). Both use synthetic binary teaching
models, local Samantha narration, and a seven-second stationary closing hold.
The optional 60-second adaptation is excluded.

The new goals default to `--cut clinical`; requesting `--cut original` fails.
Goals 01–04 and preflight retain their existing defaults. On the production Mini,
source `scripts/mini_environment.sh`, then produce 05 completely before 06:

```bash
animations/.venv/bin/python animations/render.py --goal 05 --quality preview
animations/.venv/bin/python animations/scripts/review_video.py --slug 05_test_results_clinical_v1 --quality preview
# Actually review the corrected preview, including listening, before the final.
animations/.venv/bin/python animations/render.py --goal 05 --quality final
animations/.venv/bin/python animations/scripts/review_video.py --slug 05_test_results_clinical_v1 --quality final
animations/.venv/bin/python animations/scripts/finalize_film.py --slug 05_test_results_clinical_v1 --scene clinical_test_results.py --review-note '<actual review evidence>'
animations/.venv/bin/python animations/render.py --goal 06 --cut clinical --quality preview
animations/.venv/bin/python animations/scripts/review_video.py --slug 06_beliefs_actions_clinical_v1 --quality preview
# Actually review the corrected preview, including listening, before the final.
animations/.venv/bin/python animations/render.py --goal 06 --cut clinical --quality final
animations/.venv/bin/python animations/scripts/review_video.py --slug 06_beliefs_actions_clinical_v1 --quality final
animations/.venv/bin/python animations/scripts/finalize_film.py --slug 06_beliefs_actions_clinical_v1 --scene clinical_beliefs_actions.py --review-note '<actual review evidence>'
```

The film registry declares each scene and its independent fixture identity.
New source snapshots include the relevant fixture, helpers and segmented speech
implementation. The finalizer checks the approved fixture in each frozen
producer snapshot, never merely comparing a newly calculated live hash to itself.
Legacy fixture identity checks remain intact.

For 05/06, the audio export also places decoded video frames on an exact CFR
grid. Before doing so, it requires the complete expected frame count and allows
at most 1 ms of Manim partial-clip timestamp rounding. Missing frames or larger
offsets fail; the finished movie must still pass the unchanged strict version-3
timeline check. The source-cadence measurements are retained in storage receipts.

For 05/06, the eight/twelve story cues contain shorter explicit speech segments.
Every segment is synthesized and measured; one/two-line SRT and VTT entries use
those measured intervals. Receipts bind cue text, segmentation, voice/rate and
audio identity. Legacy cue-based sidecars remain supported. Archive superseded
candidates before regenerating changed narration; never silently reuse mismatched
audio. Caption text is concise and distinct from the full spoken subtitles.

Review extraction includes before/during/after event samples and the actual last
decoded frame. Automated verification initializes review gates as pending.
Full playback and real listening acceptance are separate requirements; prior
film acceptance does not carry forward. Current production status and limitations
are in the implementation log and each local output package.

This additive Python 3.12 / Manim CE 0.22.1 project contains the verified
12-second preflight, the original silent films, and separate narrated clinical
cuts. The current state of each
film and its acceptance gates is recorded in `../docs/manim/implementation_log.md`.
Notebook Python 3.11 dependencies are unchanged.

On the Mac mini, run from the external checkout and source
`scripts/mini_environment.sh` in every new shell before these commands. It checks
the mounted volume identity and keeps runtime, caches, temporary files and output
on LOCKE STATION. Preserve the original films and their historical manifests.

From the repository root:

```bash
uv sync --project animations --locked --python 3.12
uv run --project animations --locked python animations/render.py --goal preflight --quality preview
uv run --project animations --locked python animations/render.py --goal preflight --quality final
uv run --project animations --locked python animations/render.py --goal 01 --quality preview
uv run --project animations --locked python animations/render.py --goal 01 --quality final
uv run --project animations --locked python animations/render.py --goal 02 --quality preview
uv run --project animations --locked python animations/render.py --goal 02 --quality final
uv run --project animations --locked python animations/render.py --goal 03 --quality preview
uv run --project animations --locked python animations/render.py --goal 03 --quality final
uv run --project animations --locked python animations/render.py --goal 04 --quality preview
uv run --project animations --locked python animations/render.py --goal 04 --quality final
PYTHONPATH=animations .venv/bin/python -m pytest -q animations/tests
PYTHONPATH=animations animations/.venv/bin/python -m unittest discover -s animations/visual_checks -p test_visual_components.py
```

Use at least 8 GiB free before initial environment setup. The runner requires a
5 GiB free-space reserve and samples it every 0.5 seconds while rendering. If the
reserve is breached, it stops only its own render, records the failure, and leaves
unrelated processes untouched. Refresh storage measurements before subsequent
films; this small preflight does not establish a full-series storage estimate.
Render sequentially and retain required previews, final exports and QA evidence.
Only redundant caches created by this animation project may be reclaimed later.

## Rendering and verification

Cairo/CPU rendering; preview 854×480 at 15 fps and final 1920×1080 at 30 fps.
Both files are silent H.264 MP4s in `output/preflight/`, which is ignored by Git.
The same directory contains equations as SVGs, sampled frames, stream/decode
verification and storage records. `preflight_preview.mp4` and
`preflight_final.mp4` are the convenient complete exports.

Arial is verified through Pango. A real MathTex probe failed because `latex` is
absent. The documented fallback uses local Matplotlib mathtext SVGs, explicitly
transparent, preserving fractions, subscripts, minus signs, natural logs and
base-2 logs. No system TeX installation is required. The equations and probability
ruler are synthetic typography/motion checks, not a clinical claim or a completed
film scene. The displayed endpoint is 2/3 for prior 1/2 and LR 2.

```bash
ffprobe -v error -show_streams -show_format -of json animations/output/preflight/preflight_final.mp4
ffmpeg -v error -i animations/output/preflight/preflight_final.mp4 -f null -
```

See `../docs/manim/preflight_verification.md` for actual checks, corrections,
limits and the handoff to the four-film goal. Existing notebook cells and widget
globals are never executed or imported by the animation project.

## Film production

Goal 01's cue source drives the burned-in caption, complete editable narration,
SRT/VTT and timing metadata. Production tests independently compare calculations
with the supplied immutable fixtures; the separate visual check measures actual
Manim bar widths. `scripts/review_video.py` verifies full decoding and produces
state/transition frames for visual inspection. A preview or scene source alone
is not a completed film. The trajectory atlas and its final export have been reviewed and packaged. Normal-speed playback of the corrected cuts is limited as documented in the implementation log.

## Clinical revision of goal 01

The separate 54-second clinical cut preserves the original film and fixture.
Its local artifacts are under `output/01_uncertainty_increases_clinical_v2/`.
The Mini production entries in `../docs/manim/implementation_log.md` record actual
exports and review gates; the earlier Air storage block in
`../docs/manim/clinical_revision.md` is historical.

Once the storage gate is satisfied, render the preview, review it with sound,
and inspect the generated frames before marking its visual probe as passed:

```bash
animations/.venv/bin/python animations/render.py --goal 01 --cut clinical --quality preview
animations/.venv/bin/python animations/scripts/review_video.py --slug 01_uncertainty_increases_clinical_v2 --quality preview
```

After any corrections, render and review `--quality final` the same way. Both
visual reviews and current strict-decode receipts are required by finalization:

```bash
animations/.venv/bin/python animations/scripts/finalize_film.py --slug 01_uncertainty_increases_clinical_v2 --scene clinical_uncertainty.py --review-note '<actual visual and audio review>'
```

The revision uses the locally available Samantha voice and a single cue source
for narration, burned-in captions, speech-aligned SRT/VTT, and timing metadata.
No audio service is called. Existing silent film commands remain unchanged.

## Clinical revision of goal 02

The separate 48-second pneumonia teaching cut uses three hypothetical binary
examples and the original LR-3 fixture. Its artifacts are under
`output/02_coordinate_systems_clinical_v2/`. The positive
test and all probabilities are illustrative, not clinical performance estimates.
See the Mini production entries in `../docs/manim/implementation_log.md` for
current exports and review gates; the Air storage status in
`../docs/manim/coordinate_clinical_revision.md` is historical.
Complete the goal 01 clinical preview and final first.

Once at least 5.25 GiB is available, render goal 02 sequentially:

```bash
animations/.venv/bin/python animations/render.py --goal 02 --cut clinical --quality preview
animations/.venv/bin/python animations/scripts/review_video.py --slug 02_coordinate_systems_clinical_v2 --quality preview
animations/.venv/bin/python animations/render.py --goal 02 --cut clinical --quality final
animations/.venv/bin/python animations/scripts/review_video.py --slug 02_coordinate_systems_clinical_v2 --quality final
animations/.venv/bin/python animations/scripts/finalize_film.py --slug 02_coordinate_systems_clinical_v2 --scene clinical_coordinates.py --review-note '<actual visual and audio review>'
```

Inspect and, if necessary, correct the complete preview with sound before the
final render. Mark each visual probe as passed only after actual review. Inspect
the final at 1080p and 720p, including subtitle alignment, pronunciation and
the five-second hold. Finalization requires matching strict-decode receipts.

## Clinical revisions of goals 03 and 04

The 54-second entropy-area cut and 72-second trajectory atlas have dedicated
clinical scene and cue sources. Their examples use three illustrative causes
of pleural effusion; all probabilities and E1–E4 findings are synthetic. The
source, locally generated narration, subtitle tracks and mathematical checks are
shared with their local artifact sets under `output/03_entropy_area_clinical_v2/`
and `output/04_trajectory_atlas_clinical_v2/`. Current render and review status is
in the Mini production entries of `../docs/manim/implementation_log.md`.
The shared clinical qualifications and sources are in
`../docs/manim/clinical_revision.md`. Complete the goal 01 and 02 cuts first.

After the 5.25 GiB starting gate is met, run these sequentially, review each
complete preview with sound, correct it, and only then render its final:

```bash
animations/.venv/bin/python animations/render.py --goal 03 --cut clinical --quality preview
animations/.venv/bin/python animations/scripts/review_video.py --slug 03_entropy_area_clinical_v2 --quality preview
animations/.venv/bin/python animations/render.py --goal 03 --cut clinical --quality final
animations/.venv/bin/python animations/scripts/review_video.py --slug 03_entropy_area_clinical_v2 --quality final
animations/.venv/bin/python animations/scripts/finalize_film.py --slug 03_entropy_area_clinical_v2 --scene clinical_entropy_area.py --review-note '<actual visual and audio review>'
animations/.venv/bin/python animations/render.py --goal 04 --cut clinical --quality preview
animations/.venv/bin/python animations/scripts/review_video.py --slug 04_trajectory_atlas_clinical_v2 --quality preview
animations/.venv/bin/python animations/render.py --goal 04 --cut clinical --quality final
animations/.venv/bin/python animations/scripts/review_video.py --slug 04_trajectory_atlas_clinical_v2 --quality final
animations/.venv/bin/python animations/scripts/finalize_film.py --slug 04_trajectory_atlas_clinical_v2 --scene clinical_trajectory_atlas.py --review-note '<actual visual and audio review>'
```

Current finalization requires version-3 strict-decode receipts, including the
video's own frame timestamps and complete duration. Prior version-2 receipts
and historical manifests remain unchanged. Inspect both finals at 1080p and
720p and verify speech, subtitles, endpoint pauses and closing holds.

For narrated cuts, both probes must explicitly record `playback_review: passed`
and `audio_review: passed` before full acceptance. A passed visual review does
not override a missing, pending or failed listening check. The explicit pending
option permits pending reviews but never a failed review.

New renders run their scene and config from a unique `render_sources/` snapshot
created before the renderer launches. The storage receipt binds the movie hash
to that snapshot's manifest, source hashes, narration and sidecar hashes.
Finalization verifies both receipts, requires matching preview/final inputs,
and packages the frozen producer source even if the checkout has since changed.
It rejects changed snapshots, changed package inputs and missing provenance
before creating canonical keyframes or a final source snapshot. Legacy accepted
exports and their historical receipts remain unchanged; a legacy receipt cannot
be relabeled as render-time evidence. A fresh finalization requires fresh bound
renders. The animation CI job runs these regressions separately from the
Python 3.11 notebook checks.

## Packaging while playback review is pending

When playback access is unavailable, retain `visual_review: pending` in each
probe. Record `frame_review: passed` only after actual frame inspection and keep
`playback_review: pending`. The user's explicit instruction to continue with
review gates pending permits assembly using the finalizer's
`--allow-pending-playback` option. This still requires valid version-3 video/audio
receipts, reviewed frames, matching source/audio, subtitles and storage records.

Such packages have `acceptance_status: pending_playback_review` and explicit
remaining gates in their manifest and QA record. They are not completed films.
Normal-speed preview/final playback with sound, pronunciation, intelligibility
and audible subtitle alignment remain pending. Sampled frames and decoding do
not pass those gates. Existing canonical keyframes and source snapshots are
protected against blind replacement; preserve them when adding later review
evidence.

## Mini clinical production complete — 2026-11-01

All four packages have preview and 1920×1080/30-fps H.264 finals with mono AAC,
version-3 strict receipts, inspected frames at native and 720p sizes, retained
narration/sidecars, QA and source snapshots. All eight clinical files and both
Mini host preflight clips played from beginning to terminal frame in QuickTime
at normal 1× speed with intermittent screenshot inspection. The user accepted
pronunciation, clarity and narration/subtitle timing with the in-chat reply
“Acceptable.” Listening approval is the user's judgment; this session cannot
receive audio input. Every clinical manifest is now `reviewed`, with no remaining
production gates. Each package's `playback_review.json` records scope, timestamps,
movie hashes and observations.

| Film | Runtime | Closing hold | Local artifact folder |
|---|---:|---:|---|
| 01: uncertainty increases | 54 s | 7 s | `output/01_uncertainty_increases_clinical_v2/` |
| 02: coordinate systems | 48 s | 5 s | `output/02_coordinate_systems_clinical_v2/` |
| 03: entropy area | 54 s | 6 s | `output/03_entropy_area_clinical_v2/` |
| 04: trajectory atlas | 72 s | 7 s | `output/04_trajectory_atlas_clinical_v2/` |

The independent package/preservation audit is in
`/Volumes/LOCKE STATION/diagnostic-reasoning/migration/20261101/production/series_acceptance.json`.
The session record is `playback_review_session.json` beside that audit. Original
pending probes, manifests, QA and notes were hash-verified and archived before
the metadata update. Movies, narration, sidecars, canonical keyframes and source
snapshots were preserved. QuickTime displayed extra automatic “English (US)
Transcribed” captions during speech; their overlay and transcription are player
behavior, separate from the authored captions and supplied SRT/VTT.
Required previews and final MP4s use the documented slug names; files containing
`before_` are retained diagnostic candidates, not accepted exports.
