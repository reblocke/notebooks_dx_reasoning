"""Independent rational references for the two newly authored teaching films."""
from fractions import Fraction as F
import json
import math
from pathlib import Path
import pytest
from core.story05 import story as results_story
from core.story06 import story as decision_story
from core.leaf_plots import leaf, logit_point, clipped_log_line
from core.decision_math import utility_difference, thresholds, preference

DATA = Path(__file__).resolve().parents[1]/'data'


def fraction(row):
    answer=F(row['numerator'],row['denominator'])
    assert row['value'] == pytest.approx(float(answer),abs=1e-10,rel=0)
    return answer


def update(p,r):
    return p*r/(1-p+p*r)


def test_test_profiles_reconstruct_counts_and_both_result_updates():
    actual=results_story()['profiles']
    fixture=json.loads((DATA/'test_results_fixtures.json').read_text())['goal_05']
    expected={'B':(F(1,50),F(99,100),F(2),F(98,99)),
              'A':(F(99,100),F(1,50),F(99,98),F(1,2)),
              'C':(F(4,5),F(23,25),F(10),F(5,23))}
    for row in fixture['profiles']:
        se,sp,lp,lm=expected[row['id']];computed=actual[row['id']]
        assert fraction(row['sensitivity'])==se
        assert fraction(row['specificity'])==sp
        assert se/(1-sp)==lp and (1-se)/sp==lm
        for field,value in [('lr_positive',lp),('lr_negative',lm)]:
            assert fraction(row[field])==value
            assert computed[field]==pytest.approx(float(value),abs=1e-10,rel=0)
        if row['id']!='C':
            counts=row['counts']
            for key,value in [('disease_positive',100*se),('disease_negative',100*(1-se)),
                              ('no_disease_positive',900*(1-sp)),('no_disease_negative',900*sp)]:
                assert counts[key]==computed['counts'][key]==value
            assert counts['disease_total']==100 and counts['no_disease_total']==900
            assert sum(counts[k] for k in computed['counts'])==counts['population']==1000
        for ref,result in zip(row['examples'],computed['examples']):
            p=fraction(ref['prior'])
            for kind,r in [('positive',lp),('negative',lm)]:
                q=update(p,r)
                assert fraction(ref['posterior_'+kind])==q
                assert result[kind]==pytest.approx(float(q),abs=1e-10,rel=0)
    assert F(2,9)!=2 and F(1,18)!=F(1,2)
    assert update(F(1,10),2)==F(2,11)
    assert update(F(1,10),F(1,2))==F(1,19)
    assert [f"{r['positive']:.1%}" for r in actual['C']['examples']]==['9.2%','90.9%']
    assert f"{actual['B']['examples'][0]['positive']:.1%}"=='18.2%'
    assert f"{actual['A']['examples'][0]['negative']:.1%}"=='5.3%'


def test_leaf_and_all_utility_references():
    actual=decision_story();fixture=json.loads((DATA/'beliefs_actions_fixtures.json').read_text())['goal_06']
    for row,result,p in zip(fixture['examples'],actual['examples'],[F(1,10),F(1,2),F(9,10)]):
        plus,minus=update(p,3),update(p,F(1,2))
        values={'prior':p,'positive':plus,'negative':minus,'positive_change':plus-p,
                'utility_prior':5*p-1,'utility_positive':5*plus-1,'utility_negative':5*minus-1,
                'utility_change':5*(plus-p)}
        for key,value in values.items():
            assert fraction(row[key])==value
            if key in result:
                assert result[key]==pytest.approx(float(value),abs=1e-10,rel=0)
        for key,lr in [('log_positive',3),('log_negative',.5)]:
            x,y=result[key]
            assert y-x==pytest.approx(math.log(lr),abs=1e-10,rel=0)
    assert actual['conditional_lr']==2
    assert actual['sequential_posterior']==pytest.approx(.4,abs=1e-10,rel=0)
    assert fixture['conditional_finding']['given']=='first positive result'
    assert fraction(fixture['conditional_finding']['posterior'])==F(2,5)
    for row in fixture['utilities']:
        b,c=row['benefit'],row['cost']
        assert fraction(row['probability_threshold'])==F(c,b+c)
        assert fraction(row['odds_threshold'])==F(c,b)
        assert fraction(row['gain_at_quarter'])==F(b+c,4)-c
    assert utility_difference(.25,4,4)==-2


@pytest.mark.parametrize('cost',[1,4])
def test_action_equivalence_below_at_and_above_threshold(cost):
    t=thresholds(4,cost)
    for p in [i/100 for i in range(1,100)]+[t['probability']]:
        if p==t['probability']:
            assert preference(p,4,cost)=='indifferent'
            assert utility_difference(p,4,cost)==pytest.approx(0,abs=1e-14)
        else:
            assert (p>t['probability'])==(p/(1-p)>t['odds'])
            assert (p>t['probability'])==(math.log(p/(1-p))>t['log_odds'])
            assert (preference(p,4,cost)=='act')==(utility_difference(p,4,cost)>0)


@pytest.mark.parametrize('lr',[.5,1,3])
def test_leaf_boundaries_and_clipped_slope_one_lines(lr):
    assert leaf(0,lr)==0 and leaf(1,lr)==1
    for i in range(1,100):
        p=i/100;q=leaf(p,lr)
        assert 0<q<1
        x,y=logit_point(p,lr)
        assert y==pytest.approx(x+math.log(lr),abs=1e-10,rel=0)
    first,last=clipped_log_line(lr)
    assert all(-4<=v<=4 for point in (first,last) for v in point)
    assert last[1]-first[1]==pytest.approx(last[0]-first[0])
    for p in (0,1):
        with pytest.raises(ValueError):logit_point(p,lr)


@pytest.mark.parametrize('benefit,cost',[(0,1),(4,0),(-1,1),(4,float('nan'))])
def test_invalid_payoffs_rejected(benefit,cost):
    with pytest.raises(ValueError):thresholds(benefit,cost)
