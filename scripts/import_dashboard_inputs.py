#!/usr/bin/env python3
"""
Import dashboard source files and regenerate:
- data.js
- indicator-lookup.js
- sa2_kpi_wide.csv
- all_lgas_sa2.geojson (subset to current workbook SA2s)

This importer also merges:
- trend directions from Output-Trends.csv -> trend_<indicator>
- prior-period values from Output-Mapped-SA2-Level-Data-Pivot-All-LGAs-Prior-Month.xlsx -> prior_<indicator>
"""
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "inputs"
DATA_XLSX = INPUT_DIR / "Output-Mapped-SA2-Level-Data-Pivot-All-LGAs.xlsx"
LOOKUP_XLSX = INPUT_DIR / "Output-Indicator-Lookup.xlsx"
PRIOR_XLSX = INPUT_DIR / "Output-Mapped-SA2-Level-Data-Pivot-All-LGAs-Prior-Month.xlsx"
TRENDS_CSV = INPUT_DIR / "Output-Trends.csv"
QUARTERLY_TRENDS_XLSX = INPUT_DIR / "Output-Trends-Quarterly.xlsx"
SHAPEFILE = Path("/home/azureuser/council-work/sa2-dashboard/shapefile/SA2_2021_AUST_GDA2020.shp")

DATA_JS = ROOT / "data.js"
LOOKUP_JS = ROOT / "indicator-lookup.js"
DATA_CSV = ROOT / "sa2_kpi_wide.csv"
GEOJSON_OUT = ROOT / "all_lgas_sa2.geojson"
TREND_SERIES_JSON = ROOT / "public" / "data" / "trend_series.json"

TREND_COLUMN_MAP = {
    "Trent.Labour Force": "Labour Force",
    "Trend.Unemployment": "Unemployment",
    "Trend.Unemployment Rate (%)": "Unemployment Rate (%)",
    "Trend.Jobseeker": "JobSeeker Payment",
    "Trend.Value of building job(s)": "Value of building job(s)",
    "Trend.Number of dwellings approved": "Number of dwellings approved",
    "Trend.Visitor Spend": "Visitor Spend",
    "Trend.Resident Spend": "Resident Spend",
    "Trend.House Price (Current)": "House Price (Current)",
    "Trend.House Rent (P/W)": "House Rent (P/W)",
    "Trend.Unit Price (Current)": "Unit Price (Current)",
    "Trend.Unit Rent (P/W)": "Unit Rent (P/W)",
    "Trend. Airbnb ADR": "Airbnb ADR",
    "Trend.Airbnb Gross Revenue": "Airbnb  Gross Revenue",
    "Trend.Homelessness": "Homelessness",
    "Trend.Total Businesses": "Total Businesses",
    "Trend.Healthcare Businesses": "Healthcare Businesses",
    "Trend.Tourism Businesses": "Tourism Businesses",
    "Trend.Manufacturing Businesses": "Manufacturing Businesses",
}

TREND_SERIES_INDICATOR_MAP = {
    "Unemployment Rate": "Unemployment Rate (%)",
    "Age Pension": "Age Pension",
    "JobSeeker Payment": "JobSeeker Payment",
}

ID_COLUMNS = {"SA2 Code", "SA2 Name", "Region (SA3)", "LGA Code", "LGA Name"}


def to_native(val):
    if pd.isna(val):
        return None
    if isinstance(val, pd.Timestamp):
        return val.strftime("%Y-%m-%d")
    if hasattr(val, "item"):
        try:
            return val.item()
        except Exception:
            pass
    return val


def normalize_main_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["SA2 Code", "SA2 Name"]).copy()
    df["SA2 Code"] = df["SA2 Code"].astype(int).astype(str)
    if "LGA Code" in df.columns:
        df["LGA Code"] = df["LGA Code"].astype("Int64").astype(str)
    df = df.drop_duplicates(subset=["SA2 Code"], keep="last")
    return df


def load_current_table() -> pd.DataFrame:
    df = pd.read_excel(DATA_XLSX, sheet_name="SA2 Data")
    return normalize_main_table(df)


def merge_trends(df: pd.DataFrame) -> pd.DataFrame:
    if not TRENDS_CSV.exists():
        return df
    trends = pd.read_csv(TRENDS_CSV)
    trends = normalize_main_table(trends)
    keep_cols = ["SA2 Code"] + [c for c in TREND_COLUMN_MAP if c in trends.columns]
    trends = trends[keep_cols].copy()
    trends = trends.rename(columns={src: f"trend_{dest}" for src, dest in TREND_COLUMN_MAP.items() if src in trends.columns})
    return df.merge(trends, on="SA2 Code", how="left")


def merge_prior_period(df: pd.DataFrame) -> pd.DataFrame:
    if not PRIOR_XLSX.exists():
        return df
    prior = pd.read_excel(PRIOR_XLSX, sheet_name="SA2 Data")
    prior = normalize_main_table(prior)
    metric_cols = [c for c in prior.columns if c not in ID_COLUMNS]
    prior = prior[["SA2 Code"] + metric_cols].copy()
    prior = prior.rename(columns={c: f"prior_{c}" for c in metric_cols})
    return df.merge(prior, on="SA2 Code", how="left")


def write_data_outputs(df: pd.DataFrame):
    # Keep the CSV lean for Python analytics scripts, but include merged fields in data.js for UI use.
    csv_df = df[[c for c in df.columns if not c.startswith("trend_") and not c.startswith("prior_")]].copy()
    csv_df.to_csv(DATA_CSV, index=False)

    records = [{col: to_native(row[col]) for col in df.columns} for _, row in df.iterrows()]
    DATA_JS.write_text("const SA2_DATA = " + json.dumps(records, indent=2, ensure_ascii=False) + ";\n", encoding="utf-8")


def write_lookup_output():
    df = pd.read_excel(LOOKUP_XLSX, sheet_name="Indicator Lookup")
    df = df.dropna(subset=["Indicator"]).copy()
    lookup = {}
    for _, row in df.iterrows():
        indicator = str(row["Indicator"]).strip()
        lookup[indicator] = {
            "contentArea": to_native(row.get("Content Area")),
            "frequency": to_native(row.get("Data Frequency")),
            "dataset": to_native(row.get("Dataset")),
            "latestPeriod": to_native(row.get("Latest Period")),
        }
    LOOKUP_JS.write_text("const INDICATOR_LOOKUP = " + json.dumps(lookup, indent=2, ensure_ascii=False) + ";\n", encoding="utf-8")


def write_geojson_subset(df: pd.DataFrame):
    gdf = gpd.read_file(SHAPEFILE)
    sa2_codes = set(df["SA2 Code"].astype(str))
    subset = gdf[gdf["SA2_CODE21"].astype(str).isin(sa2_codes)].copy()
    subset.to_file(GEOJSON_OUT, driver="GeoJSON")
    missing = sorted(sa2_codes - set(subset["SA2_CODE21"].astype(str)))
    return len(subset), missing


def write_trend_series_json(current_df: pd.DataFrame):
    TREND_SERIES_JSON.parent.mkdir(parents=True, exist_ok=True)
    if not QUARTERLY_TRENDS_XLSX.exists():
        TREND_SERIES_JSON.write_text(json.dumps({"meta": {"available": False}, "periods": [], "by_sa2": {}}, indent=2), encoding="utf-8")
        return 0

    df = pd.read_excel(QUARTERLY_TRENDS_XLSX, sheet_name=0)
    df = df.dropna(subset=["SA2 Code", "SA2 Name", "Indicator"]).copy()
    df["SA2 Code"] = df["SA2 Code"].astype(int).astype(str)
    periods = [c for c in df.columns if c not in {"SA2 Code", "SA2 Name", "Indicator"}]
    valid_codes = set(current_df["SA2 Code"].astype(str))
    df = df[df["SA2 Code"].isin(valid_codes)].copy()

    out = {
        "meta": {
            "available": True,
            "source": QUARTERLY_TRENDS_XLSX.name,
            "period_count": len(periods),
            "series_count": int(len(df)),
        },
        "periods": periods,
        "by_sa2": {}
    }

    for _, row in df.iterrows():
        code = row["SA2 Code"]
        indicator = TREND_SERIES_INDICATOR_MAP.get(str(row["Indicator"]).strip(), str(row["Indicator"]).strip())
        if code not in out["by_sa2"]:
            out["by_sa2"][code] = {"sa2_name": row["SA2 Name"], "series": {}}
        out["by_sa2"][code]["series"][indicator] = [to_native(row[p]) for p in periods]

    TREND_SERIES_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(out["by_sa2"])


def main():
    for path in [DATA_XLSX, LOOKUP_XLSX, SHAPEFILE]:
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}")

    df = load_current_table()
    df = merge_trends(df)
    df = merge_prior_period(df)

    write_data_outputs(df)
    write_lookup_output()
    feature_count, missing = write_geojson_subset(df)
    trend_series_sa2 = write_trend_series_json(df)

    print(f"Rows written: {len(df)}")
    print(f"Columns written to data.js: {len(df.columns)}")
    print(f"Trend fields merged: {len([c for c in df.columns if c.startswith('trend_')])}")
    print(f"Prior fields merged: {len([c for c in df.columns if c.startswith('prior_')])}")
    print(f"Quarterly trend series SA2s: {trend_series_sa2}")
    print(f"GeoJSON features written: {feature_count}")
    print(f"Unique LGAs: {df['LGA Code'].nunique() if 'LGA Code' in df.columns else 'n/a'}")
    if missing:
        print(f"Missing SA2 geometries: {len(missing)}")
        print(missing[:20])
    else:
        print("All workbook SA2s matched to geometry")


if __name__ == "__main__":
    main()
