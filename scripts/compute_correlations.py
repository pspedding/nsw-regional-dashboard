#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "sa2_kpi_wide.csv"
OUTPUT_JSON = ROOT / "public" / "data" / "correlations.json"

NON_METRIC_COLUMNS = {
    "SA2 Code",
    "SA2 Name",
    "Region (SA3)",
    "LGA Name",
}
EXCLUDE_METRICS = {"LGA Code"}
MIN_ABS_CORRELATION = 0.3
TOP_N = 5
MIN_ROWS_PER_LGA = 8


def clean_float(value):
    if pd.isna(value):
        return None
    return float(round(value, 6))


def metric_columns_for(df):
    cols = [
        c for c in df.columns
        if c not in NON_METRIC_COLUMNS
        and c not in EXCLUDE_METRICS
        and not c.endswith(" Code")
        and pd.api.types.is_numeric_dtype(df[c])
    ]
    return cols


def compute_scope(df):
    metric_columns = metric_columns_for(df)
    metric_df = df[metric_columns].copy().replace([np.inf, -np.inf], np.nan)
    corr = metric_df.corr(method="pearson")

    result = {
        "row_count": int(len(df)),
        "metric_count": len(metric_columns),
        "indicators": {}
    }

    for indicator in metric_columns:
        series = corr[indicator].drop(labels=[indicator]).dropna()
        filtered = series[series.abs() >= MIN_ABS_CORRELATION]
        positive = filtered[filtered > 0].sort_values(ascending=False).head(TOP_N)
        negative = filtered[filtered < 0].sort_values(ascending=True).head(TOP_N)
        result["indicators"][indicator] = {
            "method": "pearson",
            "positive": [{"indicator": idx, "value": clean_float(val)} for idx, val in positive.items()],
            "negative": [{"indicator": idx, "value": clean_float(val)} for idx, val in negative.items()],
        }
    return result


def main():
    df = pd.read_csv(INPUT_CSV)
    if "LGA Code" in df.columns:
        df["LGA Code"] = df["LGA Code"].astype(str)

    result = {
        "meta": {
            "source": INPUT_CSV.name,
            "method": "pearson",
            "min_abs_correlation": MIN_ABS_CORRELATION,
            "top_n": TOP_N,
            "min_rows_per_lga": MIN_ROWS_PER_LGA,
        },
        "global": compute_scope(df),
        "by_lga": {}
    }

    for lga_code, group in df.groupby("LGA Code", dropna=True):
        if len(group) < MIN_ROWS_PER_LGA:
            continue
        lga_scope = compute_scope(group)
        lga_scope["lga_name"] = str(group["LGA Name"].dropna().iloc[0]) if "LGA Name" in group.columns and group["LGA Name"].notna().any() else None
        result["by_lga"][str(lga_code)] = lga_scope

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Wrote {OUTPUT_JSON}")
    print(f"Global metrics analysed: {result['global']['metric_count']}")
    print(f"LGA scopes written: {len(result['by_lga'])}")
    sample = next(iter(result['global']['indicators']))
    print(f"Sample global indicator: {sample}")
    print(json.dumps(result['global']['indicators'][sample], indent=2))


if __name__ == "__main__":
    main()
