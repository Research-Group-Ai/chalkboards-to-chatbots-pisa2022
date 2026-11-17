# From Chalkboards to Chatbots: PISA 2022 methodology

A newly written implementation based on Protocol Sections 4.1–4.5 of the supplied manuscript **From Chalkboards to Chatbots: Evolution and Impact of Education in the Digital Age**.

**Reproduction status:** This is reconstructed code, not the authors' original scripts. The original data extract, sampling IDs, settings and execution environment were not provided. Exact reproduction of the manuscript's numerical results has not been established. No published result is hard-coded into an estimator. Artificial demonstration data are generated locally and are never presented as study evidence.

## Installation and demonstration

Use Python 3.11 or 3.12. From this directory:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/make_demo.py
python src/run_analysis.py --data data/synthetic_demo.csv --config configs/demo.json --output outputs/demo
```

The artificial survey weights only exercise the software. They are not a valid PISA sample design.

## Run with OECD data

1. Obtain the [OECD PISA 2022 student data and codebook](https://www.oecd.org/en/data/datasets/pisa-2022-database.html). Place the downloaded student file in `data/`. CSV, Parquet, SAV and ZSAV are supported. The student file must contain questionnaire variables, ESCS, ten mathematics plausible values and all weights. Raw cognitive-item responses are not needed by this implementation.
2. Inspect the codebook and set `yes_code` and `no_code` for `ST297Q03JA` in `configs/analysis.json`. Then set `response_codes_verified` to `true`. These codes are intentionally not guessed. Verify the configured identifiers and weight names against the release you downloaded.
3. For CSV exports, ensure missing-value codes are converted to nulls or specify them per column in `missing_codes`, e.g. `{"COLUMN_NAME": [97, 98, 99]}` using the actual codebook values for that specific column. Never apply one universal missing-code rule to scores and weights. SAV reading uses numeric codes and pyreadstat's default handling of user-missing values.
4. Run:

```bash
python src/run_analysis.py --data data/YOUR_STUDENT_FILE.sav --config configs/analysis.json --output outputs/real_analysis
```

Keep `sample_n: null` for the implemented full-eligible-sample inference. To explore a new 150,000-student sample, set `sample_n: 150000`. The seed and proportional country allocation are explicit new choices. Point weights are corrected for second-phase inclusion probabilities. **SEs, CIs and p-values are suppressed after this extra subsampling**, because the supplied PISA replicate weights alone do not account for its added sampling variance. A justified two-phase variance procedure is needed before claiming inferential reproduction of the manuscript's 150,000-student analysis.

## Analyses and files

| Component | Implementation |
|---|---|
| Eligibility | Valid tutoring response, ESCS, all ten math PVs, configured covariates, valid keys and weights |
| Group comparison | Weighted means, descriptive SDs, nonparticipation-minus-participation gap and standardized gap |
| Uncertainty | 80 Fay BRR replicates per PV, independent country variance contributions, Rubin pooling |
| Mean equality | Asymptotic two-group survey Wald test; no classical ANOVA sums of squares invented |
| ESCS | Q1, Q2–Q3, Q4 from unweighted global rank quartiles; boundaries fixed in replication |
| Regression | `math ~ 1 + tutoring + ESCS + tutoring*ESCS`, plus explicitly prepared numeric covariates |
| Distribution | PV-specific weighted quantiles and aggregate figures |
| Reproducibility | Sample allocation, local selected IDs, input SHA-256, configuration and runtime versions |

| Output | Contents |
|---|---|
| `overall_estimates.csv` | Pooled estimates, SEs, approximate CIs and p-values |
| `per_pv_estimates.csv` | Separate PV estimates |
| `within_covariance.csv`, `between_covariance.csv`, `total_covariance.csv` | Sampling/PV covariance components, full-sample inference only |
| `group_wald_test.csv` | Gap test, asymptotic chi-square with 1 df |
| `escs_estimates.csv` | Subgroup estimates and actual sample counts |
| `weighted_quantiles_per_pv.csv` | Quantiles computed separately for every PV |
| `group_means.png`, `weighted_distributions.png` | Aggregate figures |
| `sampling_audit.csv` | Country allocation and second-phase inclusion probabilities |
| `selected_ids_LOCAL_ONLY.csv` | Selected keys for local reproducibility; do not publish |
| `run_manifest.json` | Configuration, data checksum, counts, runtime and caveats |

The generic estimate output includes p-values for all quantities; the primary hypotheses are the mean gap and prespecified regression contrasts. SD/intercept tests should not be treated as substantive findings. No multiplicity adjustment is applied.

Read [docs/METHODOLOGY.md](docs/METHODOLOGY.md) and [docs/REPRODUCIBILITY_NOTES.md](docs/REPRODUCIBILITY_NOTES.md) before interpreting results. ST297Q03JA measures reported tutoring participation, not generative AI use or teacher replacement. The study is cross-sectional. PEM and cognitive-load mechanisms cannot be validated with these variables.

## Upload to GitHub

Suggested repository name: `chalkboards-to-chatbots-pisa2022`.

Unzip this package and upload the **contents** of this directory into a new GitHub repository. Include source, configuration, documentation, tests, `.github/` and `.gitignore`. Keep `data/` and `outputs/` restricted to their README files. `.gitignore` protects local files when using git but does not stop manual browser uploads.

For command-line upload, replace the example URL:

```bash
git init
git add .
git commit -m "Add configurable PISA 2022 methodology implementation"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

No software reuse license is assigned. The manuscript authors should choose a license and add final paper citation metadata before release. Public visibility alone does not grant reuse rights. OECD data retain their own usage terms.
