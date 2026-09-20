import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Country Bank Risk Dashboard",
    page_icon="📊",
    layout="wide",
)

# ============================================================
# LOAD DATA
# ============================================================

scores = pd.read_csv("data/risk_scores.csv")
latest = pd.read_csv("data/latest_values_wide.csv")
raw = pd.read_csv("data/raw_indicators.csv")

country_names = (
    scores[["country_code", "country_name"]]
    .drop_duplicates()
    .set_index("country_code")["country_name"]
    .to_dict()
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def risk_level(score):
    if score >= 66.7:
        return "Higher relative risk"
    elif score >= 33.3:
        return "Moderate relative risk"
    else:
        return "Lower relative risk"


def risk_components(row):
    return {
        "Inflation": row["inflation_pct_norm"],
        "Government debt": row["debt_to_gdp_pct_norm"],
        "GDP growth": row["gdp_growth_pct_norm"],
        "Political stability": row["political_stability_est_norm"],
    }


# ============================================================
# HEADER
# ============================================================

st.title("📊 Country Bank Risk Dashboard")

st.caption(
    "Interactive comparison of macroeconomic and institutional risk "
    "across selected Central and Eastern European countries"
)

st.markdown(
    """
This dashboard combines four indicators — inflation, government debt,
GDP growth, and political stability — into a composite relative risk score.
"""
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Dashboard controls")

country_code = st.sidebar.selectbox(
    "Select country",
    options=sorted(scores["country_code"].unique()),
    format_func=lambda x: country_names[x],
)

selected = scores[
    scores["country_code"] == country_code
].iloc[0]

data_year = 2024

st.sidebar.divider()

st.sidebar.markdown("### Data coverage")
st.sidebar.write("Countries:", len(scores))
st.sidebar.write("Indicators:", 4)
st.sidebar.write("Latest year:", data_year)

# ============================================================
# MAIN RISK SCORE
# ============================================================

st.subheader(f"{selected['country_name']} — Risk Overview")

score = selected["risk_score"]
level = risk_level(score)

score_col, level_col, year_col = st.columns(3)

with score_col:
    st.metric(
        "Composite Risk Score",
        f"{score:.1f} / 100",
    )

with level_col:
    st.metric(
        "Risk Category",
        level,
    )

with year_col:
    st.metric(
        "Observation Year",
        str(data_year),
    )

st.info(
    "The score is relative to the six countries in this sample. "
    "It is not an absolute credit rating or a forecast of future risk."
)

# ============================================================
# INDICATOR CARDS
# ============================================================

st.subheader("Latest Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Inflation",
        f"{selected['inflation_pct']:.1f}%",
    )

with col2:
    st.metric(
        "Government Debt",
        f"{selected['debt_to_gdp_pct']:.1f}%",
    )

with col3:
    st.metric(
        "GDP Growth",
        f"{selected['gdp_growth_pct']:.1f}%",
    )

with col4:
    st.metric(
        "Political Stability",
        f"{selected['political_stability_est']:.2f}",
    )

# ============================================================
# RISK COMPONENTS
# ============================================================

st.subheader("Risk Components")

components = risk_components(selected)

component_df = pd.DataFrame(
    {
        "Indicator": list(components.keys()),
        "Relative risk contribution": list(components.values()),
    }
)

fig_components, ax_components = plt.subplots(figsize=(10, 4.5))

bars = ax_components.barh(
    component_df["Indicator"],
    component_df["Relative risk contribution"],
)

ax_components.set_xlim(0, 100)
ax_components.set_xlabel("Normalized risk score")
ax_components.grid(axis="x", alpha=0.25)

for bar, value in zip(bars, component_df["Relative risk contribution"]):
    ax_components.text(
        min(value + 1, 96),
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}",
        va="center",
    )

plt.tight_layout()

st.pyplot(fig_components)

st.caption(
    "Each component is normalized across the six-country sample. "
    "All four indicators receive equal weight (25%)."
)

# ============================================================
# COUNTRY COMPARISON
# ============================================================

st.divider()

st.subheader("Country Comparison")

comparison_col1, comparison_col2 = st.columns(2)

country_options = sorted(scores["country_code"].unique())

with comparison_col1:
    country_1 = st.selectbox(
        "Country 1",
        country_options,
        index=country_options.index(country_code),
        format_func=lambda x: country_names[x],
    )

with comparison_col2:
    default_second = (
        "POL"
        if country_code != "POL"
        else "AUT"
    )

    country_2 = st.selectbox(
        "Country 2",
        country_options,
        index=country_options.index(default_second),
        format_func=lambda x: country_names[x],
    )

comparison_data = scores[
    scores["country_code"].isin([country_1, country_2])
].copy()

fig_compare, ax_compare = plt.subplots(figsize=(9, 4.5))

ax_compare.bar(
    comparison_data["country_name"],
    comparison_data["risk_score"],
)

ax_compare.set_ylim(0, 100)
ax_compare.set_ylabel("Composite Risk Score")
ax_compare.grid(axis="y", alpha=0.25)

for i, value in enumerate(comparison_data["risk_score"]):
    ax_compare.text(
        i,
        value + 2,
        f"{value:.1f}",
        ha="center",
    )

plt.tight_layout()

st.pyplot(fig_compare)

# ============================================================
# FULL COUNTRY DISTRIBUTION
# ============================================================

st.subheader("Risk Score Across All Countries")

distribution = scores[
    ["country_name", "risk_score"]
].sort_values(
    "risk_score",
    ascending=True,
)

fig_distribution, ax_distribution = plt.subplots(
    figsize=(10, 5)
)

bars = ax_distribution.barh(
    distribution["country_name"],
    distribution["risk_score"],
)

ax_distribution.set_xlim(0, 100)
ax_distribution.set_xlabel("Composite Risk Score")
ax_distribution.grid(axis="x", alpha=0.25)

for bar, value in zip(bars, distribution["risk_score"]):
    ax_distribution.text(
        value + 1,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}",
        va="center",
    )

plt.tight_layout()

st.pyplot(fig_distribution)

# ============================================================
# INFLATION TREND
# ============================================================

st.subheader("Inflation Trend")

inflation = raw[
    raw["metric_name"] == "inflation_pct"
].copy()

inflation["country"] = inflation["country_code"].map(
    country_names
)

fig_inflation, ax_inflation = plt.subplots(
    figsize=(10, 5)
)

for country, group in inflation.groupby("country"):
    group = group.sort_values("year")

    ax_inflation.plot(
        group["year"],
        group["value"],
        marker="o",
        label=country,
    )

ax_inflation.set_xlabel("Year")
ax_inflation.set_ylabel("Inflation (%)")
ax_inflation.grid(alpha=0.25)
ax_inflation.legend()

plt.tight_layout()

st.pyplot(fig_inflation)

# ============================================================
# DATA TABLE
# ============================================================

with st.expander("View underlying country data"):

    display_columns = [
        "country_name",
        "inflation_pct",
        "debt_to_gdp_pct",
        "gdp_growth_pct",
        "political_stability_est",
        "risk_score",
    ]

    table = scores[display_columns].copy()

    table.columns = [
        "Country",
        "Inflation (%)",
        "Government Debt (% GDP)",
        "GDP Growth (%)",
        "Political Stability",
        "Risk Score",
    ]

    st.dataframe(
        table.round(2),
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# METHODOLOGY
# ============================================================

with st.expander("Methodology & Data Sources"):

    st.markdown(
        """
### Indicators

- **Inflation** — World Bank World Development Indicators
- **Government debt** — IMF WEO DataMapper
- **GDP growth** — World Bank World Development Indicators
- **Political Stability** — World Bank Worldwide Governance Indicators

### Calculation

For each indicator, values are normalized across the six countries:

`(value - minimum) / (maximum - minimum) × 100`

GDP growth and political stability are inverted because higher values
represent lower risk.

The four normalized indicators receive equal weights:

- Inflation — 25%
- Government debt — 25%
- GDP growth — 25%
- Political stability — 25%

The resulting composite score ranges from 0 to 100.

**Higher score = higher relative risk within this sample.**

The current dataset uses 2019–2024 observations, with the current
country-level snapshot based on 2024 data.
"""
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Data sources: World Bank WDI/WGI and IMF WEO DataMapper."
)

st.caption(
    "Educational / portfolio project — not an official credit-risk assessment."
)
