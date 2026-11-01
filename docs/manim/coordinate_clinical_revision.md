# Clinical revision of “One evidence update, three coordinates”

## Mini production update — 2026-11-01

The external Mini checkout has produced the 48-second preview and 1080p final,
version-3 strict receipts, inspected frames, sidecars and an independent source
snapshot under `animations/output/02_coordinate_systems_clinical_v2/`.
The manifest status is now `reviewed`. After the Mini was unlocked, preview and
final played from the beginning to the terminal frame at normal speed with
intermittent screenshot inspection. The user accepted pronunciation, clarity and
narration/subtitle timing with the reply “Acceptable”; this session cannot receive
audio input. The package's `playback_review.json` records that evidence and its
scope. No production gates remain. The original pending records are archived.
See `implementation_log.md` for current evidence, the visible closing
qualification and the sequential replacement final.
The Air storage status below is historical.

## Status and scope at source handoff (historical)

The 48-second source, cue definitions, synthesized local narration and SRT/VTT
are prepared. The preview, final MP4, complete playback and visual review,
pronunciation check, and final package have **not** been completed: available
space remains below the 5.25 GiB render-start gate. These source and audio
checks do not establish the appearance or intelligibility of a rendered film.

This user-authorized cut is `02_coordinate_systems_clinical_v2`. It changes
the original 190-second duration, clinical framing, pacing, and audio policy;
the original film, frozen fixture and original production specification remain
intact. It uses three separate hypothetical patients with pneumonia versus no
pneumonia, not three diagnoses in one normalized differential. The positive
test is hypothetical, and LR 3 and the starting probabilities are illustrative
assumptions, not empirical claims about a real test or patient.

The original fixture remains the source of 10%→25%, 50%→75% and 90%→96.43%;
odds multiply by three, and natural-log odds increase by ln(3). The reciprocal
update is a mathematical inverse, not a claim about a negative test result.

## Verification and resumption

- `core/story02_clinical.py` supplies seven contiguous cues; `scenes/clinical_coordinates.py`
  constructs the scene using the original math and shared fixed-scale rulers.
- The finalizer selects the matching clinical source for each film, and the
  runner selects each cut's duration, event timing and final hold separately.
- Samantha at 160 words/minute generated a 48-second mono, 48-kHz WAV. Its
  SHA-256 is `fef7f7262eaccf1c831015cd4521bb92d7f5a7641c9b3705dd21e6c16eda4e0f`.
  Full audio decoding passed and subtitle timecodes match speech intervals.
- The numerical suite, actual-Manim geometry and scene construction checks,
  and immutable fixture validator are recorded in `implementation_log.md`.
- Resume with the commands in `animations/README.md` only after the storage gate
  clears. Review the entire preview with sound before final rendering; inspect
  final output at 1080p and 720p, including all coordinate changes, the inverse,
  the five-second hold, reading time, narration and subtitle alignment. Record
  actual observations and correct defects before marking review passed.
