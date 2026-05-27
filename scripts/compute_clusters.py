#!/usr/bin/env python3
"""Compute k-means clusters for scatter plot overlays, globally and per LGA."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "sa2_kpi_wide.csv"
OUTPUT_JSON = ROOT / "public" / "data" / "clusters.json"

NON_METRIC_COLUMNS = {"SA2 Code", "SA2 Name", "Region (SA3)", "LGA Name"}
EXCLUDE_METRICS = {"LGA Code"}
K_MIN = 2
K_MAX = 5
MIN_COVERAGE = 0.5
RANDOM_STATE = 42
MIN_ROWS_PER_LGA = 8


def metric_columns_for(df):
    return [
        c for c in df.columns
        if c not in NON_METRIC_COLUMNS
        and c not in EXCLUDE_METRICS
        and not c.endswith(" Code")
        and pd.api.types.is_numeric_dtype(df[c])
    ]


def silhouette_score_safe(X, labels):
    from sklearn.metrics import silhouette_score
    unique = np.unique(labels)
    if len(unique) < 2:
        return -1.0
    return float(silhouette_score(X, labels))


def best_k(X_scaled, k_min, k_max):
    best_score = -1.0
    best_k_ = k_min
    best_labels = None
    for k in range(k_min, k_max + 1):
        if k >= len(X_scaled):
            break
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        labels = km.fit_predict(X_scaled)
        score = silhouette_score_safe(X_scaled, labels)
        if score > best_score:
            best_score = score
            best_k_ = k
            best_labels = labels
    return best_k_, best_score, best_labels


def compute_scope(df):
    metric_cols = metric_columns_for(df)
    id_cols = ["SA2 Code", "SA2 Name"]
    result = {
        "row_count": int(len(df)),
        "metric_count": len(metric_cols),
        "pairs": {}
    }

    for i, mx in enumerate(metric_cols):
        for my in metric_cols[i + 1:]:
            sub = df[id_cols + [mx, my]].dropna(subset=[mx, my])
            coverage = len(sub) / len(df)
            if len(sub) < K_MIN + 1 or coverage < MIN_COVERAGE:
                continue

            X = sub[[mx, my]].values.astype(float)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            k, score, labels = best_k(X_scaled, K_MIN, K_MAX)
            if labels is None:
                continue

            pair_key = f"{mx}||{my}"
            result["pairs"][pair_key] = {
                "x": mx,
                "y": my,
                "k": k,
                "silhouette": round(score, 4),
                "coverage": round(coverage, 4),
                "assignments": [
                    {
                        "sa2_code": int(row["SA2 Code"]) if pd.notna(row["SA2 Code"]) else None,
                        "sa2_name": row["SA2 Name"],
                        "cluster": int(labels[idx]),
                    }
                    for idx, (_, row) in enumerate(sub.iterrows())
                ]
            }
    return result


def main():
    df = pd.read_csv(INPUT_CSV)
    if "LGA Code" in df.columns:
        df["LGA Code"] = df["LGA Code"].astype(str)

    result = {
        "meta": {
            "source": INPUT_CSV.name,
            "method": "kmeans",
            "k_range": [K_MIN, K_MAX],
            "min_coverage": MIN_COVERAGE,
            "random_state": RANDOM_STATE,
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
        print(f"Sample pair: {s['x']} vs {s['y']} → k={s['k']}, silhouette={s['silhouette']}")


if __name__ == "__main__":
    main()
