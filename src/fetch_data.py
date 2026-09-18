"""
fetch_data.py

Downloads:
- Inflation from World Bank WDI
- GDP growth from World Bank WDI
- Political Stability from World Bank WGI
- General government gross debt from IMF WEO

Output:
    data/raw_indicators.csv
"""

import os
import time

import pandas as pd
import requests


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

COUNTRIES = {
    "UKR": "Ukraine",
    "POL": "Poland",
    "HUN": "Hungary",
    "ROU": "Romania",
    "SRB": "Serbia",
    "AUT": "Austria",
}


# Common historical period used by the project.
START_YEAR = 2019
END_YEAR = 2024

REQUEST_TIMEOUT = 60
MAX_RETRIES = 3


# ---------------------------------------------------------------------
# World Bank
# ---------------------------------------------------------------------

WORLD_BANK_URL = (
    "https://api.worldbank.org/v2/"
    "country/{country}/indicator/{indicator}"
)


WORLD_BANK_INDICATORS = {
    "FP.CPI.TOTL.ZG": "inflation_pct",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct",
    "GOV_WGI_PV_EST": "political_stability_est",
}


# ---------------------------------------------------------------------
# IMF World Economic Outlook
# ---------------------------------------------------------------------

# IMF WEO / DataMapper indicator:
# General government gross debt, percent of GDP.
IMF_DEBT_INDICATOR = "GGXWDG_NGDP"

IMF_URL = (
    "https://www.imf.org/external/datamapper/api/v2/"
    f"{IMF_DEBT_INDICATOR}"
)


# ---------------------------------------------------------------------
# Empty dataframe
# ---------------------------------------------------------------------

def empty_dataframe():

    return pd.DataFrame(
        columns=[
            "country_code",
            "indicator_code",
            "year",
            "value",
        ]
    )


# ---------------------------------------------------------------------
# Generic request helper
# ---------------------------------------------------------------------

def make_request(url, params=None):

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as exc:

            if attempt < MAX_RETRIES:

                wait_seconds = 2 ** attempt

                print(
                    f"  ! request failed "
                    f"(attempt {attempt}/{MAX_RETRIES})"
                )

                print(
                    f"    retrying in "
                    f"{wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

            else:

                print(
                    f"  ! failed after "
                    f"{MAX_RETRIES} attempts: {exc}"
                )

    return None


# ---------------------------------------------------------------------
# Fetch World Bank indicator
# ---------------------------------------------------------------------

def fetch_world_bank_indicator(
    country_code,
    indicator_code,
):

    url = WORLD_BANK_URL.format(
        country=country_code,
        indicator=indicator_code,
    )

    params = {
        "format": "json",
        "per_page": 100,
        "date": f"{START_YEAR}:{END_YEAR}",
    }

    payload = make_request(
        url,
        params,
    )

    if (
        not isinstance(payload, list)
        or len(payload) < 2
        or payload[1] is None
    ):

        print(
            f"  ! no data for "
            f"{country_code} / {indicator_code}"
        )

        return empty_dataframe()

    rows = []

    for record in payload[1]:

        value = record.get("value")

        if value is None:
            continue

        rows.append(
            {
                "country_code": country_code,
                "indicator_code": indicator_code,
                "year": int(record["date"]),
                "value": float(value),
            }
        )

    if not rows:

        print(
            f"  ! no data for "
            f"{country_code} / {indicator_code}"
        )

        return empty_dataframe()

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Fetch IMF WEO debt
# ---------------------------------------------------------------------

def fetch_imf_debt(country_code):

    params = {
        "periods": ",".join(
            str(year)
            for year in range(
                START_YEAR,
                END_YEAR + 1,
            )
        )
    }

    payload = make_request(
        IMF_URL,
        params,
    )

    if not isinstance(payload, dict):

        print(
            f"  ! no IMF data for {country_code}"
        )

        return empty_dataframe()

    values = payload.get("values", {})

    indicator_values = values.get(
        IMF_DEBT_INDICATOR,
        {}
    )

    country_values = indicator_values.get(
        country_code,
        {}
    )

    if not country_values:

        print(
            f"  ! no IMF debt data for "
            f"{country_code}"
        )

        return empty_dataframe()

    rows = []

    for year_text, value in country_values.items():

        if value is None:
            continue

        try:
            year = int(year_text)
        except ValueError:
            continue

        if year < START_YEAR or year > END_YEAR:
            continue

        rows.append(
            {
                "country_code": country_code,
                "indicator_code": IMF_DEBT_INDICATOR,
                "year": year,
                "value": float(value),
            }
        )

    if not rows:

        print(
            f"  ! no IMF debt data for "
            f"{country_code}"
        )

        return empty_dataframe()

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():

    all_frames = []

    for country_code, country_name in COUNTRIES.items():

        # -------------------------------------------------------------
        # World Bank indicators
        # -------------------------------------------------------------

        for indicator_code in WORLD_BANK_INDICATORS:

            print(
                f"Fetching "
                f"{country_name} / "
                f"{indicator_code} ..."
            )

            df = fetch_world_bank_indicator(
                country_code,
                indicator_code,
            )

            all_frames.append(df)

            time.sleep(0.2)

        # -------------------------------------------------------------
        # IMF WEO debt
        # -------------------------------------------------------------

        print(
            f"Fetching "
            f"{country_name} / "
            f"{IMF_DEBT_INDICATOR} "
            f"(IMF WEO debt) ..."
        )

        df = fetch_imf_debt(
            country_code
        )

        all_frames.append(df)

        time.sleep(0.2)

    # -----------------------------------------------------------------
    # Combine
    # -----------------------------------------------------------------

    raw = pd.concat(
        all_frames,
        ignore_index=True,
    )

    # Human-readable country names.
    raw["country_name"] = raw["country_code"].map(
        COUNTRIES
    )

    # Human-readable metric names.
    indicator_names = {
        "FP.CPI.TOTL.ZG": "inflation_pct",
        "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct",
        "GOV_WGI_PV_EST": "political_stability_est",
        "GGXWDG_NGDP": "debt_to_gdp_pct",
    }

    raw["metric_name"] = raw["indicator_code"].map(
        indicator_names
    )

    # Keep the same structure expected by compute_score.py.
    raw = raw[
        [
            "country_code",
            "country_name",
            "indicator_code",
            "metric_name",
            "year",
            "value",
        ]
    ]

    raw = raw.sort_values(
        [
            "country_code",
            "indicator_code",
            "year",
        ]
    )

    # -----------------------------------------------------------------
    # Save
    # -----------------------------------------------------------------

    os.makedirs(
        "data",
        exist_ok=True,
    )

    output_path = (
        "data/raw_indicators.csv"
    )

    raw.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved {len(raw)} rows "
        f"to {output_path}"
    )

    print(
        "\nDownloaded observations:"
    )

    summary = (
        raw.groupby(
            [
                "country_code",
                "indicator_code",
            ]
        )
        .size()
        .unstack(
            fill_value=0
        )
    )

    print(summary)


if __name__ == "__main__":
    main()
