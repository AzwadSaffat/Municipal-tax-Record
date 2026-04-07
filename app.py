from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re

import pandas as pd
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "ccc_holding_data_collection.xlsx"
SHEET_NAME = "Holding"

EXPECTED_COLUMNS = [
    "holding",
    "circle_office",
    "ward",
    "moholla",
    "rate",
    "owner_name",
    "holding_name",
    "swo_relation",
    "swo_name",
    "address",
    "mobile",
    "type",
    "beneficiary_type",
    "note",
]

DISPLAY_COLUMNS = [
    "holding",
    "circle_office",
    "ward",
    "moholla",
    "rate",
    "owner_name",
    "holding_name",
    "swo_relation",
    "swo_name",
    "address",
    "mobile",
    "type",
]


def normalize_column_name(name: str) -> str:
    """Normalize incoming Excel column names safely."""
    normalized = re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower())
    return normalized.strip("_")


def ensure_expected_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Guarantee expected columns exist even if source file misses some."""
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df


def load_data() -> pd.DataFrame:
    """Load and normalize municipal tax data from Excel file."""
    if not DATA_FILE.exists():
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    df = pd.read_excel(DATA_FILE, sheet_name=SHEET_NAME, engine="openpyxl")
    df.columns = [normalize_column_name(c) for c in df.columns]
    df = ensure_expected_columns(df)
    df = df[EXPECTED_COLUMNS].copy()

    # Clean common null-like values and prepare text-safe columns.
    for col in EXPECTED_COLUMNS:
        df[col] = df[col].fillna("")
        if col != "rate":
            df[col] = df[col].astype(str).str.strip()

    # Keep rate as string for robust filtering/search display.
    df["rate"] = df["rate"].astype(str).str.strip()

    return df


def apply_search_and_filters(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Apply case-insensitive search and multi-filter logic."""
    filtered = df.copy()

    search_text = params.get("search", "").strip().lower()
    if search_text:
        mask = (
            filtered["owner_name"].str.lower().str.contains(search_text, na=False)
            | filtered["holding"].str.lower().str.contains(search_text, na=False)
            | filtered["swo_name"].str.lower().str.contains(search_text, na=False)
        )
        filtered = filtered[mask]

    for column in ["ward", "moholla", "rate", "type"]:
        value = params.get(column, "").strip().lower()
        if value:
            filtered = filtered[filtered[column].str.lower() == value]

    return filtered


def build_summary(df: pd.DataFrame) -> dict:
    """Create top-level dashboard summary metrics."""
    incomplete_mask = (
        (df["owner_name"].str.strip() == "")
        | (df["mobile"].str.strip() == "")
        | (df["moholla"].str.strip() == "")
    )

    return {
        "total_records": int(len(df)),
        "total_wards": int(df["ward"].replace("", pd.NA).dropna().nunique()),
        "total_mohollas": int(df["moholla"].replace("", pd.NA).dropna().nunique()),
        "incomplete_records": int(incomplete_mask.sum()),
    }


def build_validation(df: pd.DataFrame) -> dict:
    """Generate data quality insights counts."""
    missing_owner = (df["owner_name"].str.strip() == "").sum()
    missing_mobile = (df["mobile"].str.strip() == "").sum()
    missing_moholla = (df["moholla"].str.strip() == "").sum()

    total_incomplete = (
        (df["owner_name"].str.strip() == "")
        | (df["mobile"].str.strip() == "")
        | (df["moholla"].str.strip() == "")
    ).sum()

    return {
        "missing_owner_name": int(missing_owner),
        "missing_mobile": int(missing_mobile),
        "missing_moholla": int(missing_moholla),
        "total_incomplete_rows": int(total_incomplete),
    }


def _sorted_value_list(series: pd.Series) -> list[str]:
    return sorted([v for v in series.dropna().astype(str).str.strip().unique() if v])


def build_filter_options(df: pd.DataFrame) -> dict:
    """Build dropdown option values from full dataset."""
    return {
        "wards": _sorted_value_list(df["ward"]),
        "mohollas": _sorted_value_list(df["moholla"]),
        "rates": _sorted_value_list(df["rate"]),
        "types": _sorted_value_list(df["type"]),
    }


def build_chart_data(df: pd.DataFrame) -> dict:
    """Prepare labels and data arrays for Chart.js visualizations."""
    ward_counts = (
        df[df["ward"].str.strip() != ""]["ward"]
        .value_counts()
        .sort_index()
        .to_dict()
    )
    moholla_counts = (
        df[df["moholla"].str.strip() != ""]["moholla"]
        .value_counts()
        .sort_values(ascending=False)
        .head(12)
        .to_dict()
    )
    rate_counts = (
        df[df["rate"].str.strip() != ""]["rate"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    return {
        "ward": {"labels": list(ward_counts.keys()), "values": list(ward_counts.values())},
        "moholla": {
            "labels": list(moholla_counts.keys()),
            "values": list(moholla_counts.values()),
        },
        "rate": {"labels": list(rate_counts.keys()), "values": list(rate_counts.values())},
    }


@app.route("/")
def index():
    df = load_data()
    filters = {
        "search": request.args.get("search", ""),
        "ward": request.args.get("ward", ""),
        "moholla": request.args.get("moholla", ""),
        "rate": request.args.get("rate", ""),
        "type": request.args.get("type", ""),
    }

    filtered_df = apply_search_and_filters(df, filters)

    context = {
        "summary": build_summary(filtered_df),
        "validation": build_validation(filtered_df),
        "chart_data": build_chart_data(filtered_df),
        "filter_options": build_filter_options(df),
        "filters": filters,
        "rows": filtered_df[DISPLAY_COLUMNS].to_dict(orient="records"),
        "columns": DISPLAY_COLUMNS,
    }

    return render_template("index.html", **context)


@app.route("/export")
def export_filtered():
    df = load_data()
    filters = {
        "search": request.args.get("search", ""),
        "ward": request.args.get("ward", ""),
        "moholla": request.args.get("moholla", ""),
        "rate": request.args.get("rate", ""),
        "type": request.args.get("type", ""),
    }

    filtered_df = apply_search_and_filters(df, filters)
    output_df = filtered_df[DISPLAY_COLUMNS].copy()

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        output_df.to_excel(writer, index=False, sheet_name="FilteredData")

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="filtered_tax_records.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    app.run(debug=True)
