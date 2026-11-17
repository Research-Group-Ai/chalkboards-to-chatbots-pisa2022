# Statistical definitions

## Population and exposure

Estimates concern the complete-case student population represented by retained weights across included countries; this is a student-population-weighted pooled estimate, not an equal-country OECD average. Optional questionnaire coverage, country exclusions and nonresponse must be evaluated. Complete-case filtering does not eliminate selection bias.

The binary exposure is reported participation in internet/computer tutoring for additional mathematics instruction. It does not identify chatbot use, teacher-led versus technology-led schooling, causal effects or cognitive load.

## Point estimates

Separately for each plausible value m and group g:

- `mu_gm = sum(w_i*y_im) / sum(w_i)`.
- Weighted descriptive variance: `v_gm = sum(w_i*(y_im-mu_gm)^2) / sum(w_i)`.
- Gap: `D_m = mu_non_m - mu_yes_m`.
- Count-pooled variance: `s_pm^2 = ((n_non-1)*v_non_m + (n_yes-1)*v_yes_m)/(n_non+n_yes-2)`.
- Standardized gap: `d_m = D_m/sqrt(s_pm^2)`.

The SD is descriptive spread, not an SE. The pooling convention is explicit because the paper does not fully specify a weighted effect-size estimator. Each statistic is computed for each PV, then averaged; individual students' PVs are never averaged into an observed score.

## Fay BRR covariance

For estimator vector theta, R=80 and Fay factor f=0.5:

`U_m = sum_r ((theta_mr-theta_m)(theta_mr-theta_m)') / (R*(1-f)^2)`.

For independent countries, national variance contributions are summed. Each replicate replaces only one country's contribution to the global sufficient statistics; other countries retain full weights. This avoids assuming correlated national replicate indices. For nonlinear global estimators, the independent-country construction is a replication-based linearization approximation.

## PV pooling

With M=10:

`theta_bar = mean_m(theta_m)`

`U_bar = mean_m(U_m)`

`B = sum_m ((theta_m-theta_bar)(theta_m-theta_bar)')/(M-1)`

`T = U_bar + (1+1/M)*B`.

SEs are the square roots of T's diagonal. CIs use `theta_bar +/- 1.95996398454*SE`; p-values use the asymptotic normal distribution. These are large-sample approximations, not finite-design-df t intervals. Gap equality is tested with `W=D_bar^2/T_DD`, asymptotically chi-square with 1 df. It is not a classical ANOVA F test with n-2 denominator df, and classical sums of squares are not combined with Rubin coefficient pooling.

## Regression, quartiles and figures

Weighted least squares uses intercept, tutoring, ESCS and tutoring-by-ESCS interaction, plus configured numeric columns. Replicate refits supply coefficient covariance; naive model-based WLS covariance is not used. Extra categorical covariates require explicitly prepared indicators, omitted reference levels and documented validity rules. No country fixed effects are included by default; pooled coefficients may reflect country composition.

The ESCS groups use unweighted global rank quartiles of the selected eligible sample, with country/student-key ordering to break ties. Q2 and Q3 are combined. Cutpoints are held fixed in variance estimation. They are not weighted population quartiles or national quartiles. The interaction estimates effect modification within this specified linear model; similar subgroup gaps do not demonstrate socioeconomic independence.

Weighted quantiles use midpoint cumulative-weight interpolation separately by PV; the figure averages the resulting quantiles. No quantile uncertainty is estimated. The plot is a weighted quantile summary, not an exact recreation of the manuscript's boxenplot.

## Official documentation

- [OECD PISA 2022 database](https://www.oecd.org/en/data/datasets/pisa-2022-database.html)
- [OECD preparation and analysis guidance](https://www.oecd.org/en/about/programmes/pisa/how-to-prepare-and-analyse-the-pisa-database.html)
- [PISA 2022 Technical Report, Chapter 10, formula 10.9](https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/03/pisa-2022-technical-report_599753f0/01820d6d-en.pdf)

These sources support the survey/PV framework, not a claim that this implementation has reproduced the authors' data analysis. Confirm variable definitions against your exact downloaded release.
