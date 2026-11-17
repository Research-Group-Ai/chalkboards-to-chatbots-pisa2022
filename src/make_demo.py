
import json
from pathlib import Path
import numpy as np
import pandas as pd


def main():
    rng = np.random.default_rng(20261117)
    n = 1200
    g = rng.integers(0,2,n)
    escs = rng.normal(size=n)
    latent = 450 - 20*g + 35*escs + rng.normal(0,70,n)
    d = pd.DataFrame(dict(CNT=np.repeat(['DEMO_A','DEMO_B','DEMO_C'], n//3),
                          CNTSTUID=np.arange(n), ST297Q03JA=np.where(g,1,2),
                          ESCS=escs, W_FSTUWT=rng.uniform(1,3,n)))
    for i in range(1,11):
        d[f'PV{i}MATH'] = latent+rng.normal(0,15,n)
    for i in range(1,81):
        d[f'W_FSTURWT{i}'] = d.W_FSTUWT*rng.choice([.5,1.5],n)
    Path('data').mkdir(exist_ok=True)
    d.to_csv('data/synthetic_demo.csv', index=False)
    c = json.loads(Path('configs/analysis.json').read_text())
    c.update(response_codes_verified=True, yes_code=1, no_code=2, synthetic_demo=True)
    Path('configs/demo.json').write_text(json.dumps(c, indent=2))
    print('Created artificial data and configs/demo.json; not a valid PISA survey design.')


if __name__ == '__main__':
    main()
