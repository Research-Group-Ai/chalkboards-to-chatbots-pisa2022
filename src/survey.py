
import numpy as np
from scipy.stats import norm


def pool(q, u):
    """Rubin total covariance; asymptotic normal intervals (not n-2 df)."""
    q, u = np.asarray(q), np.asarray(u)
    m = len(q)
    mean = q.mean(axis=0)
    between = np.atleast_2d(np.cov(q, rowvar=False, ddof=1))
    within = u.mean(axis=0)
    total = within + (1 + 1 / m) * between
    se = np.sqrt(np.maximum(np.diag(total), 0))
    z = np.divide(mean, se, out=np.full_like(mean, np.nan), where=se > 0)
    return mean, se, 2 * norm.sf(abs(z)), total, within, between


def moments(x, y, w):
    # Includes group-specific first/second moments and regression normal equations.
    g = x[:, 1].astype(bool)
    a = []
    for mask in [~g, g]:
        a.extend([w[mask].sum(), w[mask] @ y[mask], w[mask] @ (y[mask] ** 2)])
    return np.r_[a, (x.T @ (w[:, None] * x)).ravel(), x.T @ (w * y)]


def estimate(s, p, counts):
    w0, sy0, sy20, w1, sy1, sy21 = s[:6]
    if min(w0, w1) <= 0:
        raise ValueError('Both tutoring groups need positive weight in every replicate.')
    mu0, mu1 = sy0 / w0, sy1 / w1
    v0, v1 = max(0., sy20 / w0 - mu0**2), max(0., sy21 / w1 - mu1**2)
    n0, n1 = counts
    # Explicit descriptive convention: count-pooled weighted population variances.
    pooled = ((n0 - 1) * v0 + (n1 - 1) * v1) / (n0 + n1 - 2)
    if pooled <= 0:
        raise ValueError('Zero pooled variance.')
    a = s[6:6 + p*p].reshape(p, p)
    b = s[6 + p*p:]
    if np.linalg.matrix_rank(a) < p:
        raise ValueError('Regression is rank deficient; check covariates and groups.')
    beta = np.linalg.solve(a, b)
    return np.r_[mu0, mu1, mu0 - mu1, np.sqrt(v0), np.sqrt(v1),
                 (mu0 - mu1) / np.sqrt(pooled), beta]


def analyze(df, pv, final, replicates, country, extra=None, fay=.5, inference=True):
    g = df['_tutoring'].to_numpy(float)
    escs = df['ESCS'].to_numpy(float)
    x = np.column_stack([np.ones(len(df)), g, escs, g*escs])
    names = ['mean_nonparticipation', 'mean_participation', 'gap_non_minus_yes',
             'sd_nonparticipation', 'sd_participation', 'standardized_gap',
             'beta_intercept', 'beta_tutoring', 'beta_ESCS', 'beta_tutoring_x_ESCS']
    for name in extra or []:
        x = np.column_stack([x, df[name].to_numpy(float)])
        names.append('beta_' + name)
    yall = df[pv].to_numpy(float)
    w = df[final].to_numpy(float)
    wr = df[replicates].to_numpy(float)
    counts = [int((g == k).sum()) for k in [0, 1]]
    if min(counts) < 2:
        raise ValueError('Each group requires at least two students.')
    points, variances = [], []
    for y in yall.T:
        s = moments(x, y, w)
        q = estimate(s, x.shape[1], counts)
        u = np.zeros((len(q), len(q)))
        if inference:
            # Countries are independent sampling designs. Vary one country's
            # replicate weights at a time; do not align their replicate indices.
            for _, idx in df.groupby(country, sort=True).indices.items():
                xc, yc = x[idx], y[idx]
                base = moments(xc, yc, w[idx])
                for r in range(wr.shape[1]):
                    sr = s - base + moments(xc, yc, wr[idx, r])
                    delta = estimate(sr, x.shape[1], counts) - q
                    u += np.outer(delta, delta) / (wr.shape[1] * (1-fay)**2)
        points.append(q)
        variances.append(u)
    q, se, pval, total, within, between = pool(points, variances)
    if not inference:
        se[:] = np.nan
        pval[:] = np.nan
    records = []
    for i, name in enumerate(names):
        records.append(dict(estimand=name, estimate=q[i], se=se[i],
                            ci_lower=q[i]-1.95996398454*se[i],
                            ci_upper=q[i]+1.95996398454*se[i], p_value=pval[i]))
    return records, np.asarray(points), dict(total=total, within=within, between=between)


def weighted_quantile(y, w, quantiles):
    order = np.argsort(y, kind='stable')
    y, w = np.asarray(y)[order], np.asarray(w)[order]
    cumulative = (np.cumsum(w) - .5*w) / w.sum()
    return np.interp(quantiles, cumulative, y)
