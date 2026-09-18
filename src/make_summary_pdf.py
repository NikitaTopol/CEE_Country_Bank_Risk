"""
make_summary_pdf.py
Builds a 1-page PDF summary (charts + short write-up) suitable for
attaching to job applications or bringing to an interview.

Run:
    python src/make_summary_pdf.py
Output:
    summary.pdf
"""

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors


def build():
    scores = pd.read_csv("data/risk_scores.csv").sort_values("risk_score", ascending=False)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleSmall", parent=styles["Title"], fontSize=17, spaceAfter=2)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=9.5,
                                     textColor=colors.grey, spaceAfter=10)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, leading=12.5)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=11.5, spaceBefore=8, spaceAfter=4)

    doc = SimpleDocTemplate(
        "summary.pdf", pagesize=A4,
        topMargin=14 * mm, bottomMargin=12 * mm, leftMargin=16 * mm, rightMargin=16 * mm,
    )

    story = []
    story.append(Paragraph("CEE Country Bank Risk Dashboard", title_style))
    story.append(Paragraph(
        "Composite macro/political risk score for 6 countries, built from World Bank Open Data.",
        subtitle_style,
    ))

    # Charts side by side
    img1 = Image("output/risk_score_ranking.png", width=88 * mm, height=55 * mm)
    img2 = Image("output/inflation_trend.png", width=88 * mm, height=55 * mm)
    chart_table = Table([[img1, img2]], colWidths=[90 * mm, 90 * mm])
    chart_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(chart_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Methodology", h2_style))
    story.append(Paragraph(
        "For each country, the latest available value of four indicators — inflation, government "
        "debt/GDP, GDP growth, and political stability (World Bank Governance Indicators) — is "
        "min-max normalized 0-100 relative to the other countries in the sample, then averaged "
        "with equal weights (25% each). 100 = highest relative risk in this sample; 0 = lowest. "
        "This is a relative ranking within the sample, not an absolute or externally-benchmarked score.",
        body_style,
    ))

    story.append(Paragraph("Key findings", h2_style))
    top = scores.iloc[0]
    bottom = scores.iloc[-1]
    findings = (
        f"<b>{top['country_name']}</b> ranks highest risk in this sample (score "
        f"{top['risk_score']:.0f}/100), driven mainly by elevated inflation and debt/GDP relative "
        f"to peers. <b>{bottom['country_name']}</b> ranks lowest (score {bottom['risk_score']:.0f}/100). "
        f"Austria, included as a developed-market benchmark, still carries a non-trivial score due to "
        f"its high debt/GDP ratio — a reminder that this score reflects a specific basket of metrics, "
        f"not a full credit-rating-style assessment."
    )
    story.append(Paragraph(findings, body_style))

    story.append(Paragraph("Risk score by country", h2_style))
    table_data = [["Country", "Risk score", "Inflation %", "Debt/GDP %", "GDP growth %", "Pol. stability"]]
    for _, row in scores.iterrows():
        table_data.append([
            row["country_name"],
            f"{row['risk_score']:.0f}",
            f"{row['inflation_pct']:.1f}",
            f"{row['debt_to_gdp_pct']:.1f}",
            f"{row['gdp_growth_pct']:.1f}",
            f"{row['political_stability_est']:.2f}",
        ])
    t = Table(table_data, colWidths=[28 * mm, 20 * mm, 22 * mm, 22 * mm, 24 * mm, 24 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)

    story.append(Paragraph("Limitations", h2_style))
    story.append(Paragraph(
        "Equal weighting is a simplifying assumption; the score is relative to this country sample only, "
        "not absolute; and it excludes banking-specific data (NPL ratios, external debt, FX reserves) "
        "that a full bank-risk assessment would include. World Bank data lags 1-2 years.",
        body_style,
    ))

    doc.build(story)
    print("Saved summary.pdf")


if __name__ == "__main__":
    build()
