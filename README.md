**Live Demo:** https://country-bank-risk-dashboard.streamlit.app

# Country Bank Risk Dashboard (MVP)

A small, self-contained pipeline that scores six Central and Eastern European (CEE) countries on macroeconomic and political risk relevant to banking exposure.

The project combines publicly available data from the **World Bank** and the **International Monetary Fund (IMF)** and produces a transparent composite country-risk score that can be used as a starting point for comparative banking and finance analysis.

## What it does

1. Pulls four indicators for six countries for the 2019–2024 period.
2. Combines data from the World Bank and IMF.
3. Selects the latest available observation for each country and indicator.
4. Normalizes the indicators to a 0–100 scale relative to the countries in the sample.
5. Computes a single **composite risk score (0–100)** for each country.
6. Produces:

   * a country risk ranking bar chart;
   * an inflation trend line chart.


## Desktop Dashboard

The project includes a standalone desktop dashboard built with PySide6.

The application provides:

- country selection
- composite country risk score
- risk category
- key economic and governance indicators
- normalized risk components
- cross-country comparison
- methodology overview

Run locally:

```bash
python desktop_app.py
```

Build the macOS application:

```bash
pyinstaller --windowed --name "Country Bank Risk Dashboard" --add-data "data:data" desktop_app.py
```

Launch the application:

```bash
open "dist/Country Bank Risk Dashboard.app"
```

## Countries covered

* Ukraine
* Poland
* Hungary
* Romania
* Serbia
* Austria

Austria is included as a relatively mature EU benchmark for comparison with the other countries in the sample.

## Data sources

The project uses publicly available data from two sources:

* **World Bank World Development Indicators (WDI)** for inflation and GDP growth.
* **World Bank Worldwide Governance Indicators (WGI)** for Political Stability.
* **IMF World Economic Outlook (WEO) DataMapper** for general government gross debt.

No API key is required.

| Metric                                   | Source             | Indicator code      |
| ---------------------------------------- | ------------------ | ------------------- |
| Inflation, consumer prices (annual %)    | World Bank WDI     | `FP.CPI.TOTL.ZG`    |
| General government gross debt (% of GDP) | IMF WEO DataMapper | `GGXWDG_NGDP`       |
| GDP growth (annual %)                    | World Bank WDI     | `NY.GDP.MKTP.KD.ZG` |
| Political Stability estimate             | World Bank WGI     | `GOV_WGI_PV_EST`    |

The data collection script currently retrieves observations for **2019–2024**. The composite score uses the latest available observation for each country and metric; in the current dataset, all four indicators are available for all six countries in **2024**.

Because some macroeconomic and governance indicators are published with a delay, this should be viewed as a **structural/medium-term comparative risk indicator rather than a real-time risk measure**.

## Methodology

For each country and metric, the latest available observation is selected.

Each metric is then min-max normalized across the six countries in the sample:

```text
normalized = (value - minimum) / (maximum - minimum) × 100
```

This means that the normalization is **relative to the selected country sample**, rather than to a global or historical benchmark.

For indicators where a higher raw value generally corresponds to lower risk — GDP growth and Political Stability — the normalized score is inverted:

```text
risk_component = 100 - normalized
```

After this transformation, a higher value always represents a higher relative risk contribution.

The four components are then combined using equal weights:

```text
risk_score =
    0.25 × inflation_norm
  + 0.25 × debt_to_gdp_norm
  + 0.25 × gdp_growth_risk_norm
  + 0.25 × political_stability_risk_norm
```

The final score ranges from **0 to 100 within the selected sample**, where a higher score indicates higher relative risk.

### Important interpretation

The score is **not an absolute measure of country risk**.

For example, a score of 80 does not mean that a country has "80% risk" or that it is twice as risky as a country with a score of 40. The score only reflects the country's position relative to the other countries included in the model and the selected indicators.

## How to run it

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
python -m pip install pandas requests matplotlib
```

Run the pipeline:

```bash
python src/fetch_data.py
python src/compute_score.py
python src/visualize.py
```

### Outputs

`fetch_data.py` creates:

```text
data/raw_indicators.csv
```

`compute_score.py` creates:

```text
data/latest_values_wide.csv
data/risk_scores.csv
```

`visualize.py` creates:

```text
output/risk_score_ranking.png
output/inflation_trend.png
```

## Limitations

This is a deliberately simple MVP rather than a production-grade country-risk model.

### Equal weighting

All four indicators receive a 25% weight.

This is transparent and easy to interpret, but it is a methodological simplification. A more advanced model could estimate weights using historical crisis/default outcomes or allow users to configure the weights.

### Relative rather than absolute score

The score depends on the countries included in the sample.

Adding or removing countries can change the min-max normalization and therefore change the final scores even when the underlying country data remain unchanged.

### Limited number of indicators

The model uses only four indicators. A more comprehensive banking-risk framework could include variables such as:

* non-performing loans (NPLs);
* capital adequacy;
* foreign-exchange reserves;
* external debt;
* current-account balance;
* sovereign bond spreads;
* banking-sector profitability and liquidity.

### Data frequency and publication lag

The model relies mainly on annual macroeconomic and governance indicators. These are useful for structural comparison but are not designed to provide real-time monitoring.

A more advanced version could combine annual structural indicators with higher-frequency market and macroeconomic data.

### No uncertainty or sensitivity analysis

The model produces a single point estimate.

A more mature version could report confidence intervals or show how the results change under alternative weighting schemes and indicator selections.

### No historical backtesting

The current MVP does not test whether the score would have successfully identified countries before historical banking or sovereign-risk episodes.

Backtesting against periods such as the 2008 global financial crisis or the 2022 escalation of the war in Ukraine could provide a useful next step for evaluating the model.

## Potential next steps

Possible extensions include:

1. Add banking-sector indicators such as NPL ratios and capital adequacy.
2. Add external debt and foreign-exchange reserve indicators.
3. Introduce configurable indicator weights.
4. Add sensitivity analysis for different weighting schemes.
5. Backtest the methodology against historical crisis periods.
6. Add higher-frequency indicators for a more current risk-monitoring dashboard.
7. Add automated data updates and timestamped historical scores.
8. Expand the country sample beyond the current six countries.

## Project structure

```text
CEE_Country_Bank_Risk/
│
├── src/
│   ├── fetch_data.py          # downloads raw indicators
│   ├── compute_score.py       # calculates composite risk scores
│   └── visualize.py           # generates charts
│
├── data/
│   ├── raw_indicators.csv     # raw data in long format
│   ├── latest_values_wide.csv # latest observations used in scoring
│   └── risk_scores.csv        # final scores and normalized components
│
├── output/
│   ├── risk_score_ranking.png
│   └── inflation_trend.png
│
└── README.md
```
## Interactive Dashboard

The project includes an interactive Streamlit dashboard for exploring the country risk scores.

### Run locally

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
## Disclaimer

This project is an educational and portfolio-oriented analytical tool. The composite score is a simplified comparative indicator and should not be interpreted as an official sovereign or banking credit-risk assessment.

