# Synthetic animation fixtures

`manim_fixtures.json` is a byte-for-byte copy of the supplied version 1.0
bundle's synthetic reference data. Its SHA-256 is
`d4204afd2e4ee8e8bcac9cd6d5842a4dbe172932a250930516d5f62b1922407b`.
The bundle specifications and `docs/manim/implementation_log.md` provide the
field codebook, units, category order, and provenance. These are authored examples,
not patient records or empirical estimates. Do not edit the copy to fit a scene.

## Additional synthetic fixtures: goals 05 and 06

`test_results_fixtures.json` contains `goal_05`; `beliefs_actions_fixtures.json`
contains `goal_06`. Both use schema `version: 1`. Each file has its own approved
SHA-256 in the film registry. Exact arithmetic checks precede production; the
renderer and finalizer compare against that identity, including the frozen
producer copy. Changes after acceptance require a new candidate and preserved
earlier producer snapshots.

| Field | Meaning, units and allowed values |
|---|---|
| `states` | Ordered, exhaustive binary teaching states; strings. |
| `provenance`, `description`, `id` | Authored synthetic provenance, profile description and stable identifier. |
| Rational reference object | `numerator` integer, `denominator` positive integer, `value` finite floating-point reference; the fraction is exact. |
| `sensitivity`, `specificity` | State-conditional test probabilities, dimensionless, between zero and one. |
| `observed_result` | `+` or `-`; one result of the named test. |
| `lr_positive`, `lr_negative`, `lr` | Result-specific or explicitly history-conditioned likelihood ratios; dimensionless, positive. |
| `prior`, `positive`, `negative`, `posterior_*`, `posterior` | Disease probabilities in [0,1]; never computed from rounded display percentages. |
| `counts` | Nonnegative integer people; disease/no-disease by positive/negative result plus group/population totals. Test C supplies probabilities without an integer cohort. |
| `positive_change` | Posterior minus prior, probability units; multiply by 100 for percentage points. |
| `conditional_finding` | Distinct finding conditioned on the first positive result; disease and no-disease probabilities give conditional LR 2. |
| `benefit`, `cost` | Positive magnitudes of state-conditional incremental utility of act versus defer, common arbitrary utility units. |
| `utility_prior`, `utility_positive`, `utility_negative`, `gain_at_quarter` | Expected utility difference, act minus defer; signed arbitrary utility units. |
| `utility_change` | Revision to expected utility difference after the positive result, not a causal outcome gain. |
| `probability_threshold`, `odds_threshold` | Equivalent action-indifference thresholds; probability in (0,1), odds positive. Log-odds thresholds use natural logarithms. |

There are no missing observations or sentinel missing values. An absent optional
count table means no integer cohort was specified, not zero people. All numbers
are constructed teaching inputs from the corresponding new-video specification;
none are patient data, empirical test estimates, or treatment recommendations.
