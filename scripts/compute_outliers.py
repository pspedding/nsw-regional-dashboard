#!/usr/bin/env python3
"""Compute regression-residual outliers globally and per LGA."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import linregress

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "sa2_kpi_wide.csv"
OUTPUT_JSON = ROOT / "public" / "data" / "outliers.json"

NON_METRIC_COLUMNS = {"SA2 Code", "SA2 Name", "Region (SA3)", "LGA Name"}
EXCLUDE_METRICS = {"LGA Code"}
TOP_N_OUTLIERS = 5
MIN_POINTS = 8
RESIDUAL_Z_THRESHOLD = 1.75
MIN_ROWS_PER_LGA = 8


def safe_float(v):
    return None if pd.isna(v) else float(round(v, 6))


def metric_columns_for(df):
    return [
        c for c in df.columns
        if c not in NON_METRIC_COLUMNS
        and c not in EXCLUDE_METRICS
        and not c.endswith(" Code")
        and pd.api.types.is_numeric_dtype(df[c])
    ]


def explain_residual(y_metric, x_metric, resid_z):
    direction = "Higher" if resid_z > 0 else "Lower"
    return f"{direction} {y_metric} than expected given {x_metric}"


def pair_outliers(sub, x_metric, y_metric):
    x = sub[x_metric].astype(float).values
    y = sub[y_metric].astype(float).values
    if len(x) < MIN_POINTS:
        return None
    if np.nanstd(x) < 1e-9 or np.nanstd(y) < 1e-9:
        return None

    fit = linregress(x, y)
    y_hat = fit.intercept + fit.slope * x
    residuals = y - y_hat
    resid_sd = np.std(residuals, ddof=1)
    if resid_sd < 1e-9:
        return None

    resid_z = residuals / resid_sd
    ranked_idx = np.argsort(np.abs(resid_z))[::-1]
    outliers = []
    for idx in ranked_idx:
        score = float(abs(resid_z[idx]))
        if score < RESIDUAL_Z_THRESHOLD:
            continue
        signed = float(resid_z[idx])
        outliers.append({
            "row_idx": int(idx),
            "score": round(score, 4),
            "signed_residual_z": round(signed, 4),
            "expected_y": round(float(y_hat[idx]), 4),
            "actual_y": round(float(y[idx]), 4),
            "residual": round(float(residuals[idx]), 4),
            "reason": explain_residual(y_metric, x_metric, signed),
        })
        if len(outliers) >= TOP_N_OUTLIERS:
            break

    return {
        "slope": round(float(fit.slope), 6),
        "intercept": round(float(fit.intercept), 6),
        "r_value": round(float(fit.rvalue), 6),
        "r_squared": round(float(fit.rvalue ** 2), 6),
        "outliers": outliers,
    }


def compute_scope(df):
    metric_cols = metric_columns_for(df)
    id_cols = ["SA2 Code", "SA2 Name"]
    result = {
        "row_count": int(len(df)),
        "metric_count": len(metric_cols),
        "pairs": {}
    }

    for i, x_metric in enumerate(metric_cols):
        for y_metric in metric_cols[i + 1:]:
            sub = df[id_cols + [x_metric, y_metric]].dropna(subset=[x_metric, y_metric]).reset_index(drop=True)
            pair = pair_outliers(sub, x_metric, y_metric)
            if not pair:
                continue

            pair_key = f"{x_metric}||{y_metric}"
            outliers = []
            for item in pair["outliers"]:
                idx = item.pop("row_idx")
                outliers.append({
                    "sa2_code": int(sub.at[idx, "SA2 Code"]) if pd.notna(sub.at[idx, "SA2 Code"]) else None,
                    "sa2_name": sub.at[idx, "SA2 Name"],
                    "score": item["score"],
                    "signed_residual_z": item["signed_residual_z"],
                    "expected_y": item["expected_y"],
                    "actual_y": item["actual_y"],
                    "residual": item["residual"],
                    "x_val": safe_float(sub.at[idx, x_metric]),
                    "y_val": safe_float(sub.at[idx, y_metric]),
                    "reason": item["reason"],
                })
            result["pairs"][pair_key] = {
                "x": x_metric,
                "y": y_metric,
                "slope": pair["slope"],
                "intercept": pair["intercept"],
                "r_value": pair["r_value"],
                "r_squared": pair["r_squared"],
                "outliers": outliers,
            }
    return result


def main():
    df = pd.read_csv(INPUT_CSV)
    if "LGA Code" in df.columns:
        df["LGA Code"] = df["LGA Code"].astype(str)

    result = {
        "meta": {
            "source": INPUT_CSV.name,
            "method": "regression_residuals",
            "top_n": TOP_N_OUTLIERS,
            "min_points": MIN_POINTS,
            "residual_z_threshold": RESIDUAL_Z_THRESHOLD,
            "min_rows_per_lga": MIN_ROWS_PER_LGA,
        },
        "global": compute_scope(df),
        "by_lga": {}
    }

    for lga_code, group in df.groupby("LGA Code", dropna=True):
        if len(group) < MIN_ROWS_PER_LGA:
            continue
        scope = compute_scope(group)
        scope["lga_name"] = str(group["LGA Name"].dropna().iloc[0]) if "LGA Name" in group.columns and group["LGA Name"].notna().any() else None
        result["by_lga"][str(lga_code)] = scope

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Wrote {OUTPUT_JSON}")
    print(f"Global pairs computed: {len(result['global']['pairs'])}")
    print(f"LGA scopes written: {len(result['by_lga'])}")
    if result['global']['pairs']:
        sample_key = next(iter(result['global']['pairs']))
        s = result['global']['pairs'][sample_key]
        print(f"Sample pair: {s['x']} vs {s['y']} (R^2={s['r_squared']})")
        for o in s['outliers'][:3]:
            print(f"  {o['sa2_name']}: z={o['signed_residual_z']} :: {o['reason']}")


if __name__ == "__main__":
    main()
