# Plan: close the two notebook review findings

Prepared 2026-10-31. **Status: implemented and verified on 2026-10-31; see the execution receipt below.**
Both failures were reproduced against the current working tree while preparing
this plan. Execute this bounded work before the animation foundation, or verify
its completed regressions if another authorized task has already fixed it.

## Scope and preservation

Work in the current `notebooks_dx_reasoning` checkout. At planning time the branch
is `codex/llm-readiness-dx-notebooks`, HEAD is
`689b6d017c42da28d6815dfe3c7a57933f5e23cc`, and the earlier repairs remain
uncommitted, including untracked implementation and test files. The review used
merge base `a18f86f866ef340248f1aa313cd8a6022b216f83` against `origin/main`.
Refresh those facts before implementation; do not assume HEAD contains the repairs.

Preserve the existing signatures, deterministic OVR method, ridge geometry,
confidence-weight rules, normalized-prior interpretation, structural zeros,
notebook cell order/IDs, unrelated outputs and attachments. Keep Python 3.11 and
the current Binder dependencies. The companion repository is outside these two
fixes; its existing edits remain untouched.

Expected files: `diagnostic_reasoning.py`, the affected cells of
`display_reasoning.ipynb`, `tests/unit/test_reasoning.py`,
`tests/notebooks/test_notebooks.py`, and a dated follow-up in
`docs/repair_verification.md`. Repair the applet as well: exhaustive inspection confirmed 47 boundary
misclassifications across its 8,820 permitted count combinations. This is a boundary repair, not a new estimator or a rewrite
of arbitrary-probability update functions.

## R1 — preserve exact qualitative category boundaries

**Observed failure.** `display_reasoning.ipynb`'s binary `predictor_wrapper`
(one-based cell 52 at planning time) selects the probability representative for
`HIGHLY_LIKELY`, then calls `logistic_regression_predict` (cell 50). Three
major-negative findings lead to log-odds `0.49999999999999867`, displaying
`UNCERTAIN`. The intended count calculation is exactly `2 - 3/2 = 0.5`, which
belongs to `LIKELY`. The review's raw notebook location was line 1108; locate by
function/cell source again because notebook JSON line numbers can move.

**Chosen repair.** Keep the category-selected calculation in its original
log-odds coordinates. Derive label-to-log-odds representatives from
`CERTAINTY_LABELS` and `BIN_REP_LOGODDS`; derive probability only for display and
the final update. Preserve the general probability-based
`logistic_regression_predict(pre_test_probability, weight_of_evidence)` contract
for callers that actually supply probabilities.

The widget accepts integer counts and its weights are exact multiples of one
sixth. Preserve that arithmetic for the count-specific path so combinations of
thirds and sixths cannot reintroduce boundary drift. A small calculation using
the canonical start and the integer numerator
`6*major_positive - 3*major_negative + 2*minor_positive - minor_negative`, with
one final division by six, is sufficient. Keep the declared weight definitions
authoritative; do not introduce independent rounded constants. A focused helper
is justified only if needed to share or directly test this discrete calculation.

Do not add epsilon tolerance or round arbitrary probabilities before classifying
them. Values immediately below a boundary must remain in the lower category.
Do not special-case the single reported example. Keep the calculation's
probability, printed label and plotted position consistent.

**Regression and completion criteria.**

- Add a failing regression for `HIGHLY_LIKELY`, counts `(0,3,0,0)` in the
  existing major-positive/major-negative/minor-positive/minor-negative order.
  The repaired output is `LIKELY` and probability `expit(0.5)`.
- Use an independent rational-arithmetic reference for category-selected count
  updates, including all four exact cutpoints and combinations of thirds/sixths.
  The bounded widget domain is small enough to enumerate if helpful. Avoid an
  expected-value calculation that repeats the proposed floating-point helper.
- Retain the existing `np.nextafter` tests immediately below and above each
  probability boundary. Equality belongs to the upper category; adjacent lower
  floats must not be snapped upward.
- Extend the fresh-kernel notebook test to drive the actual registered binary
  `interact` controls, including its dropdown and major-negative slider. The
  existing generalized multiclass widget checks do not exercise this callback.
  Retain a stable widget handle if necessary; exercise it after later cells run
  and after its defining cell is re-executed. Check displayed output, not only a
  detached call to the numerical function.
- Check that the static qualitative example and applet agree at the relevant
  canonical states. Preserve existing arbitrary-probability updates.
- Inspect the affected display once for consistency between its number and
  category. Clear only stale outputs of intentionally edited cells; keep test
  execution in temporary notebooks.

## R2 — reject positive support lost during prior normalization

**Observed failure.** `normalize_priors` divides by total mass at lines 60–61
of `diagnostic_reasoning.py`. A positive input can underflow to zero, but the
current post-normalization range check applies only to OVR. Consequently
`common_reference_posterior([1e-200,1e200], [1000,0])` returns `[0,1]` instead
of the mathematical posterior approximately `[1,5.0759589e-35]`.

**Chosen repair.** Reject this unrepresentable normalized prior explicitly.
Capture the original positive-support mask before division and, in both modes,
raise an actionable `ValueError` containing `priors` and `numerical range` if a
positive input normalizes to zero. Retain the OVR-specific interior checks and
the existing finite-total validation. If needed, contain the division's expected
underflow warning locally and inspect the result, so caller NumPy warning policy
does not obscure the deliberate validation error.

This follows the existing float64 range-error contract and preserves the public
normalized-prior return type. A general log-prior interface would be a broader
alternative; it is not necessary to close this finding. Do not clip, smooth,
drop, or silently reinterpret the lost entry as an intentional structural zero.
The example above should fail explicitly after this repair, rather than promise
new support for every mathematically recoverable extreme-scale update.

**Regression and completion criteria.**

- Reproduce the failure before editing. Assert that both direct normalization and
  the common-reference call now reject these weights with the stated range error.
  Retain the independent log-weight reference as evidence of why the old result
  was wrong; do not make the chosen limited-range API claim that it computes it.
- Confirm OVR also rejects lost support, with no change to ordinary fits.
- Confirm representable small positive entries remain positive, for example
  relative weights `[1e-200,1e100]`, and ordinary rescalings preserve weight ratios.
- Confirm genuine zero support remains accepted in common-reference updates:
  `[0,1]` remains `[0,1]`, including the already-tested extreme unsupported-class
  score, and a positive one-class prior remains `[1]`.
- Run the range cases with NumPy floating-point warnings promoted to exceptions
  to verify the intended error behavior. Existing invalid-domain tests still pass.
- Inject the failing range case through a retained common-reference notebook
  callback where feasible. Its Output region must show an actionable error and
  produce no ordinary result plot. Avoid widening normal UI slider ranges just
  to manufacture this numerical input; a controlled wrapper input is sufficient.

## Execution sequence and verification

1. Read applicable instructions and capture staged, unstaged and untracked state.
   Preserve existing changes; add the two reproductions before changing behavior.
2. Implement R1 and its focused arithmetic/callback regressions.
3. Implement R2 and its support/error regressions.
4. Run the complete existing teaching gates plus the new cases in Python 3.11:

   ```bash
   export JUPYTER_PREFER_ENV_PATH=1
   .venv/bin/python -m pytest -q tests/unit
   .venv/bin/python -m pytest -q tests/notebooks
   git diff --check
   ```

5. Check formatting/lint for changed Python files using the available repository
   tooling. Inspect notebook JSON to confirm only intended source/output cells
   changed. No full-suite companion run is needed when its files are unchanged.
6. Append actual commands, test counts, callback results and preservation checks
   to `docs/repair_verification.md`; update this plan's status and the animation
   implementation log. Do not overwrite the earlier verification receipts or
   describe previously passing tests as covering these newly discovered cases.

**Done:** both reported failures have regression coverage and the intended
behavior, current teaching checks pass, and the affected display is consistent.
There is no remaining scientific decision for these repairs under the defaults
above. The execution receipt below records the completed verification.

## 2026-10-31 execution refinement

Use one shared canonical integer-sixth helper in both qualitative widgets.
Enumerate both bounded domains against an independent rational oracle and drive
the actual registered callbacks, including after re-execution. Reject positive
prior support lost during normalization in both modes. Preserve existing APIs.
Storage gate: at least 8 GiB free before isolated animation setup, and at least
5 GiB throughout and after the preview/final-resolution preflight. Four-film
production remains the subsequent goal. Record actual results, not estimates.

## Execution receipt — 2026-10-31

Both numerical regressions and both actual qualitative callbacks failed before
repair. The implementation now shares `qualitative_count_logodds` and canonical
integer-sixth weights; both widget domains (12,005 + 8,820 combinations) agree
with an independent Fraction oracle. The applet passes the computed endpoint
directly to its plot. Its general plotting signature retains all prior positional
arguments, with one optional keyword endpoint. Arbitrary-probability APIs remain.

The common-reference lost-support case now raises the intended range error,
including under NumPy `errstate(all="raise")`. A real registered callback shows
that error and no normal plot. Genuine zeros, single-class models and representable
tiny positive weights remain supported.

`JUPYTER_PREFER_ENV_PATH=1 .venv/bin/python -m pytest -q tests/unit tests/notebooks`
passed **45 tests** (39 numerical, six notebook tests). All five notebooks ran in
fresh Python 3.11 kernels; retained callbacks, cell re-execution, the standalone
OVR cell and neighboring-float boundary checks passed. Seven existing SciencePlots
Matplotlib deprecation warnings remain. Only foundational cell 52 and applet cells
4/9 changed; other cells, IDs, outputs and attachments match the entry snapshot.
The corrected applet figure was visually inspected. Companion files are unchanged.
See [preflight verification](preflight_verification.md) and the storage receipt for
the separately authorized cleanup and animation preflight.
