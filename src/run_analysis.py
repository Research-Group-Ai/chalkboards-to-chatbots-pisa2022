
import argparse
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import numpy as np
import pandas as pd
from survey import analyze, weighted_quantile


def load(path):
    if path.suffix.lower() == '.csv':
        return pd.read_csv(path)
    if path.suffix.lower() == '.parquet':
        return pd.read_parquet(path)
    if path.suffix.lower() in ['.sav', '.zsav']:
        import pyreadstat
        return pyreadstat.read_sav(path, apply_value_formats=False)[0]
    raise ValueError('Use CSV, Parquet, SAV or ZSAV.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', required=True, type=Path)
    p.add_argument('--config', required=True, type=Path)
    p.add_argument('--output', type=Path, default=Path('outputs/run'))
    args = p.parse_args()
    c = json.loads(args.config.read_text())
    if not c.get('response_codes_verified'):
        raise ValueError('Verify tutoring response codes in the OECD codebook, then set response_codes_verified=true.')
    if c['yes_code'] is None or c['no_code'] is None or c['yes_code'] == c['no_code']:
        raise ValueError('Yes and no response codes must be supplied and differ.')
    if not 0 <= c['fay'] < 1:
        raise ValueError('fay must be in [0, 1).')
    df = load(args.data)
    pv = [f'PV{i}MATH' for i in range(1, 11)]
    rep = [f"{c['replicate_prefix']}{i}" for i in range(1, 81)]
    extra = c.get('numeric_covariates', [])
    cols = [c['country'], c['student_id'], c['tutoring'], 'ESCS', c['final_weight']] + pv + rep + extra
    missing = sorted(set(cols) - set(df))
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    df = df[cols].copy()
    if df.duplicated([c['country'], c['student_id']]).any():
        raise ValueError('Duplicate country/student keys. Merge source files one-to-one before running.')
    n_raw = len(df)
    numeric = list(dict.fromkeys([c['tutoring'], 'ESCS', c['final_weight']] + pv + rep + extra))
    for name in numeric:
        df[name] = pd.to_numeric(df[name], errors='coerce')
        df[name] = df[name].replace(c.get('missing_codes', {}).get(name, []), np.nan)
    valid = df[c['tutoring']].isin([c['yes_code'], c['no_code']])
    df = df.loc[valid].replace([np.inf, -np.inf], np.nan).dropna(subset=cols).copy()
    df = df.loc[(df[c['final_weight']] > 0) & (df[rep] >= 0).all(axis=1)].copy()
    df['_tutoring'] = (df[c['tutoring']] == c['yes_code']).astype(int)
    # Stable sorting makes the seeded sample invariant to source file row order.
    df = df.sort_values([c['country'], c['student_id']]).reset_index(drop=True)
    n_eligible = len(df)
    if not n_eligible:
        raise ValueError('No eligible records remain; check missing values and response coding.')
    allocation = df.groupby(c['country']).size().rename('eligible_n').to_frame()
    n = c.get('sample_n')
    subsampled = n is not None and n < n_eligible
    if n is not None and (not isinstance(n, int) or n <= 0):
        raise ValueError('sample_n must be null or a positive integer.')
    if n is not None and n > n_eligible:
        raise ValueError('Requested sample is larger than the eligible data.')
    if subsampled:
        ideal = allocation.eligible_n * n / n_eligible
        sizes = np.floor(ideal).astype(int)
        remainder = n - sizes.sum()
        for key in (ideal-sizes).sort_values(ascending=False, kind='stable').index[:remainder]:
            sizes.loc[key] += 1
        if (sizes == 0).any():
            raise ValueError('Sample size too small to retain all eligible countries.')
        rng = np.random.default_rng(c['seed'])
        chunks = []
        for key, frame in df.groupby(c['country'], sort=True):
            selected = frame.iloc[rng.choice(len(frame), int(sizes.loc[key]), replace=False)].copy()
            # Inverse second-phase inclusion probability corrects point weights.
            selected[[c['final_weight']] + rep] *= len(frame) / len(selected)
            chunks.append(selected)
        df = pd.concat(chunks, ignore_index=True)
    allocation['selected_n'] = df.groupby(c['country']).size()
    allocation['second_phase_inclusion_probability'] = allocation.selected_n/allocation.eligible_n
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    allocation.to_csv(out/'sampling_audit.csv')
    df[[c['country'], c['student_id']]].to_csv(out/'selected_ids_LOCAL_ONLY.csv', index=False)
    inference = not subsampled
    kwargs = dict(pv=pv, final=c['final_weight'], replicates=rep, country=c['country'],
                  extra=extra, fay=c['fay'], inference=inference)
    overall, by_pv, cov = analyze(df, **kwargs)
    pd.DataFrame(overall).to_csv(out/'overall_estimates.csv', index=False)
    names = [r['estimand'] for r in overall]
    pd.DataFrame(by_pv, columns=names, index=pv).to_csv(out/'per_pv_estimates.csv')
    for key, value in cov.items():
        if inference:
            pd.DataFrame(value, index=names, columns=names).to_csv(out/f'{key}_covariance.csv')
    # Unweighted rank quartiles are an explicit implementation choice; ties are
    # broken by country/student key. Boundaries are held fixed in replication.
    df['_quartile'] = pd.qcut(df.ESCS.rank(method='first'), 4, labels=False)+1
    subgroup = []
    for label, mask in [('Q1', df._quartile == 1), ('Q2-Q3', df._quartile.isin([2,3])), ('Q4', df._quartile == 4)]:
        records, _, _ = analyze(df.loc[mask].reset_index(drop=True), **kwargs)
        for r in records:
            r.update(ESCS_category=label, n=int(mask.sum()))
            subgroup.append(r)
    pd.DataFrame(subgroup).to_csv(out/'escs_estimates.csv', index=False)
    # Weighted quantiles computed separately for every PV, then summarized.
    quant = []
    for group, frame in df.groupby('_tutoring'):
        for score in pv:
            values = weighted_quantile(frame[score].to_numpy(), frame[c['final_weight']].to_numpy(), [.05,.25,.5,.75,.95])
            quant.extend(dict(tutoring=int(group), pv=score, quantile=q, score=v)
                         for q, v in zip([.05,.25,.5,.75,.95], values))
    quant = pd.DataFrame(quant)
    quant.to_csv(out/'weighted_quantiles_per_pv.csv', index=False)
    from plots import plot_outputs
    plot_outputs(pd.DataFrame(overall), quant, out)
    # Two-group survey Wald analogue: no fabricated classical sums of squares.
    gap = next(r for r in overall if r['estimand'] == 'gap_non_minus_yes')
    pd.DataFrame([dict(test='Two-group Wald chi-square; asymptotic df=1',
                       statistic=(gap['estimate']/gap['se'])**2 if inference and gap['se'] > 0 else np.nan,
                       df=1, p_value=gap['p_value'])]).to_csv(out/'group_wald_test.csv', index=False)
    versions = {}
    for package in ['numpy','pandas','scipy','matplotlib']:
        versions[package] = importlib.metadata.version(package)
    h = hashlib.sha256()
    with args.data.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    manifest = dict(config=c, raw_n=n_raw, eligible_n=n_eligible, analyzed_n=len(df),
                    group_counts={str(k):int(v) for k,v in df._tutoring.value_counts().items()},
                    python=platform.python_version(), packages=versions,
                    data_sha256=h.hexdigest(), inference_enabled=inference,
                    status='SYNTHETIC DEMONSTRATION' if c.get('synthetic_demo') else 'NEW ANALYSIS; NOT VERIFIED PAPER REPRODUCTION',
                    warning='Subsample: inference suppressed; OECD replicate weights do not capture added sampling variance.' if subsampled else 'Complete-case population only; asymptotic inference; ESCS cutpoints held fixed.')
    (out/'run_manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
