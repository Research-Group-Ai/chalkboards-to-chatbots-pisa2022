# Reproduction limits and manuscript checks

The code is reconstructed from the supplied 19-page paper. Mathematical tests and end-to-end artificial-data execution have been performed. The original PISA extract was not supplied, so neither agreement with reported numbers nor substantive findings have been verified.

## Information needed for exact reproduction

| Detail | Missing from supplied methodology | Package treatment |
|---|---|---|
| Original data release and exclusions | Precise release and country list | Analyst documents release; checksum recorded |
| Original 150,000 selection | Seed, allocation, selected IDs | Optional new seeded proportional country sample; full sample used by default |
| Tutoring recoding | Numeric yes/no codes | Mandatory explicit verification |
| Additional subsampling variance | Two-phase variance method | Subsample inference suppressed |
| ESCS cutpoints | Weighted versus unweighted; national versus global | Explicit unweighted global rank quartiles |
| ST254 / ST326 | Exact item columns, response codes and aggregation | No invented hardware index or duration scale; optional documented numeric covariates |
| Adjusted regression | Complete model formula and encoding | Explicit ESCS/tutoring interaction model; a new implementation choice |
| Balance checks | Exact gender and school-type variables, coding and test | Not reconstructed pending an explicit analysis plan |
| Rank tests | Test definition and survey treatment | Not reconstructed; no naive independent-sample rank p-values substituted |
| Original environment | Reproducible package versions/environment | Actual versions recorded in manifest |

If separate questionnaire/cognitive files are used, merge one-to-one on country AND student keys before running; duplicate keys are rejected. Do not merge international files on student ID alone. SPSS numeric missing codes in CSV must be converted or configured per variable. Check questionnaire participation by country before interpreting a global estimate.

## Manuscript numerical issues

- Table 5's between SS=1,200,000 and within SS=85,000,000 with df=1 and 149,998 imply classical F about **2117.62**, not 452.1. A survey Wald test can differ from SS-based F, but they should not be presented as the same calculation. This code reports a labeled survey Wald test without classical sums of squares.
- Table 4's gap-row SD of **12.4** equals 94.5 minus 82.1. The difference of group SDs is not the SE or SD of the mean gap. Here gap uncertainty is estimated directly with covariance.
- Using Table 4's counts and SDs with the stated count-pooled formula gives standardized gap about **0.269**, rather than approximately 0.28. Check unrounded values and the actual estimator.
- The text describes four quartiles of 150,000 each although total n is 150,000. Table 6 instead lists 37,500, 75,000 and 37,500 for Q1, Q2–Q3 and Q4.
- Reconcile the text's group SEs (0.21 and 0.25) with Table 4's CIs and combined sampling/PV uncertainty.
- Replace interpretations of ST297Q03JA as AI use or a causal pedagogical intervention with its actual tutoring-participation meaning.

Conceptual Figures 1–4 and Tables 1–3, 7–8 are not statistical estimands and are not regenerated as empirical evidence. No code here claims to validate PEM, cognitive load, knowledge internalization or a causal mechanism.

## Validation

Unit tests check a hand-computable Rubin example, direct mean-gap/BRR calculations, independent national replicate permutation, and suppression of inferential output. The synthetic end-to-end run exercises CSVs, regression, subgroup analysis, plots and manifests. Artificial weights are for software execution only, not validation of PISA design behavior. No real-data reproduction is claimed.

Dependencies use bounded ranges; manifests record actual versions. Before an archival code release, freeze a tested environment, add final citation metadata, choose a software license and validate against the original analytical data and settings.
