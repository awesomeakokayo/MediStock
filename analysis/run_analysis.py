"""
CareGrid / 10Alytics Health Track - reproducible analysis.

Usage:
    python run_analysis.py [path/to/raw_csv_dir]     (default: data/raw)

Reads the five challenge tables (country, date, health_system,
fact_health_performance, workforce) and writes every table and number used in
the report to ./outputs. All data are SYNTHETIC (simulated for the challenge).
Method notes: see Section 8 of the report and README.md.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

RAW = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw")
OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)
PHASES = ["Pre-Pandemic", "Acute Pandemic", "Recovery", "Post-Pandemic"]
KEY = {}  # headline numbers, written to key_numbers.json


def rd(name):
    return pd.read_csv(RAW / f"{name}.csv", encoding="utf-8-sig")


def z(s):
    return (s - s.mean()) / s.std()


# ------------------------------------------------------------------ load + checks
country, date, hs, perf, work = (rd(n) for n in
    ["country", "date", "health_system", "fact_health_performance", "workforce"])
P = (perf.merge(date, on="date_id").merge(country, on="country_id")
     .merge(hs[["system_id", "population_thousands"]], on="system_id"))
chk = perf.merge(hs[["system_id", "country_id"]], on="system_id", suffixes=("", "_hs"))
KEY["integrity"] = {
    "tables": {n: len(t) for n, t in [("country", country), ("date", date), ("health_system", hs),
                                       ("performance", perf), ("workforce", work)]},
    "missing_values": int(sum(t.isna().sum().sum() for t in [country, date, hs, perf, work])),
    "duplicate_rows": int(sum(t.duplicated().sum() for t in [country, date, hs, perf, work])),
    "orphan_keys": int((~perf.system_id.isin(hs.system_id)).sum() + (~perf.date_id.isin(date.date_id)).sum()),
    "country_mismatch": int((chk.country_id != chk.country_id_hs).sum()),
}

# ------------------------------------------------------------------ 3.1 shock (phase means)
ph = P.groupby("pandemic_phase")
KEY["icu_phase_mean"] = ph.icu_occupancy_pct.mean().reindex(PHASES).round(2).to_dict()
KEY["share_icu_ge85_by_phase_pct"] = (ph.icu_occupancy_pct.apply(lambda s: (s >= 85).mean() * 100)
                                      .reindex(PHASES).round(1).to_dict())
KEY["share_icu_ge90_by_phase_pct"] = (ph.icu_occupancy_pct.apply(lambda s: (s >= 90).mean() * 100)
                                      .reindex(PHASES).round(1).to_dict())

# country-quarter means; baseline = each country's own 2018 Q1 - 2019 Q4 (date_id <= 8)
CQ = (P.groupby(["country_name", "year_quarter", "date_id"])
      .agg(icu=("icu_occupancy_pct", "mean"), ed=("ed_4hr_pct", "mean"),
           wait=("elective_wait_weeks", "mean"), resp=("respiratory_illness_pct", "mean"))
      .reset_index())
base = CQ[CQ.date_id <= 8].groupby("country_name")[["icu", "ed", "wait"]].mean().add_suffix("_b")
CQ = CQ.merge(base, left_on="country_name", right_index=True)
CQ["icu_dev"] = CQ.icu - CQ.icu_b
CQ["ed_dev"] = CQ.ed - CQ.ed_b
CQ["wait_pct"] = CQ.wait / CQ.wait_b - 1
g = CQ.groupby("country_name")
R = pd.DataFrame(index=sorted(CQ.country_name.unique()))
R["icu_peak_dev"] = g.icu_dev.max()
R["icu_peak_q"] = CQ.loc[g.icu_dev.idxmax()].set_index("country_name").year_quarter
R["ed_peak_dev"] = g.ed_dev.min()
R["ed_trough_q"] = CQ.loc[g.ed_dev.idxmin()].set_index("country_name").year_quarter
R["wait_peak_pct"] = g.wait_pct.max()
late = CQ[CQ.year_quarter >= "2024 Q1"].groupby("country_name")[["icu_dev", "ed_dev", "wait_pct"]].mean()
R["icu_2024_dev"], R["ed_2024_dev"], R["wait_2024_pct"] = late.icu_dev, late.ed_dev, late.wait_pct
R["recov_icu"] = 1 - R.icu_2024_dev / R.icu_peak_dev
R["recov_ed"] = 1 - R.ed_2024_dev / R.ed_peak_dev
R["recov_wait"] = 1 - R.wait_2024_pct / R.wait_peak_pct
qi = {q: i for i, q in enumerate(sorted(CQ.year_quarter.unique()))}
R["lag_quarters_icu_peak_to_ed_low"] = R.ed_trough_q.map(qi) - R.icu_peak_q.map(qi)
R["wait_tier"] = np.where(R.wait_2024_pct <= 0.10, "Recovered",
                          np.where(R.wait_2024_pct > 0.50, "Stalled", "Partly recovered"))
R = R.join(country.set_index("country_name")[["income_group", "who_region"]])

KEY["icu_peak_rise_pts"] = {"median": round(R.icu_peak_dev.median(), 1), "min": round(R.icu_peak_dev.min(), 1),
                            "max": round(R.icu_peak_dev.max(), 1)}
KEY["countries_icu_within_2pts_2024"] = int((R.icu_2024_dev.abs() <= 2).sum())
KEY["ed_gap_2024_pts"] = {"median": round(R.ed_2024_dev.median(), 1), "min": round(R.ed_2024_dev.min(), 1),
                          "max": round(R.ed_2024_dev.max(), 1), "countries_below_baseline": int((R.ed_2024_dev < 0).sum())}
KEY["wait_2024_vs_baseline_pct_median"] = round(R.wait_2024_pct.median() * 100, 0)
KEY["wait_tiers"] = R.wait_tier.value_counts().to_dict()
KEY["wait_recovered_countries"] = list(R.index[R.wait_tier == "Recovered"])
KEY["median_share_recovered_pct"] = {k: round(R[k].median() * 100, 1) for k in ["recov_icu", "recov_ed", "recov_wait"]}
KEY["lag_icu_peak_to_ed_low_quarters"] = {"median": float(R.lag_quarters_icu_peak_to_ed_low.median()),
                                          "countries_ed_low_after_icu_peak": int((R.lag_quarters_icu_peak_to_ed_low > 0).sum())}
KEY["icu_peak_by_income_group"] = R.groupby("income_group").icu_peak_dev.mean().round(1).to_dict()

# ED low point: equal-weight vs population-weighted
eq = P.groupby("year_quarter").ed_4hr_pct.mean()
pw = P.groupby("year_quarter").apply(lambda d: np.average(d.ed_4hr_pct, weights=d.population_thousands))
KEY["ed_low_quarter"] = {"equal_weight": [eq.idxmin(), round(eq.min(), 2)], "pop_weighted": [pw.idxmin(), round(pw.min(), 2)]}
for y in (2019, 2022):
    KEY[f"share_region_quarters_ed_below70_{y}_pct"] = round((P[P.year == y].ed_4hr_pct < 70).mean() * 100, 1)

# indexed quarterly series (Figure 1)
qs = (P.groupby(["year_quarter", "date_id"]).agg(icu=("icu_occupancy_pct", "mean"), ed=("ed_4hr_pct", "mean"),
      wait=("elective_wait_weeks", "mean"), resp=("respiratory_illness_pct", "mean")).reset_index().sort_values("date_id"))
b = qs[qs.date_id <= 8][["icu", "ed", "wait", "resp"]].mean()
for k in ["icu", "ed", "wait", "resp"]:
    qs[k + "_index"] = (qs[k] / b[k] * 100).round(1)
qs.drop(columns="date_id").to_csv(OUT / "quarterly_indexed.csv", index=False)
KEY["respiratory_baseline_pct"] = round(b.resp, 2)

# within-country regional dispersion of ICU occupancy
rg = P.groupby(["country_name", "year_quarter", "pandemic_phase"]).icu_occupancy_pct.agg(["min", "max", "count"]).reset_index()
rg["range"] = rg["max"] - rg["min"]
multi = rg[rg["count"] >= 8]
KEY["icu_regional_range_pts_by_phase"] = multi.groupby("pandemic_phase")["range"].mean().reindex(PHASES).round(1).to_dict()
q21 = P[P.year_quarter == "2021 Q1"].groupby("country_name").icu_occupancy_pct.agg(["min", "max"])
KEY["countries_2021Q1_with_region_ge85_and_region_lt75"] = int(((q21["max"] >= 85) & (q21["min"] < 75)).sum())

# ------------------------------------------------------------------ region-year panel
A = (P.groupby(["system_id", "year"]).agg(icu=("icu_occupancy_pct", "mean"), ed=("ed_4hr_pct", "mean"),
     wait=("elective_wait_weeks", "mean"), los=("avg_length_of_stay_days", "mean"),
     readm=("readmission_30d_pct", "mean"), beds=("beds_per_1000", "mean"),
     spend=("health_spend_per_capita_usd", "mean")).reset_index())
A = A.merge(work[["system_id", "survey_year", "doctors_per_1000", "nurses_per_1000", "vacancy_rate_pct", "burnout_index"]],
            left_on=["system_id", "year"], right_on=["system_id", "survey_year"])
A = A.merge(hs[["system_id", "country_id"]], on="system_id").merge(country[["country_id", "country_name", "income_group"]], on="country_id")
A["sys"] = A.system_id.astype(str)

yr = P.groupby("year").agg(beds=("beds_per_1000", "mean"), spend=("health_spend_per_capita_usd", "mean"), los=("avg_length_of_stay_days", "mean"))
KEY["beds_per_1000"] = {"2019": round(yr.beds[2019], 2), "2024": round(yr.beds[2024], 2), "change_pct": round((yr.beds[2024] / yr.beds[2019] - 1) * 100, 1)}
KEY["spend_per_person_usd"] = {"2019": round(yr.spend[2019]), "2024": round(yr.spend[2024]), "change_pct": round((yr.spend[2024] / yr.spend[2019] - 1) * 100, 1)}
cc = P[P.year.isin([2019, 2024])].groupby(["country_name", "year"])[["beds_per_1000", "health_spend_per_capita_usd"]].mean().unstack()
KEY["countries_beds_down_spend_up"] = [int((cc["beds_per_1000"][2024] < cc["beds_per_1000"][2019]).sum()),
                                       int((cc["health_spend_per_capita_usd"][2024] > cc["health_spend_per_capita_usd"][2019]).sum())]
wf = A.groupby("year")[["burnout_index", "vacancy_rate_pct"]].mean().round(2)
wf.to_csv(OUT / "workforce_annual.csv")
KEY["workforce_corr_region_years"] = round(A.vacancy_rate_pct.corr(A.burnout_index), 2)
KEY["workforce_corr_within_year_range"] = [round(min(A[A.year == y].vacancy_rate_pct.corr(A[A.year == y].burnout_index) for y in A.year.unique()), 2),
                                           round(max(A[A.year == y].vacancy_rate_pct.corr(A[A.year == y].burnout_index) for y in A.year.unique()), 2)]
KEY["los_between_country_sd_days"] = round(A.groupby("country_name").los.mean().std(), 2)
KEY["los_within_region_sd_days"] = round(A.groupby("system_id").los.std().mean(), 2)

# fixed-effects regressions (region + year FE, SE clustered by country)
rows = []
for y in ["wait", "ed", "icu", "los", "readm"]:
    m = smf.ols(f"{y} ~ vacancy_rate_pct + burnout_index + C(sys) + C(year)", data=A).fit(
        cov_type="cluster", cov_kwds={"groups": A.country_id})
    for v in ["vacancy_rate_pct", "burnout_index"]:
        rows.append({"outcome": y, "predictor": v, "coef": m.params[v], "p_value": m.pvalues[v]})
    m = smf.ols(f"{y} ~ np.log(spend) + C(sys) + C(year)", data=A).fit(cov_type="cluster", cov_kwds={"groups": A.country_id})
    rows.append({"outcome": y, "predictor": "log_spend", "coef": m.params["np.log(spend)"], "p_value": m.pvalues["np.log(spend)"]})
pd.DataFrame(rows).round(4).to_csv(OUT / "panel_regressions.csv", index=False)

# ------------------------------------------------------------------ 3.2 correlates of recovery (2018-19 structure)
S = A[A.year.isin([2018, 2019])].groupby("country_name")[["spend", "beds", "doctors_per_1000", "nurses_per_1000", "vacancy_rate_pct"]].mean()
S["staff"] = S.doctors_per_1000 + S.nurses_per_1000
X = R.join(S)
cor = []
for tgt in ["recov_wait", "wait_2024_pct", "icu_peak_dev"]:
    for f in ["spend", "beds", "staff", "vacancy_rate_pct"]:
        r, p = stats.spearmanr(X[f], X[tgt])
        cor.append({"target": tgt, "feature": f, "spearman": round(r, 3), "p_value": round(p, 4), "n": len(X)})
pd.DataFrame(cor).to_csv(OUT / "spearman_recovery_correlates.csv", index=False)
KEY["recovered8_vs_rest_median"] = (X.assign(rec=X.wait_tier == "Recovered").groupby("rec")[["spend", "staff"]].median().round(1)
                                    .rename(index={True: "recovered", False: "others"}).to_dict())

# ------------------------------------------------------------------ 3.3 efficiency
Lc = (A[A.year >= 2023].groupby("country_name").agg(ed=("ed", "mean"), wait=("wait", "mean"), spend=("spend", "mean"),
      doc=("doctors_per_1000", "mean"), nur=("nurses_per_1000", "mean"), beds=("beds", "mean"), los=("los", "mean"))
      .join(country.set_index("country_name")[["income_group"]]))
Lc["staff"] = Lc.doc + Lc.nur
Lc["outcome"] = (z(Lc.ed) + z(-Lc.wait)) / 2
Lc["lspend"] = np.log(Lc.spend)
m2 = smf.ols("outcome ~ lspend + staff", data=Lc).fit()
Lc["efficiency_residual"] = m2.resid
Lc["efficiency_rank"] = Lc.efficiency_residual.rank(ascending=False).astype(int)
KEY["efficiency_model"] = {"r2": round(m2.rsquared, 3), "n": len(Lc),
    "rank_corr_spend_only": round(stats.spearmanr(Lc.efficiency_residual, smf.ols("outcome ~ lspend", data=Lc).fit().resid)[0], 2),
    "rank_corr_plus_beds": round(stats.spearmanr(Lc.efficiency_residual, smf.ols("outcome ~ lspend + staff + beds", data=Lc).fit().resid)[0], 2),
    "rank_corr_plus_income": round(stats.spearmanr(Lc.efficiency_residual, smf.ols("outcome ~ lspend + staff + C(income_group)", data=Lc).fit().resid)[0], 2)}
rng = np.random.default_rng(7)
rk = []
for _ in range(1000):
    s = Lc.sample(len(Lc), replace=True, random_state=int(rng.integers(1e9)))
    mm = smf.ols("outcome ~ lspend + staff", data=s).fit()
    rk.append((Lc.outcome - mm.predict(Lc)).rank(ascending=False))
rk = pd.concat(rk, axis=1)
Lc["rank_p10"], Lc["rank_p90"] = rk.quantile(.1, axis=1), rk.quantile(.9, axis=1)
Lc.round(3).to_csv(OUT / "efficiency_2023_24.csv")
KEY["los_vs_beds_spearman"] = [round(v, 3) for v in stats.spearmanr(Lc.los, Lc.beds)]

# ------------------------------------------------------------------ country appendix table
T = R.join(Lc[["efficiency_rank"]])
T[["income_group", "icu_peak_dev", "ed_2024_dev", "wait_2024_pct", "recov_wait", "wait_tier", "efficiency_rank",
   "recov_icu", "recov_ed", "icu_peak_q", "ed_trough_q", "lag_quarters_icu_peak_to_ed_low"]].sort_values("wait_2024_pct").round(3).to_csv(
    OUT / "country_results.csv", index_label="country")

# ------------------------------------------------------------------ UK vs EU
eu, uk = P[P.is_eu_member], P[P.iso3 == "GBR"]
KEY["uk_vs_eu"] = {
    "elective_wait_weeks_2019": [round(uk[uk.year == 2019].elective_wait_weeks.mean(), 1), round(eu[eu.year == 2019].elective_wait_weeks.mean(), 1)],
    "elective_wait_weeks_2024": [round(uk[uk.year == 2024].elective_wait_weeks.mean(), 1), round(eu[eu.year == 2024].elective_wait_weeks.mean(), 1)],
    "spend_avg_uk_eu": [round(uk.health_spend_per_capita_usd.mean()), round(eu.health_spend_per_capita_usd.mean())],
}
Wd = work.merge(country, on="country_id")
KEY["uk_vs_eu"]["vacancy_2024_uk_eu"] = [round(Wd[(Wd.iso3 == "GBR") & (Wd.survey_year == 2024)].vacancy_rate_pct.mean(), 1),
                                         round(Wd[Wd.is_eu_member & (Wd.survey_year == 2024)].vacancy_rate_pct.mean(), 1)]

(OUT / "key_numbers.json").write_text(json.dumps(KEY, indent=2, default=str), encoding="utf-8")
print("Done. Wrote", sorted(p.name for p in OUT.iterdir()))
