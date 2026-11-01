import itertools
import numpy as np
from core.story04 import story
from core.math import bayes_update, bridge, entropy, from_barycentric, to_barycentric
from core.atlas_geometry import heat_value, position, trace_position


def test_atlas_fixed_models_and_all_binary_sequences():
    model = story()
    for case in model['cases'].values():
        prior = case['states'][0]
        likelihoods = case['likelihoods']
        total = 0
        for outcomes in itertools.product((0, 1), repeat=4):
            joint = prior.copy()
            for event, likelihood in zip(outcomes, likelihoods):
                joint *= likelihood if event else 1-likelihood
            total += joint.sum()
        assert np.isclose(total, 1)
        p = prior
        for likelihood in reversed(likelihoods):
            p = bayes_update(p, likelihood).posterior
        np.testing.assert_allclose(p, case['states'][-1], atol=1e-12)
        for i, likelihood in enumerate(likelihoods):
            for alpha in (0, .25, .5, .75, 1):
                p = bridge(case['states'][i], likelihood, alpha)
                assert np.all(p > 0) and np.isclose(p.sum(), 1)
                np.testing.assert_allclose(from_barycentric(to_barycentric(p)), p, atol=1e-12)
            np.testing.assert_allclose(p, case['states'][i+1], atol=1e-12)
    cases=model['cases']
    assert np.all(np.diff([entropy(p) for p in cases['convergence']['states']]) < 0)
    assert np.all(np.diff([entropy(p) for p in cases['reopening']['states']]) > 0)
    s=cases['substitution']['states']
    assert np.isclose(entropy(s[0]), entropy(s[-1])) and entropy(s[2]) > entropy(s[0])
    assert all(entropy(p)>1.55 and max(p)<=.4+1e-12 for p in cases['persistent_ambiguity']['states'])
    assert all(np.allclose(s[i], cases['substitution']['states'][i]) for i in (0,2,4))


def test_fixed_geometry_and_heat_scale():
    assert np.isclose(heat_value([1/3]*3),1)
    for p in ([1,0,0],[0,1,0],[0,0,1]): assert heat_value(p)==0
    assert np.isclose(np.linalg.norm(position([1,0,0])-position([0,1,0])),3.8)
    assert np.allclose(trace_position(0,0), [1.4,-1.75,0])
    assert np.allclose(trace_position(4,1.65), [5.6,-.25,0])
