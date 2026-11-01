import json
from pathlib import Path

import numpy as np
import pytest
from scipy.special import logsumexp

import diagnostic_reasoning as dr

CASES = json.loads(
    (Path(__file__).parents[1] / "fixtures/reference_cases.json").read_text()
)


def direct_ovr(p, likelihood):
    p, likelihood = np.asarray(p), np.asarray(likelihood)
    return np.array(
        [
            likelihood[k]
            / np.average(np.delete(likelihood, k), weights=np.delete(p, k))
            for k in range(len(p))
        ]
    )


def reference_logs(p, scores):
    p, scores = np.asarray(p), np.asarray(scores)
    return np.array(
        [
            scores[k]
            + np.log(np.delete(p, k).sum())
            - logsumexp(np.log(np.delete(p, k)) + np.delete(scores, k))
            for k in range(len(p))
        ]
    )


def test_bayes_references():
    c = CASES["coherent"]
    p, likelihood = np.asarray(c["prior"]), np.asarray(c["likelihood"])
    expected = p * likelihood / (p @ likelihood)
    fit = dr.ovr_project_posterior(p, direct_ovr(p, likelihood), reg=0)
    np.testing.assert_allclose(fit.posterior, expected, atol=1e-9)
    np.testing.assert_allclose(
        fit.posterior, dr.common_reference_posterior(p, fit.log_scores)
    )
    recovered_weights = fit.fitted_ovr_lr / (1 - p + p * fit.fitted_ovr_lr)
    np.testing.assert_allclose(recovered_weights, expected / p)
    np.testing.assert_allclose(dr.ovr_project_posterior(p, np.ones(3)).posterior, p)
    c = CASES["binary"]
    np.testing.assert_allclose(
        dr.ovr_project_posterior(c["prior"], c["ovr"], reg=0).posterior,
        c["posterior"],
        atol=1e-9,
    )
    c = CASES["common_reference"]
    p, likelihood = np.asarray(c["prior"]), np.asarray(c["likelihood"])
    np.testing.assert_allclose(
        dr.common_reference_posterior(p, np.log(likelihood)),
        p * likelihood / (p @ likelihood),
    )


def test_two_findings_reference_prior_contract():
    c = CASES["two_findings"]
    p, a, b = (np.asarray(c[k]) for k in ("prior", "likelihood1", "likelihood2"))
    expected = p * a * b / np.sum(p * a * b)
    fa = dr.ovr_project_posterior(p, direct_ovr(p, a), reg=0)
    fb = dr.ovr_project_posterior(p, direct_ovr(p, b), reg=0)
    np.testing.assert_allclose(
        dr.common_reference_posterior(p, fa.log_scores + fb.log_scores),
        expected,
        atol=1e-9,
    )
    wrong = dr.ovr_project_posterior(p, direct_ovr(p, a) * direct_ovr(p, b), reg=0)
    assert np.max(np.abs(wrong.posterior - expected)) > 0.001


@pytest.mark.parametrize("case", ["worked", "tail"])
def test_final_diagnostics_share_model(case):
    c = CASES[case]
    p, lr = np.asarray(c["prior"]), np.asarray(c["ovr"])
    w, reg = np.array([1.0, 2.0, 3.0]), 1e-6
    fit = dr.ovr_project_posterior(p, lr, weights=w, reg=reg)
    logs = reference_logs(p, fit.log_scores)
    np.testing.assert_allclose(np.log(fit.fitted_ovr_lr), logs, atol=1e-10)
    residual = logs - np.log(lr)
    assert fit.rmse_logLR == pytest.approx(np.sqrt(np.mean(residual**2)))
    assert fit.diagnostics["weighted_data_sse"] == pytest.approx(
        np.sum(w * residual**2)
    )
    penalty = reg * np.sum(fit.log_scores**2)
    assert fit.diagnostics["ridge_penalty"] == pytest.approx(penalty)
    assert fit.diagnostics["objective_final"] == pytest.approx(
        0.5 * (w @ residual**2 + penalty)
    )
    np.testing.assert_allclose(dr.normalize_priors([5, 3, 2], ovr=True), p)


@pytest.mark.parametrize("scores", [[0.0, 0.2, -0.1], [0.0, -34.0, -35.0]])
def test_jacobian_and_gauge(scores):
    p, s, free = np.array([0.5, 0.3, 0.2]), np.array(scores), np.array([1, 2])
    h = 1e-5
    numeric = np.column_stack(
        [
            (
                reference_logs(p, s + h * np.eye(3)[k])
                - reference_logs(p, s - h * np.eye(3)[k])
            )
            / (2 * h)
            for k in free
        ]
    )
    np.testing.assert_allclose(
        dr.model_jacobian(p, s, free), numeric, atol=1e-8, rtol=1e-5
    )
    np.testing.assert_allclose(
        dr.model_log_ovr(p, s + 1000), dr.model_log_ovr(p, s), atol=1e-11
    )


@pytest.mark.parametrize(
    "kwargs,field",
    [
        ({"priors": [0, 0, 0]}, "priors"),
        ({"priors": [-0.1, 0.6, 0.5]}, "priors"),
        ({"priors": [np.inf, 0.3, 0.2]}, "priors"),
        ({"priors": [[0.5, 0.3, 0.2]]}, "priors"),
        ({"ovr_lr": [1, np.nan, 1]}, "ovr_lr"),
        ({"ovr_lr": [0, 1, 1]}, "ovr_lr"),
        ({"weights": [1]}, "weights"),
        ({"weights": 1}, "weights"),
        ({"weights": [0, 1, 1]}, "weights"),
        ({"weights": [1, -1, 1]}, "weights"),
        ({"reg": np.nan}, "reg"),
        ({"reg": np.inf}, "reg"),
        ({"reg": -1}, "reg"),
        ({"reg": "invalid"}, "reg"),
        ({"baseline": -1}, "baseline"),
        ({"baseline": 3}, "baseline"),
        ({"baseline": 1.5}, "baseline"),
        ({"baseline": True}, "baseline"),
    ],
)
def test_invalid_ovr_boundary(kwargs, field):
    args = {"priors": [0.5, 0.3, 0.2], "ovr_lr": [4, 3, 2], **kwargs}
    with pytest.raises(ValueError, match=field):
        dr.ovr_project_posterior(**args)


@pytest.mark.parametrize(
    "p,s",
    [
        ([], []),
        ([0, 0], [0, 0]),
        ([-1, 2], [0, 0]),
        ([0.5, 0.5], [1]),
        ([0.5, 0.5], 1),
        ([0.5, 0.5], [[1], [2]]),
        ([0.5, 0.5], [np.inf, 0]),
        ([np.nan, 1], [0, 0]),
    ],
)
def test_invalid_common_reference(p, s):
    with pytest.raises(ValueError):
        dr.common_reference_posterior(p, s)


def test_zero_support_and_numerical_range():
    with np.errstate(all="raise"):
        np.testing.assert_array_equal(
            dr.common_reference_posterior([0, 1], [10, 0]), [0, 1]
        )
        np.testing.assert_array_equal(dr.common_reference_posterior([5], [100]), [1])
        np.testing.assert_array_equal(
            dr.common_reference_posterior([0, 1], [1e308, -1e308]), [0, 1]
        )
    with pytest.raises(ValueError, match="numerical range"):
        dr.common_reference_posterior([0.5, 0.5], [1000, -1000])
    with pytest.raises(ValueError, match="numerical range"):
        dr.representable_exp([1000], "fitted OVR LRs")


@pytest.mark.parametrize("n,lr", [(3, 0.01), (8, 0.1)])
def test_symmetric_candidate_policy(n, lr):
    fit = dr.ovr_project_posterior(np.ones(n), np.full(n, lr))
    assert not fit.success
    assert fit.diagnostics["optimizer_terminated"]
    assert fit.diagnostics["fit_status"] == "symmetric_inconsistent"
    assert not fit.diagnostics["minimum_verified"]
    np.testing.assert_allclose(fit.posterior, np.full(n, 1 / n))


def test_ridge_and_permutation_contract():
    p, lr = np.array([0.5, 0.3, 0.2]), np.array([4.0, 3.0, 2.0])
    a = dr.ovr_project_posterior(p, lr, baseline=0, reg=0.01)
    b = dr.ovr_project_posterior(p, lr, baseline=1, reg=0.01)
    assert abs(a.posterior[0] - b.posterior[0]) > 1e-5  # retained reference dependence
    perm = np.array([2, 0, 1])
    a = dr.ovr_project_posterior(p, lr, reg=0)
    b = dr.ovr_project_posterior(p[perm], lr[perm], reg=0)
    np.testing.assert_allclose(a.posterior[perm], b.posterior, atol=1e-8)
    small = dr.ovr_project_posterior(p, lr, reg=1e-12)
    assert small.rmse_logLR == pytest.approx(a.rmse_logLR, rel=1e-8)


def test_binary_and_category_boundaries():
    for scalar in (float, np.float64):
        assert dr.bayesian_update_prob(scalar(0), 2) == 0
        assert dr.bayesian_update_prob(scalar(1), 2) == 1
        assert dr.odds_to_probability(dr.probability_to_odds(scalar(1))) == 1
    assert dr.bayesian_update_prob(0.5, 2) == pytest.approx(2 / 3)
    np.testing.assert_allclose(
        dr.odds_to_probability(np.array([0.0, 1.0, np.inf])), [0, 0.5, 1]
    )
    np.testing.assert_allclose(
        dr.probability_to_odds(np.array([0.0, 0.5, 1.0])), [0, 1, np.inf]
    )
    assert dr.logodds_to_prob(-1000) == 0
    for value in (-1, np.nan, np.inf):
        with pytest.raises(ValueError):
            dr.bayesian_update_prob(0.5, value)
    assert dr.certainty_label(0.37) == "UNLIKELY"
    for k, boundary in enumerate(dr.BIN_BOUNDARIES_PROB):
        assert dr.certainty_label(np.nextafter(boundary, 0)) == dr.CERTAINTY_LABELS[k]
        assert dr.certainty_label(boundary) == dr.CERTAINTY_LABELS[k + 1]
        assert (
            dr.certainty_label(np.nextafter(boundary, 1)) == dr.CERTAINTY_LABELS[k + 1]
        )
    assert dr.qualitative_score(2, 4, 3, 6) == 0


def test_qualitative_count_boundaries_against_rational_oracle():
    from fractions import Fraction
    from itertools import product
    from scipy.special import expit

    for maxima in [(6, 6, 6, 6), (5, 5, 6, 6)]:
        for index, label in enumerate(dr.CERTAINTY_LABELS):
            for a, b, c, d in product(*(range(n + 1) for n in maxima)):
                exact = Fraction(index - 2) + a - Fraction(b, 2) + Fraction(c, 3) - Fraction(d, 6)
                actual = dr.qualitative_count_logodds(label, a, b, c, d)
                assert actual == float(exact)
                category = sum(exact >= boundary for boundary in map(Fraction, [-1.5, -.5, .5, 1.5]))
                assert dr.certainty_label(expit(actual)) == dr.CERTAINTY_LABELS[category]
    for invalid in [-1, 1.5, True, np.nan]:
        with pytest.raises(ValueError, match='counts'):
            dr.qualitative_count_logodds('UNCERTAIN', invalid, 0, 0, 0)


def test_normalization_rejects_lost_positive_support():
    # Independent log-domain reference demonstrates that the lost class matters.
    z = np.log([1e-200, 1e200]) + [1000., 0.]
    reference = np.exp(z - logsumexp(z))
    assert reference[0] > .999999
    with np.errstate(all='raise'):
        for ovr in [False, True]:
            with pytest.raises(ValueError, match='priors.*numerical range'):
                dr.normalize_priors([1e-200, 1e200], ovr=ovr)
        with pytest.raises(ValueError, match='priors.*numerical range'):
            dr.common_reference_posterior([1e-200, 1e200], [1000, 0])
        assert dr.normalize_priors([1e-200, 1e100])[0] > 0
        np.testing.assert_array_equal(dr.common_reference_posterior([0, 1], [1e308, 0]), [0, 1])
        np.testing.assert_array_equal(dr.common_reference_posterior([2], [1000]), [1])
