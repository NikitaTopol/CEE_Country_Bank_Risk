import os

import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams["font.size"] = 10


def plot_risk_ranking():
    scores = (
        pd.read_csv("data/risk_scores.csv")
        .sort_values("risk_score", ascending=True)
    )

    fig, ax = plt.subplots(figsize=(9, 5.5))

    bars = ax.barh(
        scores["country_name"],
        scores["risk_score"],
    )

    for bar, value in zip(bars, scores["risk_score"]):
        ax.text(
            value + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}",
            va="center",
            fontsize=10,
        )

    ax.set_xlabel(
        "Composite risk score "
        "(higher = higher relative risk)"
    )

    ax.set_title(
        "Country Bank Risk Score Ranking",
        fontsize=15,
        pad=15,
    )

    ax.set_xlim(0, 100)

    ax.grid(
        axis="x",
        alpha=0.25,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.text(
        0.01,
        0.01,
        "Source: World Bank WDI/WGI and IMF WEO. "
        "Score is relative to the six-country sample.",
        fontsize=8,
    )

    fig.tight_layout(rect=[0, 0.04, 1, 1])

    path = os.path.join(
        OUTPUT_DIR,
        "risk_score_ranking.png",
    )

    fig.savefig(
        path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Saved {path}")


def plot_inflation_trend():
    raw = pd.read_csv("data/raw_indicators.csv")

    infl = raw[
        raw["metric_name"] == "inflation_pct"
    ].copy()

    fig, ax = plt.subplots(figsize=(9, 5.5))

    for code, grp in infl.groupby("country_code"):
        grp = grp.sort_values("year")

        name = grp["country_name"].iloc[0]

        ax.plot(
            grp["year"],
            grp["value"],
            marker="o",
            linewidth=1.8,
            label=name,
        )

    ax.set_xlabel("Year")

    ax.set_ylabel(
        "Inflation, consumer prices (annual %)"
    )

    ax.set_title(
        "Inflation Trend by Country",
        fontsize=15,
        pad=15,
    )

    ax.set_xticks(
        sorted(infl["year"].unique())
    )

    ax.grid(
        alpha=0.25,
    )

    ax.legend(
        loc="upper left",
        fontsize=9,
        frameon=False,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.text(
        0.01,
        0.01,
        "Source: World Bank World Development Indicators.",
        fontsize=8,
    )

    fig.tight_layout(rect=[0, 0.04, 1, 1])

    path = os.path.join(
        OUTPUT_DIR,
        "inflation_trend.png",
    )

    fig.savefig(
        path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Saved {path}")


def create_pdf_summary():
    scores = pd.read_csv(
        "data/risk_scores.csv"
    )

    latest = pd.read_csv(
        "data/latest_values_wide.csv"
    )

    scores = scores.sort_values(
        "risk_score",
        ascending=False,
    )

    latest_wide = latest.pivot(
        index="country_code",
        columns="metric_name",
        values="value",
    )

    latest_wide["country_name"] = (
        latest.drop_duplicates("country_code")
        .set_index("country_code")["country_name"]
    )

    latest_wide = latest_wide.loc[
        scores["country_code"]
    ]

    pdf_path = os.path.join(
        OUTPUT_DIR,
        "country_risk_summary.pdf",
    )

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=13 * mm,
        bottomMargin=13 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=18,
        leading=21,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleCustom",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        spaceBefore=6,
        spaceAfter=5,
    )

    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11,
        spaceAfter=5,
    )

    story = []

    story.append(
        Paragraph(
            "Country Bank Risk Dashboard",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "CEE country-risk comparison | 2024 snapshot",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            "Composite Risk Scores",
            heading_style,
        )
    )

    score_data = [
        [
            "Rank",
            "Country",
            "Risk score",
        ]
    ]

    for rank, (_, row) in enumerate(
        scores.iterrows(),
        start=1,
    ):
        score_data.append(
            [
                str(rank),
                row["country_name"],
                f"{row['risk_score']:.1f}",
            ]
        )

    score_table = Table(
        score_data,
        colWidths=[
            20 * mm,
            70 * mm,
            35 * mm,
        ],
    )

    score_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#eeeeee"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (0, -1),
                    "CENTER",
                ),
                (
                    "ALIGN",
                    (2, 1),
                    (2, -1),
                    "CENTER",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8.5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(score_table)

    story.append(
        Spacer(1, 7)
    )

    story.append(
        Paragraph(
            "Latest Indicator Values",
            heading_style,
        )
    )

    indicator_data = [
        [
            "Country",
            "Inflation %",
            "Debt / GDP %",
            "GDP growth %",
            "Political stability",
        ]
    ]

    for _, row in scores.iterrows():

        code = row["country_code"]
        values = latest_wide.loc[code]

        indicator_data.append(
            [
                row["country_name"],
                f"{values['inflation_pct']:.1f}",
                f"{values['debt_to_gdp_pct']:.1f}",
                f"{values['gdp_growth_pct']:.1f}",
                f"{values['political_stability_est']:.2f}",
            ]
        )

    indicator_table = Table(
        indicator_data,
        colWidths=[
            34 * mm,
            27 * mm,
            30 * mm,
            27 * mm,
            34 * mm,
        ],
    )

    indicator_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#eeeeee"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7.2,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    story.append(indicator_table)

    story.append(
        Spacer(1, 8)
    )

    story.append(
        Paragraph(
            "Methodology",
            heading_style,
        )
    )

    methodology = (
        "The model combines four indicators: inflation, general government "
        "gross debt, GDP growth, and Political Stability. Each indicator is "
        "min-max normalized across the six countries. GDP growth and Political "
        "Stability are inverted because higher values generally correspond "
        "to lower risk. The four components receive equal weights of 25%. "
        "The resulting score ranges from 0 to 100 within the selected sample, "
        "with higher values indicating higher relative risk."
    )

    story.append(
        Paragraph(
            methodology,
            body_style,
        )
    )

    story.append(
        Paragraph(
            "<b>Data sources:</b> World Bank World Development Indicators "
            "(WDI), World Bank Worldwide Governance Indicators (WGI), and "
            "IMF World Economic Outlook (WEO) DataMapper.",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "<b>Important:</b> This score is a simplified comparative "
            "indicator, not an absolute probability of default or an official "
            "credit-risk assessment. Results depend on the selected countries, "
            "indicators, normalization method, and equal-weight assumption.",
            body_style,
        )
    )

    doc.build(story)

    print(f"Saved {pdf_path}")


if __name__ == "__main__":
    plot_risk_ranking()
    plot_inflation_trend()
    create_pdf_summary()
