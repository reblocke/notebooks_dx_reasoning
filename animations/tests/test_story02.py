import math
import pytest
from core.story02 import story


def test_examples_are_separate_and_derived():
    s=story()
    assert len(s['examples'])==3
    for actual,fixture in zip(s['examples'],s['fixture']['examples']):
        for key, expected in [('posterior','p_after'),('odds_before','odds_before'),
                              ('odds_after','odds_after'),('log_before','log_odds_before'),('log_after','log_odds_after')]:
            assert actual[key] == pytest.approx(fixture[expected],abs=1e-10)
        assert actual['inverse']==pytest.approx(actual['prior'],abs=1e-10)
        assert actual['log_after']-actual['log_before']==pytest.approx(math.log(3),abs=1e-10)
    assert sum(x['prior'] for x in s['examples']) != pytest.approx(1)
