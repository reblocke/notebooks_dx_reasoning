# Synthetic reference fixtures

`reference_cases.json` contains hand-entered teaching/test parameters from the
repair specifications. They are mathematical constructions, not clinical data
or empirically estimated likelihoods. Array position fixes class order (A, B, C
for three-class cases); no missing entries are allowed.

| Field | Definition and domain |
|---|---|
| `prior` | Relative class weights; positive for OVR, normalized before use; unitless. |
| `likelihood`, `likelihood1`, `likelihood2` | Synthetic finding probabilities conditional on each class, in `(0,1]`. |
| `ovr` | Positive unitless likelihood ratio against the prior-weighted complementary mixture. |
| `posterior` | Expected class probabilities, each in `[0,1]`, summing to one. |

Expected Bayes posteriors are derived independently as `prior*likelihood` divided
by its sum. The two-finding fixture assumes independence conditional on each
class and uses the product of the class likelihoods. Natural-log LR residuals
and their diagnostic units are defined in the shared calculation module.
