"""
compute_score.py
Turns raw World Bank indicators into one composite "risk score" per country.

Method:
1. For each metric, take the latest available year per country.
2. Min-max normalize each metric to a 0-100 scale ACROSS the selected countries.
3. Flip the scale for metrics where "higher = lower risk"
   (GDP growth, political stability), so that on every metric 100 = riskiest.
4. Average the four normalized metrics with equal weights (25% each)
   to get the final risk score (0 = lowest risk, 100 = highest risk
   *within this sample of countries* — this is a relative, not absolute, score).

Run:
    python src/compute_score.py
Input:
    data/raw_indicators.csv
Output:
    data/risk_scores.csv          (final scores)
    data/latest_values_wide.csv   (latest raw values, for reference/debugging)
"""

import pandas as pd

# Metrics where a HIGHER raw value means LOWER risk -> must be inverted
INVERT_METRICS = {"gdp_growth_pct", "political_stability_est"}

WEIGHTS = {
    "inflation_pct": 0.25,
    "debt_to_gdp_pct": 0.25,
    "gdp_growth_pct": 0.25,
    "political_stability_est": 0.25,
}


def get_latest_per_country(raw: pd.DataFrame) -> pd.DataFrame:
    """Keep only the most recent available year for each country/metric."""
    idx = raw.groupby(["country_code", "metric_name"])["year"].idxmax()
    return raw.loc[idx].reset_index(drop=True)


def min_max_normalize(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    if hi == lo:  # avoid divide-by-zero if all countries are tied
        return pd.Series(50.0, index=series.index)
    return (series - lo) / (hi - lo) * 100


def main():
    raw = pd.read_csv("data/raw_indicators.csv")

    latest = get_latest_per_country(raw)
    latest.to_csv("data/latest_values_wide.csv", index=False)

    wide = latest.pivot(index="country_code", columns="metric_name", values="value")
    wide["country_name"] = raw.drop_duplicates("country_code").set_index("country_code")["country_name"]

    normalized = pd.DataFrame(index=wide.index)
    for metric in WEIGHTS:
        col = min_max_normalize(wide[metric])
        if metric in INVERT_METRICS:
            col = 100 - col
        normalized[metric + "_norm"] = col

    normalized["risk_score"] = sum(
        normalized[f"{m}_norm"] * w for m, w in WEIGHTS.items()
    )

    result = wide.join(normalized)
    result = result.sort_values("risk_score", ascending=False)
    result.to_csv("data/risk_scores.csv")

    print("Composite risk score (higher = riskier, relative to this country set):\n")
    print(result[["country_name", "risk_score"]].round(1).to_string())


if __name__ == "__main__":
    main()
