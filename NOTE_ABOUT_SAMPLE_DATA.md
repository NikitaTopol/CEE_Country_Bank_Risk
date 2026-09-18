®# ⚠️ Important: this package ships with SAMPLE data, not live data

The `data/raw_indicators.csv`, `data/risk_scores.csv`, `output/*.png`, and
`summary.pdf` files included here were generated from **approximate,
hand-typed sample values** — used only to prove that the full pipeline
(fetch → score → charts → PDF) runs end-to-end without errors, since the
environment that built this package did not have outbound internet access
to the World Bank API.

**Before using this for your CV / applications, run:**

```bash
pip install -r requirements.txt
python src/fetch_data.py
python src/compute_score.py
python src/visualize.py
python src/make_summary_pdf.py
```

This will overwrite the sample files with real, current World Bank data.
Delete this note file once you've done that.
