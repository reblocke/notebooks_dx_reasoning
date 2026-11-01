"""Production functions checked against authored, independent scientific fixtures."""
import json
import math
from pathlib import Path

import numpy as np
import pytest

from core import math as dm

FIXTURES = json.loads((Path(__file__).resolve().parents[1] / 'data/manim_fixtures.json').read_text())


def test_binary_model_branches_and_expected_entropy():
    f = FIXTURES['goal_01']
    prior = np.asarray(f['prior'])
    branches = [dm.bayes_update(prior, b['likelihood']) for b in f['branches']]
    for actual, expected in zip(branches, f['branches']):
        np.testing.assert_allclose(actual.joint, expected['joint_masses'], atol=1e-10)
        np.testing.assert_allclose(actual.posterior, expected['posterior'], atol=1e-10)
        assert actual.evidence_probability == pytest.approx(expected['probability'], abs=1e-10)
        assert dm.entropy(actual.posterior) == pytest.approx(expected['entropy_bits'], abs=1e-10)
    assert dm.entropy(prior) == pytest.approx(f['prior_entropy_bits'], abs=1e-10)
    expected_h = dm.expected_posterior_entropy(prior, f['branches'][0]['likelihood'])
    assert expected_h == pytest.approx(f['expected_posterior_entropy_bits'], abs=1e-10)
    assert dm.entropy(prior) - expected_h == pytest.approx(f['expected_information_gain_bits'], abs=1e-10)
    with pytest.raises(ValueError, match='sum to one'):
        dm.entropy(branches[0].joint)


def test_entropy_and_bad_inputs():
    assert dm.entropy([1, 0, 0]) == 0
    assert dm.entropy([1/3]*3) == pytest.approx(math.log2(3), abs=1e-10)
    for p in ([.2,.3], [-.1,1.1], [float('nan'),1], [[.5,.5]]):
        with pytest.raises(ValueError): dm.entropy(p)
    for p, likelihood in [([.5,.5], [.1]), ([.5,.5], [-.1,.2]), ([.5,.5], [0,0]), ([.5,.5], [float('inf'),1])]:
        with pytest.raises(ValueError): dm.bayes_update(p, likelihood)
    with pytest.raises(ValueError): dm.expected_posterior_entropy([.5,.5],[.2,1.1])


def test_binary_coordinates_and_inverse():
    for case in FIXTURES['goal_02']['examples']:
        p, lr = case['p_before'], FIXTURES['goal_02']['likelihood_ratio']
        assert dm.binary_update(p,lr) == pytest.approx(case['p_after'], abs=1e-10)
        assert dm.binary_update(case['p_after'],1/lr) == pytest.approx(p, abs=1e-10)
        assert dm.probability_odds(p) == pytest.approx(case['odds_before'], abs=1e-10)
        assert dm.log_odds(p) == pytest.approx(case['log_odds_before'], abs=1e-10)
    assert dm.binary_update(0,3)==0
    assert dm.binary_update(1,3)==1
    for p, lr in [(-.1,2),(1.1,2),(.5,0),(.5,float('nan'))]:
        with pytest.raises(ValueError): dm.binary_update(p,lr)


def test_illustrative_bridge_and_geometry():
    for case in FIXTURES['goal_04']['cases']:
        p = np.asarray(case['states'][0]['p'])
        for finding, state in zip(case['findings'], case['states'][1:]):
            likelihood = finding['p_observed_given_d']
            np.testing.assert_allclose(dm.bridge(p,likelihood,0), p, atol=1e-10)
            end = dm.bridge(p,likelihood,1)
            np.testing.assert_allclose(end, state['p'], atol=1e-10)
            for alpha in (.25,.5,.75):
                mid=dm.bridge(p,likelihood,alpha)
                assert np.all(mid>0) and np.sum(mid)==pytest.approx(1)
                np.testing.assert_allclose(dm.from_barycentric(dm.to_barycentric(mid)),mid,atol=1e-10)
            np.testing.assert_allclose(dm.to_barycentric(end),state['barycentric_xy'],atol=1e-10)
            p=end
    for p in [[1,0,0],[0,1,0],[0,0,1],[1/3]*3]:
        np.testing.assert_allclose(dm.from_barycentric(dm.to_barycentric(p)),p,atol=1e-10)
    with pytest.raises(ValueError): dm.bridge([.5,.5],[.1,.9],1.1)
    with pytest.raises(ValueError): dm.from_barycentric([10,10])


def test_atlas_frozen_findings_and_complementary_outcomes():
    for case in FIXTURES['goal_04']['cases']:
        prior = np.asarray(case['states'][0]['p'])
        for event, expected in zip(case['findings'], case['states'][1:]):
            likelihood = np.asarray(event['p_observed_given_d'])
            observed = dm.bayes_update(prior, likelihood)
            complement = dm.bayes_update(prior, 1-likelihood)
            np.testing.assert_allclose(observed.posterior, expected['p'], atol=1e-10)
            np.testing.assert_allclose(complement.posterior, event['posterior_if_complement'], atol=1e-10)
            assert observed.evidence_probability == pytest.approx(event['p_observed_given_observed_prefix'], abs=1e-10)
            assert observed.evidence_probability + complement.evidence_probability == pytest.approx(1, abs=1e-10)
            assert dm.entropy(observed.posterior) == pytest.approx(expected['entropy_bits'], abs=1e-10)
            gain = dm.entropy(prior) - dm.expected_posterior_entropy(prior, likelihood)
            assert gain == pytest.approx(event['expected_entropy_reduction_for_binary_test_bits'], abs=1e-10)
            prior = observed.posterior


def test_entropy_area_reference_states():
    for state in FIXTURES['goal_03']['states'].values():
        p = np.asarray(state['p'])
        heights = -np.log2(p)
        np.testing.assert_allclose(heights, state['surprisal_bits'], atol=1e-10)
        np.testing.assert_allclose(p*heights, state['contribution_bits'], atol=1e-10)
        assert dm.entropy(p) == pytest.approx(state['entropy_bits'], abs=1e-10)


def test_fixed_coordinate_adapter_matches_all_three_representations():
    """Screen coordinates preserve shared scales, including tiny odds movement."""
    f = FIXTURES['goal_02']
    spans = {'probability': (0,1), 'odds': (0,30), 'log_odds': (-3.5,3.5)}
    for kind, domain in spans.items():
        lengths=[]
        for case in f['examples']:
            pair = (case['p_before'], case['p_after']) if kind == 'probability' else (
                (case['odds_before'], case['odds_after']) if kind == 'odds' else
                (case['log_odds_before'], case['log_odds_after']))
            a,b = [dm.axis_coordinate(x, domain, width=7.0, left=-3.5) for x in pair]
            length=b-a
            lengths.append(length)
            assert length / 7 == pytest.approx(case['screen_displacement_per_axis_width'][kind], abs=1e-10)
        if kind == 'log_odds':
            assert max(lengths)-min(lengths) < 14.222/1920
    with pytest.raises(ValueError): dm.axis_coordinate(31,(0,30),width=7,left=0)
    with pytest.raises(ValueError): dm.axis_coordinate(0,(1,1),width=7,left=0)
