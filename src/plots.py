
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot_outputs(estimates, quantiles, out):
    fig, ax = plt.subplots(figsize=(7, 4))
    rows = estimates.set_index('estimand').loc[['mean_nonparticipation','mean_participation']]
    ax.bar(['No reported tutoring','Reported tutoring'], rows.estimate, color=['#21618c','#b65c29'])
    if np.isfinite(rows.se).all():
        ax.errorbar([0,1], rows.estimate, yerr=1.96*rows.se, fmt='none', color='black', capsize=6)
    ax.set_ylabel('Mathematics score (PV-pooled weighted mean)')
    fig.tight_layout()
    fig.savefig(out/'group_means.png', dpi=180)
    plt.close(fig)
    summary = quantiles.groupby(['tutoring','quantile']).score.mean().unstack()
    fig, ax = plt.subplots(figsize=(7, 4))
    for i, (_, row) in enumerate(summary.iterrows()):
        ax.plot([row[.05], row[.95]], [i,i], color='#21618c')
        ax.plot([row[.25], row[.75]], [i,i], linewidth=10, color='#21618c')
        ax.plot(row[.5], i, '|', color='white', markersize=15)
    ax.set_yticks([0,1], ['No reported tutoring','Reported tutoring'])
    ax.set_xlabel('Mathematics score; averaged PV-specific weighted quantiles')
    ax.set_title('5th, 25th, 50th, 75th and 95th percentiles')
    fig.tight_layout()
    fig.savefig(out/'weighted_distributions.png', dpi=180)
    plt.close(fig)
