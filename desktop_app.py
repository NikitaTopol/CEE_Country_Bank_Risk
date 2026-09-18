import sys
from pathlib import Path

import pandas as pd

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)


COUNTRIES = {
    "UKR": "Ukraine",
    "POL": "Poland",
    "HUN": "Hungary",
    "ROU": "Romania",
    "SRB": "Serbia",
    "AUT": "Austria",
}

METRICS = {
    "inflation_pct": ("Inflation", "%"),
    "debt_to_gdp_pct": ("Government Debt", "% GDP"),
    "gdp_growth_pct": ("GDP Growth", "%"),
    "political_stability_est": ("Political Stability", "WGI"),
}

NORMALIZED_METRICS = {
    "inflation_pct_norm": "Inflation Risk",
    "debt_to_gdp_pct_norm": "Debt Risk",
    "gdp_growth_pct_norm": "Growth Risk",
    "political_stability_est_norm": "Political Stability Risk",
}

DATA_FILE = Path(__file__).resolve().parent / "data" / "risk_scores.csv"


def risk_category(score):
    if score >= 70:
        return "High Risk"
    elif score >= 45:
        return "Medium Risk"
    else:
        return "Low Risk"


def category_style(category):
    if category == "High Risk":
        return """
            QLabel {
                background: #ffe5e5;
                color: #b42318;
                border: 1px solid #f5b5b5;
                border-radius: 8px;
                padding: 7px 14px;
                font-weight: bold;
            }
        """
    elif category == "Medium Risk":
        return """
            QLabel {
                background: #fff3d6;
                color: #9a6700;
                border: 1px solid #f0d58a;
                border-radius: 8px;
                padding: 7px 14px;
                font-weight: bold;
            }
        """
    else:
        return """
            QLabel {
                background: #e3f5e8;
                color: #18794e;
                border: 1px solid #b8dfc4;
                border-radius: 8px;
                padding: 7px 14px;
                font-weight: bold;
            }
        """


class CountryRiskApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Country Bank Risk Dashboard")
        self.resize(1250, 800)

        self.data = pd.read_csv(DATA_FILE)
        self.data["country_name"] = self.data["country_code"].map(COUNTRIES)

        self.setup_style()
        self.setup_ui()

    def setup_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #f4f6f8;
            }

            QWidget {
                color: #202124;
                font-family: Arial;
            }

            QTabWidget::pane {
                border: none;
                background: #f4f6f8;
            }

            QTabBar::tab {
                background: #e5e7eb;
                color: #4b5563;
                padding: 10px 24px;
                margin-right: 2px;
                border-radius: 6px;
                font-size: 14px;
            }

            QTabBar::tab:selected {
                background: #ffffff;
                color: #111827;
                font-weight: bold;
            }

            QPushButton {
                background: #ffffff;
                color: #202124;
                border: 1px solid #d1d5db;
                border-radius: 7px;
                padding: 10px 16px;
                font-size: 14px;
            }

            QPushButton:hover {
                background: #eef2f7;
                border: 1px solid #9ca3af;
            }

            QPushButton:pressed {
                background: #e5e7eb;
            }

            QTableWidget {
                background: #ffffff;
                color: #202124;
                border: 1px solid #d9dde3;
                border-radius: 8px;
                gridline-color: #e5e7eb;
                font-size: 14px;
            }

            QHeaderView::section {
                background: #f0f2f5;
                color: #374151;
                border: none;
                border-bottom: 1px solid #d9dde3;
                padding: 10px;
                font-weight: bold;
            }

            QProgressBar {
                background: #e5e7eb;
                border: none;
                border-radius: 5px;
                height: 10px;
                text-align: center;
            }

            QProgressBar::chunk {
                background: #64748b;
                border-radius: 5px;
            }
        """)

    def setup_ui(self):

        self.tabs = QTabWidget()

        self.overview_tab = QWidget()
        self.comparison_tab = QWidget()
        self.methodology_tab = QWidget()

        self.tabs.addTab(self.overview_tab, "Overview")
        self.tabs.addTab(self.comparison_tab, "Comparison")
        self.tabs.addTab(self.methodology_tab, "Methodology")

        self.setCentralWidget(self.tabs)

        self.build_overview()
        self.build_comparison()
        self.build_methodology()

        self.show_country("UKR")

    def build_overview(self):

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 30)
        layout.setSpacing(16)

        title = QLabel("Country Bank Risk Dashboard")
        title.setStyleSheet(
            "font-size: 30px; font-weight: bold; color: #111827;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Composite country risk assessment for Central and Eastern Europe"
        )
        subtitle.setStyleSheet(
            "font-size: 15px; color: #6b7280;"
        )
        layout.addWidget(subtitle)

        countries_layout = QHBoxLayout()
        countries_layout.setSpacing(8)

        for code, name in COUNTRIES.items():

            button = QPushButton(name)
            button.setCursor(Qt.PointingHandCursor)

            button.clicked.connect(
                lambda checked=False, c=code: self.show_country(c)
            )

            countries_layout.addWidget(button)

        layout.addLayout(countries_layout)

        country_card = QFrame()
        country_card.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 1px solid #e1e5ea;
                border-radius: 12px;
            }
        """)

        country_layout = QVBoxLayout(country_card)
        country_layout.setContentsMargins(25, 22, 25, 22)

        self.country_label = QLabel()
        self.country_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #111827;"
        )
        country_layout.addWidget(self.country_label)

        self.score_label = QLabel()
        self.score_label.setStyleSheet(
            "font-size: 38px; font-weight: bold; color: #111827;"
        )
        country_layout.addWidget(self.score_label)

        self.category_label = QLabel()
        country_layout.addWidget(self.category_label)

        self.year_label = QLabel("Latest data: 2024")
        self.year_label.setStyleSheet(
            "font-size: 13px; color: #6b7280; margin-top: 8px;"
        )
        country_layout.addWidget(self.year_label)

        layout.addWidget(country_card)

        indicators_title = QLabel("Key Indicators")
        indicators_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #111827; margin-top: 5px;"
        )
        layout.addWidget(indicators_title)

        self.metrics_layout = QHBoxLayout()
        self.metrics_layout.setSpacing(12)
        layout.addLayout(self.metrics_layout)

        risk_title = QLabel("Risk Components")
        risk_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #111827; margin-top: 8px;"
        )
        layout.addWidget(risk_title)

        self.risk_layout = QVBoxLayout()
        self.risk_layout.setSpacing(10)
        layout.addLayout(self.risk_layout)

        layout.addStretch()

        self.overview_tab.setLayout(layout)

    def show_country(self, code):

        row = self.data[
            self.data["country_code"] == code
        ].iloc[0]

        country_name = COUNTRIES.get(code, code)
        score = float(row["risk_score"])
        category = risk_category(score)

        self.country_label.setText(country_name)

        self.score_label.setText(
            f"{score:.1f} / 100"
        )

        self.category_label.setText(category)
        self.category_label.setStyleSheet(
            category_style(category)
        )

        while self.metrics_layout.count():

            item = self.metrics_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        for column, (name, unit) in METRICS.items():

            value = float(row[column])

            card = QFrame()
            card.setMinimumHeight(125)

            card.setStyleSheet("""
                QFrame {
                    background: #ffffff;
                    border: 1px solid #e1e5ea;
                    border-radius: 10px;
                }
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 15, 15, 15)

            name_label = QLabel(name)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet(
                "font-size: 13px; color: #6b7280; font-weight: bold;"
            )

            value_label = QLabel(f"{value:.2f}")
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet(
                "font-size: 25px; font-weight: bold; color: #111827;"
            )

            unit_label = QLabel(unit)
            unit_label.setAlignment(Qt.AlignCenter)
            unit_label.setStyleSheet(
                "font-size: 12px; color: #9ca3af;"
            )

            card_layout.addWidget(name_label)
            card_layout.addWidget(value_label)
            card_layout.addWidget(unit_label)

            self.metrics_layout.addWidget(card)

        while self.risk_layout.count():

            item = self.risk_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        for column, name in NORMALIZED_METRICS.items():

            risk_value = float(row[column])

            row_widget = QWidget()
            row_layout = QVBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)

            header_layout = QHBoxLayout()

            label = QLabel(name)
            label.setStyleSheet(
                "font-size: 13px; color: #374151;"
            )

            value = QLabel(f"{risk_value:.1f}")
            value.setStyleSheet(
                "font-size: 13px; font-weight: bold; color: #111827;"
            )

            header_layout.addWidget(label)
            header_layout.addStretch()
            header_layout.addWidget(value)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(round(risk_value)))
            bar.setTextVisible(False)

            row_layout.addLayout(header_layout)
            row_layout.addWidget(bar)

            self.risk_layout.addWidget(row_widget)

    def build_comparison(self):

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 30)

        title = QLabel("Country Comparison")
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #111827;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Composite risk scores across the six-country sample"
        )
        subtitle.setStyleSheet(
            "font-size: 14px; color: #6b7280; margin-bottom: 12px;"
        )
        layout.addWidget(subtitle)

        table = QTableWidget()

        table.setRowCount(len(self.data))
        table.setColumnCount(3)

        table.setHorizontalHeaderLabels(
            ["Country", "Risk Score", "Risk Level"]
        )

        sorted_data = self.data.sort_values(
            "risk_score",
            ascending=False
        )

        for row_index, (_, row) in enumerate(
            sorted_data.iterrows()
        ):

            country = row["country_name"]
            score = float(row["risk_score"])
            category = risk_category(score)

            table.setItem(
                row_index,
                0,
                QTableWidgetItem(str(country))
            )

            table.setItem(
                row_index,
                1,
                QTableWidgetItem(f"{score:.1f}")
            )

            table.setItem(
                row_index,
                2,
                QTableWidgetItem(category)
            )

        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )
        table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )

        table.setMinimumHeight(350)

        layout.addWidget(table)

        note = QLabel(
            "Higher scores indicate higher relative risk within this sample."
        )
        note.setStyleSheet(
            "font-size: 13px; color: #6b7280; margin-top: 10px;"
        )
        layout.addWidget(note)

        self.comparison_tab.setLayout(layout)

    def build_methodology(self):

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 30)

        title = QLabel("Methodology")
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #111827;"
        )
        layout.addWidget(title)

        text = QLabel(
            """
            <h3>Composite Risk Score</h3>

            The dashboard calculates a relative country risk score from
            0 to 100 using four indicators:

            <ul>
                <li>Inflation</li>
                <li>General government gross debt (% of GDP)</li>
                <li>GDP growth</li>
                <li>Political Stability</li>
            </ul>

            <h3>Calculation</h3>

            Indicators are normalized using min-max normalization across
            the six-country sample.

            GDP growth and Political Stability are inverted because
            higher values correspond to lower risk.

            Each indicator receives an equal weight of 25%.

            <h3>Interpretation</h3>

            <b>0</b> = lowest relative risk within the sample<br>
            <b>100</b> = highest relative risk within the sample

            <h3>Data</h3>

            Latest available observations are used for each country and
            indicator. The current dataset contains 2024 observations.

            <h3>Limitations</h3>

            The score is a relative country-risk indicator. It is not a
            banking-specific default probability and does not incorporate
            bank-level financial ratios, market spreads, or uncertainty
            estimates.
            """
        )

        text.setWordWrap(True)
        text.setStyleSheet(
            """
            QLabel {
                background: #ffffff;
                border: 1px solid #e1e5ea;
                border-radius: 10px;
                padding: 22px;
                font-size: 14px;
                color: #374151;
            }
            """
        )

        layout.addWidget(text)
        layout.addStretch()

        self.methodology_tab.setLayout(layout)


def main():

    app = QApplication(sys.argv)

    window = CountryRiskApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
