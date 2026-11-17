import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pandas as pd
from survey import pool, analyze


class SurveyTests(unittest.TestCase):
    def test_rubin(self):
        q,se,_,cov,_,_ = pool([[1.],[3.]], [[[4.]],[[4.]]])
        np.testing.assert_allclose(q,[2.])
        np.testing.assert_allclose(cov,[[7.]])
        np.testing.assert_allclose(se,[np.sqrt(7)])

    def test_country_independence_and_gap(self):
        rng = np.random.default_rng(1)
        n=60
        g=np.tile([0,1],n//2)
        e=rng.normal(size=n)
        y=500-25*g+10*e+rng.normal(0,20,n)
        d=pd.DataFrame({'_tutoring':g,'ESCS':e,'CNT':np.repeat(['A','B'],n//2),'w':np.ones(n)})
        for i in range(1,11):
            d[f'p{i}']=y
        d['r1']=np.where(np.arange(n)%3==0,1.5,.5)
        d['r2']=2-d.r1
        args=dict(pv=[f'p{i}' for i in range(1,11)],final='w',replicates=['r1','r2'],country='CNT')
        records,_,cov=analyze(d,**args)
        ix=[r['estimand'] for r in records].index('gap_non_minus_yes')
        full=y[g==0].mean()-y[g==1].mean()
        self.assertAlmostEqual(records[ix]['estimate'],full)
        expected=0.
        for country in ['A','B']:
            for r in ['r1','r2']:
                w=np.where(d.CNT==country,d[r],1.)
                gap=np.average(y[g==0],weights=w[g==0])-np.average(y[g==1],weights=w[g==1])
                expected+=(gap-full)**2/(2*.5**2)
        self.assertAlmostEqual(cov['total'][ix,ix],expected)
        changed=d.copy()
        mask=changed.CNT=='B'
        changed.loc[mask,['r1','r2']]=changed.loc[mask,['r2','r1']].to_numpy()
        _,_,permuted=analyze(changed,**args)
        np.testing.assert_allclose(cov['total'],permuted['total'],rtol=1e-10,atol=1e-10)
        # Arbitrary replicate alignment between independent countries must not matter.
        swapped=d.copy()
        mask=swapped.CNT=='B'
        swapped.loc[mask,['r1','r2']]=d.loc[mask,['r2','r1']].to_numpy()
        _,_,swapped_cov=analyze(swapped,**args)
        np.testing.assert_allclose(cov['total'],swapped_cov['total'],rtol=1e-9,atol=1e-9)

    def test_subsample_has_no_inference(self):
        rng=np.random.default_rng(4)
        d=pd.DataFrame({'_tutoring':np.tile([0,1],20),'ESCS':rng.normal(size=40),'CNT':'A','w':1.,'r':1.})
        for i in range(10):
            d[f'p{i}']=rng.normal(size=40)
        records,_,_=analyze(d,[f'p{i}' for i in range(10)],'w',['r'],'CNT',inference=False)
        self.assertTrue(all(np.isnan(r['se']) and np.isnan(r['p_value']) for r in records))


if __name__=='__main__':
    unittest.main()
