# Diagnostic-reasoning repair verification

Completed October 30, 2026 (America/Denver). This record covers NB-001–NB-021
and the bounded DX-001–DX-003 companion changes. Teaching baseline:
`689b6d017c42da28d6815dfe3c7a57933f5e23cc`; companion baseline:
`9e6fbf664d08e9c009ec5ac180040bdd6200ded0`. These are synthetic software
checks, not clinical validation or evidence about a manuscript's execution path.

## Adopted contracts

- Normalize relative prior weights without clipping. OVR requires at least two
  strictly positive classes; common-reference finite scores preserve structural
  zeros and allow one class. Reject zero-total and malformed inputs.
- Confidence weights are strictly positive matching vectors. Reject scalar
  broadcasting, negative/bool/noninteger baselines, and invalid regularization.
- Preserve weighted squared natural-log LR loss, deterministic single-start
  fitting, the baseline-relative ridge geometry, and existing defaults. The default
  baseline is the first class with the largest normalized prior. The UI
  explicitly permits zero ridge. No new smoothing or sequence engine is added.
- A coherent candidate is not a demonstrated minimum. Fully symmetric
  inconsistent inputs are flagged, with no arbitrary class selection. Failed or
  flagged port fits are excluded from successful batch rows; selected failed
  cells remain blank in new coherent workbooks and are recorded as failures.
- Data RMSE is unweighted `sqrt(mean(logLR_residual**2))`. Weighted data SSE
  and ridge penalty are separate; objective is their half-sum. Finite but
  unrepresentable positive float64 outputs fail explicitly.
- The assessment prompt retains its chosen cutoffs/examples with corrected
  direction labels, explicit boundary inclusivity, version `assessment-lr-v2`
  and a runtime SHA256 identifier. Historical outputs are not re-versioned.

## Verification receipts

The teaching gate passes **43 tests**: 37 numerical checks and six notebook
checks (all five notebooks in fresh kernels plus the standalone OVR cell).
The companion's complete existing and extended suite passes **171 tests**.
Companion Ruff formatting/lint, repository policy audit, and both repositories'
`git diff --check` pass. The new teaching Python files also pass Ruff checks.

The clean teaching Python 3.11 environment was created and populated from
`requirements-dev.txt`; `jupyter lab --version` returns `4.6.5`. All retained
notebook cells execute there. Kernel tests explicitly select the tested Python,
rather than accidentally using an unrelated registered kernel.

| Component | Clean teaching environment | Companion/browser environment |
|---|---|---|
| Python | 3.11.18 | 3.11.18 |
| NumPy | 2.4.6 | 2.4.2 |
| SciPy | 1.17.1 | 1.17.1 |
| Matplotlib | 3.11.2 | 3.10.8 |
| ipywidgets | 8.1.9 | 8.1.8 |
| nbclient | 0.11.0 | 0.10.4 |
| nbformat | 5.11.1 | 5.10.4 |
| JupyterLab / Voila | 4.6.5 / 0.5.13 | 4.6.5 / 0.5.13 |

A temporary disk-space shortage interrupted an initial verification attempt;
the task-created duplicate environment/cache entries were cleaned, and the
clean environment was subsequently recreated and verified. Research artifacts
and unrelated environments were not removed. Installing launch tools in the
companion environment added packages without upgrading its existing packages.

Actual local browser checks verified both Voila entry notebooks, the core
Calculate button, controlled all-zero-prior failure, applet extrema, and the
99%→1% LR display (`0.000102`, not zero). The initial launch exposed an older
user-registered kernel overriding the active environment. The documented
shell-local `JUPYTER_PREFER_ENV_PATH=1` resolves that selection; global kernel
registrations are unchanged. Corrected displayed equations render as math.

Both regenerated worked attachments and applet figures at `(0.99,10)`,
`(0.01,0.1)`, and `(0.5,2)` were visually inspected. The fixed log-odds limits
are approximately `[-7.547705,7.547705]`, including padding; endpoints, arrows
and annotations fit. Positive and negative cases use the identical scale.

## Ticket coverage

| Ticket | Implemented behavior / verification |
|---|---|
| NB-001 | Public boundary validation, preserved weight ratios, canonical normalized priors; invalid-input tests. |
| NB-002 | Direct complement log-sums and consistent Jacobian/reporting; dominant-class reference and finite differences. |
| NB-003 | Data-only RMSE, separate weighted SSE/penalty/objective; weighted and near-zero-ridge tests. |
| NB-004 | Qualified candidates and explicit symmetric-input status; both known counterexamples and permutation checks. |
| NB-005 | Retained baseline-relative ridge, documented reference dependence, zero-ridge control and recovery tests. |
| NB-006 | Reference-prior/score contract and dependent-evidence distinction; independent two-finding Bayes fixture. |
| NB-007 | Canonical table/plot inputs, label validation, visible failures and labeled candidates; registered callbacks and injected failure. |
| NB-008 | Two corrected attachments and their prose derive from one declared fixture; exported images inspected. |
| NB-009 | Narrow objective, normalization and calibration claims in core and continuation prose; manual mathematical review. |
| NB-010 | Shared endpoint-safe binary helpers, array odds conversions, validated plot modes/bounds and dependence wording. |
| NB-011 | Distinct retained dependency bindings and shared result type; real callbacks after later cells and both re-execution orders. |
| NB-012 | Explicit evidence modes, dynamic labels and raw-weight/normalized-prior distinction; both branches checked against Bayes. |
| NB-013 | Count aggregate labeled synthetic, one aggregation/projection documented; marginal-product/joint-event counterexample. |
| NB-014 | Common-reference shape, support and finiteness checks; structural-zero, one-class and invalid-input fixtures. |
| NB-015 | Canonical weights/cutpoints/representatives and corrected tables; exact boundary and neutral-tally checks. |
| NB-016 | Correct odds/logit/natural-log/regression identities and probability argument documentation. |
| NB-017 | Conditional independence/history-conditioned alternative, repeated-observation and outer-bin limits explained. |
| NB-018 | Fixed full-control-range ruler, inward annotation alignment and positive-LR formatting; rendered and browser checks. |
| NB-019 | Python 3.11 syntax, JupyterLab installation and environment-kernel selection; clean installation, kernels and local Voila. |
| NB-020 | README identifies the existing Apache 2.0 license file; manual link/content check. |
| NB-021 | Independent numerical fixtures, actual callback/kernel gate, documented commands and Python 3.11 CI workflow. |
| DX-001 | Gradient-checked convergence, distinct failed backtracking and recomputed final objective; forced-failure regression. |
| DX-002 | Stable NumPy-only model, strict boundary and numerical-range handling; tail/reference/Jacobian tests. |
| DX-003 | Shared versioned prompt, corrected two signs and explicit intervals; deterministic boundary/example/import checks. |

For the ordinary `(4,3,2)` example, the former displayed RMSE was
`0.8472784031`; the corrected data-only RMSE is approximately `1.093831713`.
The fitted posterior remains approximately `(0.517050,0.298570,0.184381)`.
The former dominant-class fitted-LR/reporting discrepancy is covered by a
separate complement-log-sum evaluation, not by comparison between copied solvers.

## Preservation and limits

Notebook cell counts/order/IDs and unrelated attachments/outputs were checked
against the baseline JSON. Only changed-cell stale outputs were cleared; executed
test notebooks are not saved into source. The two worked attachments are the
intentional generated changes. Companion pre-existing `pyproject.toml` and
`uv.lock` edits were preserved byte-for-byte using pre/post SHA256 checks.

No API keys, paid model calls, patient data, manuscript analyses or historical
workbooks were needed or regenerated. Existing historical result attribution
remains a separate provenance question. No hosted Binder build or GitHub CI run
is claimed; the CI workflow is added for subsequent runs. The latest clean
environment emits SciencePlots/Matplotlib deprecation warnings; tested rendering
and calculations pass, while future dependency releases remain subject to CI.


## 2026-10-31 review follow-up

R1: exact integer-sixth qualitative updates now serve both binary interfaces,
including the applet's separately reproduced boundary drift. All 20,825 allowed
category/count states agree with an independent rational oracle. Tables, plotted
endpoints and labels share the same calculation. R2: normalization rejects positive
prior mass lost to float64 underflow in both modes, without clipping or changing
intentional structural-zero support.

Before repair, both new numerical tests and both actual widget callback regressions
failed. After repair, `JUPYTER_PREFER_ENV_PATH=1 .venv/bin/python -m pytest -q tests/unit tests/notebooks` passed 45 tests (39 numerical, six notebook tests),
including all five fresh kernels and range-error/no-plot handling. Existing
SciencePlots deprecation warnings remain; no test was skipped. Python syntax checks
and `git diff --check` passed. Only display cell 52 and applet cells 4/9 changed;
all other cells, IDs, outputs and attachments remain identical to the entry snapshot.
The corrected applet boundary plot was inspected at native size. All captured
companion files remained byte-identical. Details: [follow-up](manim/review_followup_plan.md).
