#!/usr/bin/env python3
"""Validate the authored mathematical fixtures using the Python standard library.

This is an oracle for the reference data, not a test of future Manim scenes,
rendered pixels, notebook implementations, or empirical clinical validity.
Default: read ../data/manim_fixtures.json and print a JSON report to stdout.
"""

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys


TOLERANCE = 1e-10
LABELS = ["A", "B", "C"]
MAX_ENTROPY = math.log2(3)
BRIDGE_ALPHAS = [0.0, 0.25, 0.5, 0.75, 1.0]
SWEEP_INTERVALS = 40


def entropy(probabilities):
    """Entropy in bits, including the continuous boundary convention."""
    return -math.fsum(float(p) * math.log2(float(p))
                      for p in probabilities if p > 0)


def divergence(posterior, prior):
    return math.fsum(float(q) * math.log2(float(q / p))
                     for q, p in zip(posterior, prior) if q > 0)


def normalize(values):
    total = sum(values)
    if total <= 0:
        raise ValueError("Normalization requires positive total mass")
    return [v / total for v in values]


def bayes(prior, likelihood):
    if len(prior) != len(likelihood):
        raise ValueError("Prior and likelihood lengths differ")
    joint = [p * likelihood_i for p, likelihood_i in zip(prior, likelihood)]
    return normalize(joint), sum(joint), joint


def fractions(values):
    return [Fraction(v) for v in values]


def decimal_fraction(value):
    """For authored terminating decimals without a separate exact field."""
    if isinstance(value, bool) or not math.isfinite(float(value)):
        raise ValueError("Expected a finite numeric value")
    return Fraction(str(value))


def barycentric(probabilities):
    a, b, c = map(float, probabilities)
    return [(c - b) / 2, math.sqrt(3) * a / 2]


def inverse_barycentric(point):
    x, y = point
    a = 2 * y / math.sqrt(3)
    return [a, (1 - a) / 2 - x, (1 - a) / 2 + x]


def softmax(log_weights):
    maximum = max(log_weights)
    weights = [math.exp(v - maximum) for v in log_weights]
    return normalize(weights)


def likelihood_bridge(prior, likelihood, alpha):
    return softmax([math.log(float(p)) + alpha * math.log(float(l))
                    for p, l in zip(prior, likelihood)])


def geometric_bridge(prior, posterior, alpha):
    return softmax([(1 - alpha) * math.log(float(p)) + alpha * math.log(float(q))
                    for p, q in zip(prior, posterior)])


def short(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [short(v) for v in value]
    return value


class Oracle:
    def __init__(self):
        self.results = {}
        self.goal = None

    def begin(self, goal):
        self.goal = goal
        self.results[goal] = {
            "checks": 0, "passed": 0, "failed": 0,
            "groups": defaultdict(lambda: {"checks": 0, "passed": 0, "failed": 0}),
            "errors": [], "details": {},
        }

    def check(self, group, name, condition, detail=""):
        result = self.results[self.goal]
        status = "passed" if condition else "failed"
        result["checks"] += 1
        result[status] += 1
        result["groups"][group]["checks"] += 1
        result["groups"][group][status] += 1
        if not condition:
            result["errors"].append({"group": group, "check": name, "detail": detail})
        return bool(condition)

    def exact(self, group, name, actual, expected):
        return self.check(group, name, actual == expected,
                          f"expected {short(expected)!r}; got {short(actual)!r}")

    def near(self, group, name, actual, expected):
        a, e = float(actual), float(expected)
        ok = math.isfinite(a) and math.isfinite(e) and abs(a - e) <= TOLERANCE
        return self.check(group, name, ok,
                          f"expected {e:.17g}; got {a:.17g}; absolute tolerance {TOLERANCE:g}")

    def vector(self, group, name, actual, expected):
        if len(actual) != len(expected):
            return self.check(group, name, False,
                              f"expected length {len(expected)}; got {len(actual)}")
        pairs = [(float(a), float(e)) for a, e in zip(actual, expected)]
        finite = all(math.isfinite(a) and math.isfinite(e) for a, e in pairs)
        error = max((abs(a - e) for a, e in pairs), default=0) if finite else float("inf")
        return self.check(group, name, finite and error <= TOLERANCE,
                          f"expected {short(expected)!r}; got {short(actual)!r}; "
                          f"maximum absolute error {error:.17g}")

    def distribution(self, group, name, values, positive=True):
        lower = all(float(v) > 0 for v in values) if positive else all(float(v) >= 0 for v in values)
        self.check(group, name + ".support", len(values) == 3 and lower
                   and all(math.isfinite(float(v)) and float(v) <= 1 for v in values),
                   "Expected three finite probabilities in the specified support")
        self.near(group, name + ".sum", sum(values), 1)

    def exact_vector_field(self, group, name, mapping, field):
        values = fractions(mapping[field + "_exact"])
        self.vector(group, name + ".float_matches_exact", mapping[field], values)
        return values

    def exact_scalar_field(self, group, name, mapping, field):
        value = Fraction(mapping[field + "_exact"])
        self.near(group, name + ".float_matches_exact", mapping[field], value)
        return value


def validate_timing(o, goal):
    beats = goal["beats"]
    o.check("authored_timing", "beats_present", bool(beats), "Expected authored beat intervals")
    o.exact("authored_timing", "unique_beat_ids", len({b["beat_id"] for b in beats}), len(beats))
    previous = 0
    for b in beats:
        o.near("authored_timing", b["beat_id"] + ".contiguous_start", b["start"], previous)
        o.check("authored_timing", b["beat_id"] + ".positive_duration",
                math.isfinite(b["end"]) and b["end"] > b["start"], "Beat duration must be positive")
        previous = b["end"]
    o.near("authored_timing", "timeline_matches_nominal", previous, goal["nominal_duration_seconds"])
    low, high = goal["allowed_total_duration_seconds"]
    o.check("authored_timing", "nominal_within_allowed_range", low <= previous <= high)
    if "minimum_final_hold_seconds" in goal:
        o.check("authored_timing", "final_beat_has_hold_budget",
                beats[-1]["end"] - beats[-1]["start"] >= goal["minimum_final_hold_seconds"],
                "This checks the authored budget, not an actual rendered hold")


def validate_goal_01(o, data):
    g = data["goal_01"]
    validate_timing(o, g)
    p = o.exact_vector_field("exact_encodings", "prior", g, "prior")
    o.distribution("probability_domains", "prior", p)
    o.exact("rational_bayes", "prior_sum_exact", sum(p), Fraction(1))
    o.near("entropy", "prior_entropy", g["prior_entropy_bits"], entropy(p))
    branches = {b["outcome"]: b for b in g["branches"]}
    o.exact("binary_model", "outcome_set", sorted(branches), ["E", "not_E"])
    o.exact("binary_model", "two_branches", len(g["branches"]), 2)
    computed = {}
    for label, b in branches.items():
        l = o.exact_vector_field("exact_encodings", label + ".likelihood", b, "likelihood")
        joint_stored = o.exact_vector_field("exact_encodings", label + ".joint", b, "joint_masses")
        z_stored = o.exact_scalar_field("exact_encodings", label + ".probability", b, "probability")
        q_stored = o.exact_vector_field("exact_encodings", label + ".posterior", b, "posterior")
        o.check("probability_domains", label + ".likelihood_support", len(l) == 3 and all(0 < x < 1 for x in l))
        q, z, joint = bayes(p, l)
        o.exact("rational_bayes", label + ".joint_identity", joint_stored, joint)
        o.exact("rational_bayes", label + ".marginal_identity", z_stored, z)
        o.exact("rational_bayes", label + ".posterior_identity", q_stored, q)
        o.distribution("probability_domains", label + ".posterior", q_stored)
        o.near("entropy", label + ".posterior_entropy", b["entropy_bits"], entropy(q))
        computed[label] = (l, q, z)
    l1, q1, z1 = computed["E"]
    l0, q0, z0 = computed["not_E"]
    o.exact("binary_model", "likelihoods_complement", [a + b for a, b in zip(l1, l0)], [Fraction(1)] * 3)
    o.exact("binary_model", "branch_probabilities_sum", z1 + z0, Fraction(1))
    average = [z1 * a + z0 * b for a, b in zip(q1, q0)]
    o.exact("binary_model", "posterior_average_exact", average, p)
    o.vector("binary_model", "stored_posterior_average", g["weighted_average_posterior"], average)
    expected_h = float(z1) * entropy(q1) + float(z0) * entropy(q0)
    gain = entropy(p) - expected_h
    expected_kl = float(z1) * divergence(q1, p) + float(z0) * divergence(q0, p)
    o.near("expected_information", "expected_entropy", g["expected_posterior_entropy_bits"], expected_h)
    o.near("expected_information", "expected_gain", g["expected_information_gain_bits"], gain)
    o.near("expected_information", "entropy_KL_identity", gain, expected_kl)
    o.check("expected_information", "nonnegative_expected_gain", gain >= -TOLERANCE)
    observed = computed[g["observed_outcome"]][1]
    increase = entropy(observed) - entropy(p)
    o.near("observed_information", "stored_entropy_increase", g["observed_entropy_increase_bits"], increase)
    o.check("observed_information", "observed_entropy_increases", increase > TOLERANCE)
    o.results[o.goal]["details"] = {"binary_outcomes_checked": 2,
        "observed_branch_probability": float(computed[g["observed_outcome"]][2]),
        "expected_information_gain_bits": gain, "observed_entropy_increase_bits": increase}


def validate_goal_02(o, data):
    g = data["goal_02"]
    validate_timing(o, g)
    lr = decimal_fraction(g["likelihood_ratio"])
    inv = Fraction(1) / lr
    o.check("binary_contract", "positive_LR", lr > 0)
    o.near("inverse_updates", "reciprocal_LR", g["inverse_likelihood_ratio"], inv)
    o.exact("binary_contract", "separate_binary_models", g["examples_are_separate_binary_models"], True)
    axes = g["axes"]
    o.vector("common_axes", "probability_range", axes["probability"], [0, 1])
    for axis, bounds in axes.items():
        o.check("common_axes", axis + ".finite_increasing_bounds",
                len(bounds) == 2 and all(math.isfinite(x) for x in bounds) and bounds[1] > bounds[0])
    log_displacements, probability_changes, odds_changes = [], [], []
    o.exact("binary_contract", "example_count", len(g["examples"]), 3)
    for example in g["examples"]:
        name = example["example_id"]
        pb = o.exact_scalar_field("exact_encodings", name + ".p_before", example, "p_before")
        pa = o.exact_scalar_field("exact_encodings", name + ".p_after", example, "p_after")
        ob = o.exact_scalar_field("exact_encodings", name + ".odds_before", example, "odds_before")
        oa = o.exact_scalar_field("exact_encodings", name + ".odds_after", example, "odds_after")
        o.check("binary_contract", name + ".open_probability_support", 0 < pb < 1 and 0 < pa < 1)
        o.exact("rational_updates", name + ".prior_odds", ob, pb / (1 - pb))
        o.exact("rational_updates", name + ".odds_multiplier", oa, ob * lr)
        o.exact("rational_updates", name + ".posterior_probability", pa, oa / (1 + oa))
        direct = pb * lr / (1 - pb + pb * lr)
        o.exact("rational_updates", name + ".direct_probability_formula", pa, direct)
        back_odds = oa * inv
        o.exact("inverse_updates", name + ".inverse_odds", back_odds, ob)
        o.exact("inverse_updates", name + ".inverse_probability", back_odds / (1 + back_odds), pb)
        zb, za = math.log(float(ob)), math.log(float(oa))
        o.near("log_coordinates", name + ".log_before", example["log_odds_before"], zb)
        o.near("log_coordinates", name + ".log_after", example["log_odds_after"], za)
        o.near("log_coordinates", name + ".additive_evidence", za - zb, math.log(float(lr)))
        o.near("inverse_updates", name + ".inverse_log_translation", za + math.log(float(inv)), zb)
        changes = {"probability": float(pa - pb), "odds": float(oa - ob), "log_odds": za - zb}
        endpoints = {"probability": [float(pb), float(pa)], "odds": [float(ob), float(oa)], "log_odds": [zb, za]}
        for axis, change in changes.items():
            o.near("coordinate_changes", name + "." + axis, example[axis + "_change"], change)
            low, high = axes[axis]
            o.check("common_axes", name + "." + axis + ".within_fixed_axis",
                    all(low - TOLERANCE <= v <= high + TOLERANCE for v in endpoints[axis]))
            normalized = change / (high - low)
            o.near("screen_displacements", name + "." + axis,
                   example["screen_displacement_per_axis_width"][axis], normalized)
        log_displacements.append(changes["log_odds"] / (axes["log_odds"][1] - axes["log_odds"][0]))
        probability_changes.append(changes["probability"])
        odds_changes.append(changes["odds"])
    o.vector("screen_displacements", "equal_log_axis_displacement", log_displacements, [log_displacements[0]] * 3)
    o.check("coordinate_changes", "probability_changes_are_not_equal",
            max(probability_changes) - min(probability_changes) > TOLERANCE)
    o.check("coordinate_changes", "odds_changes_are_not_equal", max(odds_changes) - min(odds_changes) > TOLERANCE)
    o.results[o.goal]["details"] = {"separate_binary_examples_checked": 3,
        "common_log_odds_displacement": math.log(float(lr)),
        "common_log_axis_fraction": log_displacements[0]}


def validate_goal_03(o, data):
    g = data["goal_03"]
    validate_timing(o, g)
    o.exact("rectangle_states", "state_inventory", sorted(g["states"]), ["C", "R0", "R1", "R2", "U"])
    o.vector("rectangle_axes", "cumulative_probability_range", g["axes"]["cumulative_probability"], [0, 1])
    o.vector("rectangle_axes", "entropy_range", g["axes"]["entropy_bits"], [0, MAX_ENTROPY])
    states = {}
    for name, state in g["states"].items():
        p = o.exact_vector_field("exact_encodings", name, state, "p")
        o.distribution("rectangle_states", name, p)
        o.exact("rectangle_maps", name + ".exact_width_sum", sum(p), Fraction(1))
        left = [Fraction(0), p[0], p[0] + p[1]]
        right = [x + width for x, width in zip(left, p)]
        o.vector("rectangle_maps", name + ".left_edges", state["rectangle_left_edges"], left)
        o.exact("rectangle_maps", name + ".adjacent_edges", right[:-1], left[1:])
        o.exact("rectangle_maps", name + ".final_right_edge", right[-1], Fraction(1))
        heights = [-math.log2(float(x)) for x in p]
        areas = [float(x) * height for x, height in zip(p, heights)]
        o.vector("rectangle_maps", name + ".surprisal_heights", state["surprisal_bits"], heights)
        o.vector("rectangle_maps", name + ".width_times_height", state["contribution_bits"], areas)
        o.near("rectangle_maps", name + ".total_area_entropy", state["entropy_bits"], math.fsum(areas))
        o.near("entropy", name + ".direct_entropy", state["entropy_bits"], entropy(p))
        lower, upper = g["axes"]["surprisal_bits"]
        o.check("rectangle_axes", name + ".heights_fit_axis", all(lower <= h <= upper for h in heights))
        states[name] = p
    o.near("entropy", "uniform_maximum", g["states"]["U"]["entropy_bits"], MAX_ENTROPY)
    sweep = g["parameter_sweep"]
    start, end = decimal_fraction(sweep["p_A_start"]), decimal_fraction(sweep["p_A_end"])
    o.check("sweep", "sweep_domain", 0 < end < start < Fraction(1, 3))
    o.exact("sweep", "B_C_rule", sweep["B_and_C_rule"], "(1-p_A)/2")
    samples = []
    for index in range(SWEEP_INTERVALS + 1):
        alpha = Fraction(index, SWEEP_INTERVALS)
        a = start + alpha * (end - start)
        p = [a, (1 - a) / 2, (1 - a) / 2]
        o.exact("sweep", f"sample_{index}.exact_sum", sum(p), Fraction(1))
        h_a = -math.log2(float(a))
        area_a = float(a) * h_a
        h = entropy(p)
        # Independent binary-entropy decomposition of this symmetric family.
        binary_h = -float(a) * math.log2(float(a)) - float(1 - a) * math.log2(float(1 - a))
        o.near("sweep", f"sample_{index}.entropy_decomposition", h, binary_h + float(1 - a))
        o.check("sweep", f"sample_{index}.height_fits_axis", h_a <= g["axes"]["surprisal_bits"][1])
        samples.append((p, h_a, area_a, h))
    o.exact("sweep", "start_matches_R1", samples[0][0], states[sweep["start_state"]])
    o.exact("sweep", "end_matches_R2", samples[-1][0], states[sweep["end_state"]])
    o.check("sweep", "rare_category_height_increases", all(a[1] < b[1] for a, b in zip(samples, samples[1:])))
    o.check("sweep", "rare_category_area_decreases", all(a[2] > b[2] for a, b in zip(samples, samples[1:])))
    o.check("sweep", "total_entropy_decreases", all(a[3] > b[3] for a, b in zip(samples, samples[1:])))
    update = g["observed_update"]
    likelihood = [decimal_fraction(v) for v in update["likelihood"]]
    q, z, _ = bayes(states[update["prior_state"]], likelihood)
    o.exact("observed_bayes", "C_to_R0", q, states[update["posterior_state"]])
    o.check("observed_bayes", "observed_update_increases_entropy",
            entropy(q) > entropy(states[update["prior_state"]]))
    goal1_e = next(b for b in data["goal_01"]["branches"] if b["outcome"] == "E")
    o.exact("cross_goal_consistency", "prior_matches_goal01", states["C"], fractions(data["goal_01"]["prior_exact"]))
    o.exact("cross_goal_consistency", "likelihood_matches_goal01", likelihood, fractions(goal1_e["likelihood_exact"]))
    o.exact("cross_goal_consistency", "posterior_matches_goal01", q, fractions(goal1_e["posterior_exact"]))
    o.exact("cross_goal_consistency", "branch_probability_matches_goal01", z, Fraction(goal1_e["probability_exact"]))
    o.results[o.goal]["details"] = {"rectangle_states_checked": len(states),
        "sweep_parameter_samples_checked": len(samples),
        "sweep_is_hypothetical_distribution_change": True}


def validate_atlas_geometry(o, g):
    geometry = g["geometry"]
    expected = {"A": [0, math.sqrt(3) / 2], "B": [-0.5, 0], "C": [0.5, 0]}
    for name, vertex in expected.items():
        o.vector("geometry", name + ".vertex", geometry[name], vertex)
    for first, second in [("A", "B"), ("B", "C"), ("C", "A")]:
        distance = math.sqrt(math.fsum((a - b) ** 2 for a, b in zip(geometry[first], geometry[second])))
        o.near("geometry", first + second + ".unit_side", distance, 1)
    reference_points = [[1, 0, 0], [0, 1, 0], [0, 0, 1],
                        [Fraction(1, 3)] * 3, [0.5, 0.5, 0], [0, 0.5, 0.5], [0.5, 0, 0.5], [0.2, 0.3, 0.5]]
    for index, p in enumerate(reference_points):
        point = barycentric(p)
        o.vector("geometry", f"reference_{index}.inverse", inverse_barycentric(point), p)
        h = entropy(p)
        o.check("heatmap", f"reference_{index}.entropy_range", -TOLERANCE <= h <= MAX_ENTROPY + TOLERANCE)
        if index < 3:
            o.near("heatmap", f"vertex_{index}.zero_entropy", h, 0)
        if index == 3:
            o.near("heatmap", "centroid.maximum_entropy", h, MAX_ENTROPY)
    o.near("heatmap", "minimum", g["entropy"]["minimum"], 0)
    o.near("heatmap", "maximum", g["entropy"]["maximum"], MAX_ENTROPY)
    o.exact("heatmap", "base", g["entropy"]["base"], 2)
    o.exact("heatmap", "unit", g["entropy"]["unit"], "bits")
    o.vector("trace_axes", "finding_indices", g["entropy_trace_axes"]["observed_finding_index"], [0, 4])
    low, high = g["entropy_trace_axes"]["entropy_bits"]
    o.near("trace_axes", "entropy_lower_bound", low, 0)
    o.check("trace_axes", "ceiling_covers_all_three_class_entropies", high >= MAX_ENTROPY)


def validate_goal_04(o, data):
    g = data["goal_04"]
    validate_timing(o, g)
    o.exact("model_contract", "category_order", g["categories"]["labels"], LABELS)
    for key in ["mutually_exclusive", "exhaustive", "fixed_across_states_and_windows"]:
        o.exact("model_contract", key, g["categories"][key], True)
    cases = {case["case_id"]: case for case in g["cases"]}
    expected_names = ["convergence", "persistent_ambiguity", "reopening", "substitution"]
    o.exact("model_contract", "case_inventory", sorted(cases), expected_names)
    o.exact("model_contract", "case_count", len(g["cases"]), 4)
    validate_atlas_geometry(o, g)
    validated = {}
    case_details = {}
    for name, case in cases.items():
        o.exact("model_contract", name + ".labels", case["labels"], LABELS)
        o.exact("model_contract", name + ".conditional_independence", case["conditional_independence_given_diagnosis"], True)
        o.exact("model_contract", name + ".state_count", len(case["states"]), 5)
        o.exact("model_contract", name + ".finding_count", len(case["findings"]), 4)
        states = []
        for index, state in enumerate(case["states"]):
            prefix = f"{name}.state_{index}"
            o.exact("state_structure", prefix + ".index", state["step"], index)
            p = o.exact_vector_field("exact_encodings", prefix, state, "p")
            o.distribution("state_domains", prefix, p)
            o.exact("state_domains", prefix + ".exact_sum", sum(p), Fraction(1))
            o.near("state_entropy", prefix, state["entropy_bits"], entropy(p))
            o.vector("geometry", prefix + ".position", state["barycentric_xy"], barycentric(p))
            o.vector("geometry", prefix + ".inverse", inverse_barycentric(state["barycentric_xy"]), p)
            o.check("trace_axes", prefix + ".entropy_fits_axis",
                    g["entropy_trace_axes"]["entropy_bits"][0] - TOLERANCE <= entropy(p)
                    <= g["entropy_trace_axes"]["entropy_bits"][1] + TOLERANCE)
            states.append(p)
        likelihoods = []
        current = states[0]
        branch_probability = Fraction(1)
        signed_changes = []
        for index, finding in enumerate(case["findings"], 1):
            prefix = f"{name}.finding_{index}"
            o.exact("finding_structure", prefix + ".index", finding["finding_index"], index)
            o.exact("finding_structure", prefix + ".observed_outcome", finding["observed_outcome"], 1)
            l = o.exact_vector_field("exact_encodings", prefix + ".likelihood", finding, "p_observed_given_d")
            complement = o.exact_vector_field("exact_encodings", prefix + ".complement", finding, "p_complement_given_d")
            z_reference = o.exact_scalar_field("exact_encodings", prefix + ".conditional_probability", finding, "p_observed_given_observed_prefix")
            o.check("likelihood_domains", prefix + ".support", len(l) == 3 and all(0 < x <= Fraction(4, 5) for x in l))
            o.exact("binary_models", prefix + ".complement_identity", complement, [1 - x for x in l])
            o.check("likelihood_domains", prefix + ".complement_support", all(0 < x < 1 for x in complement))
            q, z, _ = bayes(current, l)
            o.exact("frozen_likelihood_replay", prefix + ".posterior", q, states[index])
            o.exact("frozen_likelihood_replay", prefix + ".branch_probability", z, z_reference)
            # Check the authored offline construction without using it to drive the replay.
            ratios = [b / a for a, b in zip(states[index - 1], states[index])]
            design_c = Fraction(4, 5) / max(ratios)
            o.exact("offline_design_rule", prefix + ".scale", z_reference, design_c)
            o.exact("offline_design_rule", prefix + ".stored_likelihood", l, [design_c * r for r in ratios])
            qc, zc, _ = bayes(current, complement)
            o.exact("binary_models", prefix + ".branch_sum", z + zc, Fraction(1))
            o.vector("binary_models", prefix + ".complement_posterior", finding["posterior_if_complement"], qc)
            o.near("binary_models", prefix + ".complement_entropy", finding["entropy_if_complement_bits"], entropy(qc))
            o.exact("binary_models", prefix + ".posterior_average", [z * a + zc * b for a, b in zip(q, qc)], current)
            change = entropy(current) - entropy(q)
            expected_gain = entropy(current) - float(z) * entropy(q) - float(zc) * entropy(qc)
            o.near("information_quantities", prefix + ".signed_entropy_reduction", finding["realized_entropy_reduction_bits"], change)
            o.near("information_quantities", prefix + ".KL_direction", finding["posterior_to_prior_kl_bits"], divergence(q, current))
            o.near("information_quantities", prefix + ".expected_entropy_reduction", finding["expected_entropy_reduction_for_binary_test_bits"], expected_gain)
            o.near("information_quantities", prefix + ".expected_KL_identity", expected_gain,
                   float(z) * divergence(q, current) + float(zc) * divergence(qc, current))
            o.check("information_quantities", prefix + ".nonnegative_expected_gain", expected_gain >= -TOLERANCE)
            for alpha in BRIDGE_ALPHAS:
                bridge_name = prefix + f".alpha_{alpha:g}"
                bp = likelihood_bridge(current, l, alpha)
                gp = geometric_bridge(current, q, alpha)
                o.vector("bridges", bridge_name + ".equivalent_formulas", bp, gp)
                o.distribution("bridges", bridge_name, bp)
                o.vector("bridges", bridge_name + ".geometry_roundtrip", inverse_barycentric(barycentric(bp)), bp)
                o.check("bridges", bridge_name + ".entropy_range", -TOLERANCE <= entropy(bp) <= MAX_ENTROPY + TOLERANCE)
                # The trace is a function of this same distribution, not linear interpolation of H.
                geometry_h = entropy(inverse_barycentric(barycentric(bp)))
                o.near("bridge_trace", bridge_name + ".state_entropy_consistency", entropy(bp), geometry_h)
                for a, b in [(0, 1), (0, 2)]:
                    actual = math.log(bp[a] / bp[b])
                    expected = math.log(float(current[a] / current[b])) + alpha * math.log(float(l[a] / l[b]))
                    o.near("bridges", bridge_name + f".pairwise_log_ratio_{a}_{b}", actual, expected)
                if alpha == 0:
                    o.vector("bridge_endpoints", prefix + ".start", bp, current)
                if alpha == 1:
                    o.vector("bridge_endpoints", prefix + ".end", bp, q)
            current = q
            branch_probability *= z
            likelihoods.append(l)
            signed_changes.append(change)
        joint = [states[0][j] * math.prod(l[j] for l in likelihoods) for j in range(3)]
        o.exact("full_path", name + ".product_endpoint", normalize(joint), states[-1])
        o.exact("full_path", name + ".product_evidence", sum(joint), branch_probability)
        reference_branch = o.exact_scalar_field("exact_encodings", name + ".full_branch", case, "probability_of_full_observed_branch")
        o.exact("full_path", name + ".stored_branch_probability", reference_branch, branch_probability)
        reverse = states[0]
        for l in reversed(likelihoods):
            reverse, _, _ = bayes(reverse, l)
        o.exact("full_path", name + ".reverse_order_endpoint", reverse, states[-1])
        net = entropy(states[0]) - entropy(states[-1])
        o.near("full_path", name + ".net_entropy_reduction", case["net_entropy_reduction_bits"], net)
        o.near("full_path", name + ".signed_telescope", math.fsum(signed_changes), net)
        o.near("full_path", name + ".endpoint_KL", case["endpoint_to_initial_kl_bits"], divergence(states[-1], states[0]))
        # Independently enumerate the full fixed conditionally-independent binary model.
        all_outcomes = []
        for outcomes in itertools.product((0, 1), repeat=4):
            mass = [states[0][j] * math.prod(likelihoods[t][j] if e else 1 - likelihoods[t][j]
                                           for t, e in enumerate(outcomes)) for j in range(3)]
            z = sum(mass)
            posterior = normalize(mass)
            outcome_name = "".join(map(str, outcomes))
            o.check("all_outcome_branches", name + "." + outcome_name + ".positive_mass", 0 < z < 1)
            o.exact("all_outcome_branches", name + "." + outcome_name + ".posterior_sum", sum(posterior), Fraction(1))
            o.check("all_outcome_branches", name + "." + outcome_name + ".posterior_support", all(x > 0 for x in posterior))
            all_outcomes.append((outcomes, mass, z, posterior))
        o.exact("all_outcome_branches", name + ".sixteen_branches", len(all_outcomes), 16)
        o.exact("all_outcome_branches", name + ".total_probability", sum(row[2] for row in all_outcomes), Fraction(1))
        o.exact("all_outcome_branches", name + ".marginal_diagnosis",
                [sum(row[1][j] for row in all_outcomes) for j in range(3)], states[0])
        o.exact("all_outcome_branches", name + ".posterior_average",
                [sum(row[2] * row[3][j] for row in all_outcomes) for j in range(3)], states[0])
        chosen = next(row for row in all_outcomes if row[0] == (1, 1, 1, 1))
        o.exact("all_outcome_branches", name + ".displayed_branch_endpoint", chosen[3], states[-1])
        o.exact("all_outcome_branches", name + ".displayed_branch_probability", chosen[2], branch_probability)
        expected_h = math.fsum(float(row[2]) * entropy(row[3]) for row in all_outcomes)
        full_gain = entropy(states[0]) - expected_h
        expected_kl = math.fsum(float(row[2]) * divergence(row[3], states[0]) for row in all_outcomes)
        o.check("all_outcome_branches", name + ".nonnegative_full_expected_gain", full_gain >= -TOLERANCE)
        o.near("all_outcome_branches", name + ".full_expected_KL_identity", full_gain, expected_kl)
        validated[name] = (states, likelihoods)
        case_details[name] = {"states_checked": 5, "fixed_likelihood_rows_replayed": 4,
                              "complete_outcome_branches_checked": 16,
                              "bridge_samples_checked": 4 * len(BRIDGE_ALPHAS),
                              "observed_branch_probability": float(branch_probability),
                              "entropy_sequence_bits": [entropy(p) for p in states],
                              "full_test_expected_information_gain_bits": full_gain}
    h = {name: [entropy(p) for p in states] for name, (states, _) in validated.items()}
    o.check("narrative_trace_properties", "convergence_entropy_strictly_decreases", all(a - b > TOLERANCE for a, b in zip(h["convergence"], h["convergence"][1:])))
    o.check("narrative_trace_properties", "reopening_entropy_strictly_increases", all(b - a > TOLERANCE for a, b in zip(h["reopening"], h["reopening"][1:])))
    substitution = validated["substitution"][0]
    o.exact("narrative_trace_properties", "substitution_start_A", substitution[0][0], Fraction(4, 5))
    o.exact("narrative_trace_properties", "substitution_end_B", substitution[-1][1], Fraction(4, 5))
    o.exact("narrative_trace_properties", "substitution_endpoint_swap", substitution[-1], [substitution[0][1], substitution[0][0], substitution[0][2]])
    o.near("narrative_trace_properties", "substitution_equal_endpoint_entropy", h["substitution"][0], h["substitution"][-1])
    o.check("narrative_trace_properties", "substitution_has_ambiguous_intermediates",
            all(max(substitution[i]) <= Fraction(13, 20) for i in [1, 2]))
    o.check("narrative_trace_properties", "substitution_entropy_not_constant", max(h["substitution"]) - min(h["substitution"]) > TOLERANCE)
    ambiguity = validated["persistent_ambiguity"][0]
    o.check("narrative_trace_properties", "persistent_high_entropy", min(h["persistent_ambiguity"]) > 1.55)
    o.check("narrative_trace_properties", "persistent_no_dominant_category", all(max(p) <= Fraction(2, 5) for p in ambiguity))
    o.exact("narrative_trace_properties", "intentionally_different_initial_priors", len({tuple(s[0]) for s, _ in validated.values()}), 4)
    window_summaries = []
    for window in g["encounter_windows"]:
        name = window["window_id"]
        states, likelihoods = validated[window["case_id"]]
        indices = window["state_indices"]
        a, b = indices[0], indices[-1]
        o.exact("encounter_windows", name + ".contiguous_state_indices", indices, list(range(a, b + 1)))
        o.check("encounter_windows", name + ".valid_limits", 0 <= a < b <= 4)
        o.exact("encounter_windows", name + ".visible_findings", window["visible_finding_indices"], list(range(a + 1, b + 1)))
        o.exact("encounter_windows", name + ".hidden_prefix", window["hidden_prefix_indices"], list(range(1, a + 1)))
        start = states[0]
        for t in window["hidden_prefix_indices"]:
            start, _, _ = bayes(start, likelihoods[t - 1])
        o.exact("encounter_windows", name + ".prefix_retained_in_start", start, states[a])
        current = start
        for t in window["visible_finding_indices"]:
            current, _, _ = bayes(current, likelihoods[t - 1])
            o.exact("encounter_windows", name + f".state_{t}_unchanged", current, states[t])
            o.vector("encounter_windows", name + f".state_{t}_same_geometry", barycentric(current), barycentric(states[t]))
        cropped_h = [entropy(states[t]) for t in indices]
        if name == "reopening_segment":
            o.check("encounter_windows", name + ".entropy_increases", all(x < y for x, y in zip(cropped_h, cropped_h[1:])))
        elif name == "convergence_segment":
            o.check("encounter_windows", name + ".entropy_decreases", all(x > y for x, y in zip(cropped_h, cropped_h[1:])))
        elif name == "whole_path":
            o.near("encounter_windows", name + ".equal_endpoint_entropy", cropped_h[0], cropped_h[-1])
        window_summaries.append({"window_id": name, "state_indices": indices,
                                 "visible_finding_indices": window["visible_finding_indices"],
                                 "net_entropy_reduction_bits": cropped_h[0] - cropped_h[-1]})
    o.exact("encounter_windows", "window_inventory", sorted(w["window_id"] for w in g["encounter_windows"]),
            ["convergence_segment", "reopening_segment", "whole_path"])
    o.results[o.goal]["details"] = {"cases": case_details, "encounter_windows": window_summaries,
        "bridge_alpha_samples": BRIDGE_ALPHAS,
        "bridge_samples_are_illustrative_not_observation_times": True}


def reject_nonfinite_constant(value):
    raise ValueError("JSON contains a nonfinite numeric constant: " + value)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path,
                        default=Path(__file__).resolve().parent.parent / "data" / "manim_fixtures.json",
                        help="Fixture JSON (default: ../data/manim_fixtures.json relative to this script)")
    parser.add_argument("--output-report", type=Path,
                        help="Write the JSON report here instead of stdout")
    args = parser.parse_args(argv)
    oracle = Oracle()
    report = {
        "oracle": "diagnostic_manim_authored_fixture_oracle_v1",
        "scope": "Validates authored mathematical examples and reference metadata only.",
        "not_validated": ["future Manim implementation", "rendered geometry or pixels",
                          "actual animation timing", "notebook or application implementations",
                          "empirical clinical validity"],
        "absolute_tolerance": TOLERANCE,
        "check_count_convention": "Each named scalar, vector, exact rational identity, or predicate is one check; vector components are not separately counted.",
        "fixtures_filename": args.fixtures.name,
        "fixtures_sha256": None,
    }
    try:
        raw = args.fixtures.read_bytes()
        report["fixtures_sha256"] = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw, parse_constant=reject_nonfinite_constant)
        report["fixture_schema_version"] = data.get("schema_version")
    except Exception as exc:
        oracle.begin("fixture_loading")
        message = "Could not read fixture file" if isinstance(exc, OSError) else str(exc)
        oracle.check("input", "load_valid_json", False, type(exc).__name__ + ": " + message)
        data = None
    if data is not None:
        oracle.begin("shared_contract")
        try:
            oracle.exact("schema", "schema_version", data["schema_version"], "diagnostic-manim-fixtures-v1")
            oracle.near("schema", "absolute_tolerance", data["absolute_tolerance"], TOLERANCE)
            oracle.exact("units", "entropy_log_base", data["entropy_log_base"], 2)
            oracle.exact("units", "log_odds_log_base", data["log_odds_log_base"], "e")
            oracle.exact("categories", "category_order", data["category_order"], LABELS)
        except Exception as exc:
            oracle.check("structure", "shared_contract_readable", False, type(exc).__name__ + ": " + str(exc))
        for key, function in [("goal_01", validate_goal_01), ("goal_02", validate_goal_02),
                              ("goal_03", validate_goal_03), ("goal_04", validate_goal_04)]:
            oracle.begin(key)
            try:
                function(oracle, data)
            except Exception as exc:
                oracle.check("structure_or_math", "fixture_validation_completed", False,
                             type(exc).__name__ + ": " + str(exc))
    for result in oracle.results.values():
        result["status"] = "pass" if result["failed"] == 0 else "fail"
        result["groups"] = dict(result["groups"])
    report["results"] = oracle.results
    report["total_checks"] = sum(r["checks"] for r in oracle.results.values())
    report["passed_checks"] = sum(r["passed"] for r in oracle.results.values())
    report["failed_checks"] = sum(r["failed"] for r in oracle.results.values())
    report["status"] = "pass" if report["failed_checks"] == 0 else "fail"
    encoded = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output_report is None:
        sys.stdout.write(encoded)
    else:
        try:
            args.output_report.parent.mkdir(parents=True, exist_ok=True)
            args.output_report.write_text(encoded, encoding="utf-8")
        except OSError as exc:
            print("FAIL: could not write verification report (" + type(exc).__name__ + ")", file=sys.stderr)
            return 2
    if report["failed_checks"]:
        for goal, result in oracle.results.items():
            for error in result["errors"]:
                print(f"FAIL {goal}/{error['group']}/{error['check']}: {error['detail']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
