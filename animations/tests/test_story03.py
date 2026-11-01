import numpy as np
from core.story03 import story
from core.math import bridge, entropy


def test_observed_branch_and_cue_identity():
    data=story()
    np.testing.assert_allclose(data['posterior'],data['states']['R0']['p'],atol=1e-10)
    assert [(x.beat_id,x.start,x.end) for x in data['cues']] == [(x['beat_id'],x['start'],x['end']) for x in data['fixture']['beats']]
    for alpha in [0,.25,.5,.75,1]:
        p=bridge(data['prior'],data['likelihood'],alpha)
        assert np.isclose(p.sum(),1)
        assert np.isfinite(entropy(p))
