"""Shared synthetic teaching calculations; no empirical calibration is implied.

OVR inputs refer to one observation at the supplied reference prior. The loss is
weighted squared natural-log LR error plus baseline-relative score shrinkage.
A single local optimizer produces a coherent candidate, not a minimum certificate.
"""

from dataclasses import dataclass
from numbers import Integral

import numpy as np
from scipy.optimize import least_squares
from scipy.special import expit, logsumexp


FEATURE_SIXTHS = {
    "major_positive": 6,
    "minor_positive": 2,
    "minor_negative": -1,
    "major_negative": -3,
}
FEATURE_WEIGHTS = {name: units / 6 for name, units in FEATURE_SIXTHS.items()}
CERTAINTY_LABELS = (
    "HIGHLY_UNLIKELY",
    "UNLIKELY",
    "UNCERTAIN",
    "LIKELY",
    "HIGHLY_LIKELY",
)
BIN_BOUNDARIES_LOGODDS = np.array([-1.5, -0.5, 0.5, 1.5])
BIN_REP_LOGODDS = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
BIN_BOUNDARIES_PROB = expit(BIN_BOUNDARIES_LOGODDS)
CERTAINTY_ESTIMATES = dict(zip(CERTAINTY_LABELS, expit(BIN_REP_LOGODDS)))


def float_vector(values, name, minimum=1):
    try:
        a = np.asarray(values, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a numeric 1-D vector.") from exc
    if a.ndim != 1 or a.size < minimum:
        raise ValueError(
            f"{name} must be a 1-D vector with at least {minimum} entries."
        )
    if not np.all(np.isfinite(a)):
        raise ValueError(f"{name} must contain only finite values.")
    return a.copy()


def normalize_priors(values, *, ovr=False):
    p = float_vector(values, "priors", 2 if ovr else 1)
    if np.any(p < 0) or (ovr and np.any(p == 0)):
        raise ValueError(
            "priors must be strictly positive for OVR."
            if ovr
            else "priors must be nonnegative."
        )
    total = np.sum(p)
    if not np.isfinite(total) or total <= 0:
        raise ValueError("priors must have positive finite total mass.")
    positive = p > 0
    with np.errstate(under="ignore"):
        p /= total
    if np.any(positive & (p == 0)):
        raise ValueError("normalized priors lose positive support outside the numerical range.")
    if ovr and (np.any(p <= 0) or np.any(p >= 1)):
        raise ValueError(
            "normalized OVR priors are outside the supported numerical range (0, 1)."
        )
    return p


def validate_posterior(values, names=None):
    p = float_vector(values, "posterior")
    if (
        np.any(p < 0)
        or np.any(p > 1)
        or not np.isclose(p.sum(), 1.0, atol=1e-10, rtol=0)
    ):
        raise ValueError("posterior must be a probability vector summing to one.")
    if names is not None and len(names) != len(p):
        raise ValueError("names and posterior must have the same length.")
    return p


def common_reference_posterior(priors, scores):
    """Finite class log likelihoods (or log LRs sharing one reference)."""
    p = normalize_priors(priors)
    s = float_vector(scores, "scores")
    if s.shape != p.shape:
        raise ValueError("scores and priors must have the same 1-D shape.")
    # Structural zeros cannot choose the score gauge for the supported classes.
    active = p > 0
    logp = np.full(p.shape, -np.inf)
    np.log(p, out=logp, where=p > 0)
    z = np.full(p.shape, -np.inf)
    with np.errstate(over="ignore"):
        z[active] = logp[active] + (s[active] - s[active].max())
    with np.errstate(under="ignore"):
        q = np.exp(z - logsumexp(z))
    if not np.all(np.isfinite(q)) or np.any(active & (q == 0)):
        raise ValueError("posterior is outside the supported float64 numerical range.")
    return validate_posterior(q)


def _probability(value, *, interior=False):
    p = float(value)
    if not np.isfinite(p) or not 0 <= p <= 1 or (interior and p in (0, 1)):
        domain = "strictly between 0 and 1" if interior else "between 0 and 1 inclusive"
        raise ValueError(f"probability must be finite and {domain}.")
    return p


def _positive_lr(value):
    lr = float(value)
    if not np.isfinite(lr) or lr <= 0:
        raise ValueError("likelihood_ratio must be finite and strictly positive.")
    return lr


def probability_to_odds(probability):
    p = np.asarray(probability, dtype=float)
    if not np.all(np.isfinite(p)) or np.any(p < 0) or np.any(p > 1):
        raise ValueError("probability must be finite and between 0 and 1 inclusive.")
    with np.errstate(divide="ignore"):
        result = p / (1 - p)
    return float(result) if p.ndim == 0 else result


def odds_to_probability(odds):
    o = np.asarray(odds, dtype=float)
    if np.any(np.isnan(o)) or np.any(o < 0):
        raise ValueError("odds must be nonnegative and not NaN.")
    with np.errstate(invalid="ignore"):
        result = np.where(np.isposinf(o), 1.0, o / (1 + o))
    return float(result) if o.ndim == 0 else result


def prob_to_logodds(probability):
    p = _probability(probability, interior=True)
    return np.log(p) - np.log1p(-p)


def logodds_to_prob(logodds):
    x = float(logodds)
    if not np.isfinite(x):
        raise ValueError("logodds must be finite.")
    return float(expit(x))


def bayesian_update_odds(pre_test_odds, likelihood_ratio):
    odds_to_probability(pre_test_odds)  # validate, including the infinite endpoint
    lr = _positive_lr(likelihood_ratio)
    return float(pre_test_odds) * lr


def bayesian_update_prob(pre_test_prob, likelihood_ratio):
    p, lr = _probability(pre_test_prob), _positive_lr(likelihood_ratio)
    return p if p in (0, 1) else logodds_to_prob(prob_to_logodds(p) + np.log(lr))


def certainty_label(probability):
    """At a cutpoint, equality belongs to the upper category."""
    p = _probability(probability)
    return CERTAINTY_LABELS[np.searchsorted(BIN_BOUNDARIES_PROB, p, side="right")]


def qualitative_count_logodds(start_category, major_positive, major_negative,
                              minor_positive, minor_negative):
    """Exact sixth-unit aggregation for the bounded synthetic count controls."""
    if start_category not in CERTAINTY_LABELS:
        raise ValueError("start_category must be a canonical certainty label.")
    counts = dict(zip(
        ("major_positive", "major_negative", "minor_positive", "minor_negative"),
        (major_positive, major_negative, minor_positive, minor_negative),
    ))
    if any(isinstance(n, (bool, np.bool_)) or not isinstance(n, Integral) or n < 0
           for n in counts.values()):
        raise ValueError("counts must be nonnegative integers.")
    start = BIN_REP_LOGODDS[CERTAINTY_LABELS.index(start_category)]
    units = int(start * 6) + sum(FEATURE_SIXTHS[k] * int(n) for k, n in counts.items())
    return units / 6


def qualitative_score(major_positive, major_negative, minor_positive, minor_negative):
    """Illustrative count aggregate, not an estimated joint-event OVR LR."""
    return sum(
        FEATURE_WEIGHTS[name] * count
        for name, count in (
            ("major_positive", major_positive),
            ("major_negative", major_negative),
            ("minor_positive", minor_positive),
            ("minor_negative", minor_negative),
        )
    )


@dataclass
class OVRProjectionResult:
    posterior: np.ndarray
    log_scores: np.ndarray
    fitted_ovr_lr: np.ndarray
    rmse_logLR: float
    success: bool
    message: str
    diagnostics: dict

    # Retained notebook result contracts, backed by the same calculation.
    @property
    def ovr_lr_fitted(self):
        return self.fitted_ovr_lr

    @property
    def lr_vs_baseline(self):
        return representable_exp(self.log_scores, "baseline likelihood weights")

    @property
    def rmse(self):
        return self.rmse_logLR

    @property
    def nfev(self):
        return self.diagnostics["nfev"]


def representable_exp(log_values, name):
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        values = np.exp(log_values)
    if not np.all(np.isfinite(values)) or np.any(values == 0):
        raise ValueError(
            f"{name} are outside the supported positive float64 numerical range."
        )
    return values


def model_log_ovr(priors, scores):
    """Direct complementary log-sums; no total-minus-dominant subtraction/floors."""
    logp = np.log(priors)
    z = logp + scores
    return np.array(
        [
            scores[k] + logsumexp(np.delete(logp, k)) - logsumexp(np.delete(z, k))
            for k in range(len(priors))
        ]
    )


def model_jacobian(priors, scores, free_idx):
    z = np.log(priors) + scores
    jac = np.eye(len(priors))
    for k in range(len(priors)):
        others = np.arange(len(priors)) != k
        jac[k, others] = -np.exp(z[others] - logsumexp(z[others]))
    return jac[:, free_idx]


def _validate_ovr(priors, ovr_lr, weights, reg, baseline):
    p = normalize_priors(priors, ovr=True)
    lr = float_vector(ovr_lr, "ovr_lr", 2)
    if lr.shape != p.shape or np.any(lr <= 0):
        raise ValueError("ovr_lr must be strictly positive and match priors shape.")
    w = np.ones_like(p) if weights is None else float_vector(weights, "weights", 2)
    if w.shape != p.shape or np.any(w <= 0):
        raise ValueError("weights must be strictly positive and match priors shape.")
    try:
        if not np.isscalar(reg):
            raise ValueError
        reg = float(reg)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("reg must be a finite nonnegative scalar.") from exc
    if not np.isfinite(reg) or reg < 0:
        raise ValueError("reg must be finite and nonnegative.")
    if baseline is None:
        baseline = int(np.argmax(p))
    if isinstance(baseline, (bool, np.bool_)) or not isinstance(baseline, Integral):
        raise ValueError("baseline must be an integer class index.")
    if not 0 <= baseline < len(p):
        raise ValueError("baseline must be within the class index bounds.")
    return p, lr, w, float(reg), int(baseline)


def ovr_project_posterior(
    priors,
    ovr_lr,
    reg=1e-6,
    weights=None,
    baseline=None,
    *,
    max_nfev=200,
    ftol=1e-10,
    xtol=1e-10,
    gtol=1e-10,
):
    """Fit one coherent candidate at the normalized reference prior.

    With baseline=None, use the first class with the largest normalized prior.
    Positive ridge depends on that choice; reg=0 removes the penalty. Optional
    weights are positive residual-loss weights, not calibrated precisions.
    Boundary/range errors raise ValueError; optimizer failures retain diagnostics.
    """
    p, lr, w, reg, baseline = _validate_ovr(priors, ovr_lr, weights, reg, baseline)
    free = np.array([k for k in range(len(p)) if k != baseline])
    logp = np.log(p)
    rest = np.array([logsumexp(np.delete(logp, k)) for k in range(len(p))])
    target = np.log(lr)
    logq0 = -np.logaddexp(0.0, -(logp - rest + target))
    s0 = logq0 - logp
    s0 -= s0[baseline]

    def unpack(theta):
        s = np.zeros_like(p)
        s[free] = theta
        return s

    def residual_and_jac(theta):
        scores = unpack(theta)
        residual = np.sqrt(w) * (model_log_ovr(p, scores) - target)
        jac = np.sqrt(w)[:, None] * model_jacobian(p, scores, free)
        if reg > 0:
            residual = np.r_[residual, np.sqrt(reg) * theta]
            jac = np.vstack([jac, np.sqrt(reg) * np.eye(len(free))])
        return residual, jac

    fit = least_squares(
        lambda t: residual_and_jac(t)[0],
        s0[free],
        jac=lambda t: residual_and_jac(t)[1],
        method="trf",
        max_nfev=max_nfev,
        ftol=ftol,
        xtol=xtol,
        gtol=gtol,
    )
    scores = unpack(fit.x)
    fitted_log = model_log_ovr(p, scores)
    fitted_lr = representable_exp(fitted_log, "fitted OVR LRs")
    q = common_reference_posterior(p, scores)
    residual = fitted_log - target
    data_sse = float(np.sum(w * residual**2))
    penalty = float(reg * np.sum(scores[free] ** 2))
    symmetric = bool(
        np.all(p == p[0]) and np.all(lr == lr[0]) and np.all(w == w[0]) and lr[0] != 1
    )
    status = (
        "symmetric_inconsistent"
        if symmetric
        else ("coherent_candidate" if fit.success else "optimizer_failed")
    )
    message = (
        "Symmetric inconsistent inputs: coherent candidate only; the loss may favor "
        "asymmetry and a minimum is not established. "
        if symmetric
        else ""
    ) + str(fit.message)
    return OVRProjectionResult(
        q,
        scores,
        fitted_lr,
        float(np.sqrt(np.mean(residual**2))),
        bool(fit.success and not symmetric),
        message,
        {
            "baseline": baseline,
            "K": len(p),
            "priors": p,
            "input_ovr_lr": lr,
            "sum_q_init": float(np.exp(logq0).sum()),
            "fitted_log_ovr_lr": fitted_log,
            "weighted_data_sse": data_sse,
            "ridge_penalty": penalty,
            "objective_final": 0.5 * (data_sse + penalty),
            "fit_status": status,
            "optimizer_terminated": bool(fit.success),
            "coherent": True,
            "minimum_verified": False,
            "optimality": float(fit.optimality),
            "nfev": int(fit.nfev),
            "optimizer_status": int(fit.status),
        },
    )


def project_ovr_to_coherent(
    priors,
    ovr_lr,
    weights=None,
    baseline=None,
    reg=0.0,
    max_nfev=200,
    ftol=1e-10,
    xtol=1e-10,
    gtol=1e-10,
):
    """Adapter for the retained continuous notebook's reg=0 default."""
    return ovr_project_posterior(
        priors,
        ovr_lr,
        reg,
        weights,
        baseline,
        max_nfev=max_nfev,
        ftol=ftol,
        xtol=xtol,
        gtol=gtol,
    )


def _project_ovr_to_coherent(
    priors,
    ovr_lr,
    weights=None,
    baseline=None,
    reg=1e-6,
    max_nfev=200,
    ftol=1e-10,
    xtol=1e-10,
    gtol=1e-10,
):
    """Adapter for the retained qualitative notebook's argument order."""
    return project_ovr_to_coherent(
        priors, ovr_lr, weights, baseline, reg, max_nfev, ftol, xtol, gtol
    )


def require_candidate(result):
    """Only a known, explicitly labeled symmetry candidate may bypass success."""
    if (
        not result.success
        and result.diagnostics.get("fit_status") != "symmetric_inconsistent"
    ):
        raise ValueError(result.message)
    print(
        "Coherent fit candidate; minimum not verified. "
        f"Optimizer terminated: {result.diagnostics['optimizer_terminated']} | "
        f"data RMSE (natural-log LR): {result.rmse_logLR:.6g}"
    )
    print(result.message)
    print(
        f"Baseline index: {result.diagnostics['baseline']} | "
        f"sum of independent binary slices: {result.diagnostics['sum_q_init']:.6g}"
    )
    print(
        f"Weighted data SSE: {result.diagnostics['weighted_data_sse']:.6g} | "
        f"ridge penalty: {result.diagnostics['ridge_penalty']:.6g} | "
        f"objective (half-sum): {result.diagnostics['objective_final']:.6g}"
    )
    return result
