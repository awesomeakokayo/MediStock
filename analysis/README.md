# Analysis package: 10Alytics Health Track (Team 289)

Reproduces every number and table in the analytical report ("After the Surge").
**All data are synthetic** (simulated for the challenge); outputs must not be cited as real-world evidence.

## Run

```bash
pip install -r requirements.txt
# put the five challenge CSVs in data/raw/ (see note below), then:
python run_analysis.py data/raw
```

Outputs are written to `outputs/`. The script is deterministic (fixed bootstrap seed).

**Raw data:** the challenge CSVs (`country`, `date`, `health_system`, `fact_health_performance`, `workforce`) are not
included here. Keep `data/raw/` out of version control (add it to `.gitignore`) until the organisers' terms confirm the
files may be redistributed.

## Output files and where the report uses them

| File | Contents | Report section |
|---|---|---|
| `key_numbers.json` | Integrity checks and every headline number | Sections 1, 3.1–3.5 |
| `quarterly_indexed.csv` | National quarterly series indexed to 2018–19 = 100 | Figure 1 |
| `country_results.csv` | Per-country shock, 2024 gap, recovery shares, tier, lag, efficiency rank | Section 3.2, Appendix |
| `efficiency_2023_24.csv` | Efficiency model inputs, residuals, ranks and bootstrap rank range | Section 3.3, Table 1 |
| `spearman_recovery_correlates.csv` | Rank correlations of recovery and shock with spending, beds, staffing, vacancy | Sections 3.1, 3.2 |
| `panel_regressions.csv` | Region and year fixed-effects results (workforce pressure and spending) | Sections 3.4, 3.5 |
| `workforce_annual.csv` | Burnout and vacancy by survey year | Figure 3 |

Figure 2 uses the median, minimum and maximum of `recov_icu`, `recov_ed` and `recov_wait` in `country_results.csv`.

## Definitions (full notes in report Section 8)

- **Baseline:** each country's own 2018 Q1 – 2019 Q4 average.
- **Peak shock:** highest (ICU, waits) or lowest (ED) country-quarter relative to baseline.
- **2024 gap:** average of 2024 Q1–Q4 minus baseline. **Share recovered** = 1 − (2024 gap ÷ peak gap).
- **Wait tiers:** Recovered ≤ 10% above baseline; Stalled > 50% above; otherwise Partly recovered (analyst-chosen thresholds).
- **Efficiency:** residual of an outcome index (ED 4-hour rate and elective wait, standardised) regressed on ln(spend per person) and clinical staff per 1,000, 2023–24 country averages.
- **Panel regressions:** region and year fixed effects, standard errors clustered by country.
- Aggregation is equal-weight across regions unless stated.

## What this dataset cannot support

No inventory, procurement, wastage or environmental fields exist in the data. Nothing in this package measures them.
