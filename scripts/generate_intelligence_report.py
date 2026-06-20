#!/usr/bin/env python3
"""
generate_intelligence_report.py
Regenerates reports/central-coast.md using the Anthropic API + live SA2 data.
Called as part of the monthly dashboard refresh.

Usage:
    python3 scripts/generate_intelligence_report.py
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

import anthropic
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SA2_CSV = ROOT / "sa2_kpi_wide.csv"
INDICATOR_LOOKUP_JS = ROOT / "indicator-lookup.js"
OUTPUT_MD = ROOT / "reports" / "central-coast.md"
TARGET_LGA = "Central Coast"
TARGET_LGA_CODE = "11650"

# ── Load data ─────────────────────────────────────────────────────────
df = pd.read_csv(SA2_CSV)
df_lga = df[df["LGA Code"].astype(str) == TARGET_LGA_CODE].copy()

if df_lga.empty:
    print(f"ERROR: No rows found for LGA code {TARGET_LGA_CODE}")
    sys.exit(1)

print(f"Loaded {len(df_lga)} SA2 rows for {TARGET_LGA} (LGA {TARGET_LGA_CODE})")

# ── Determine latest data period from indicator-lookup.js ─────────────
import re

lookup_src = INDICATOR_LOOKUP_JS.read_text()
period_matches = re.findall(r'"latestPeriod"\s*:\s*"([^"]+)"', lookup_src)
freq_monthly = re.findall(r'"frequency"\s*:\s*"Monthly"', lookup_src)
monthly_periods = period_matches[:len(freq_monthly)]  # rough alignment
latest_period = sorted(set(monthly_periods), reverse=True)[0][:7] if monthly_periods else datetime.now().strftime("%B %Y")
# Convert YYYY-MM to "Month YYYY"
try:
    latest_period_label = datetime.strptime(latest_period, "%Y-%m").strftime("%B %Y")
except Exception:
    latest_period_label = latest_period

print(f"Latest data period: {latest_period_label}")

# ── Build compact JSON dataset for the prompt ─────────────────────────
# Include all numeric columns with meaningful data coverage
def coverage(col):
    return df_lga[col].notna().sum() / len(df_lga)

EXCLUDE = {"SA2 Code", "LGA Code"}
metric_cols = [
    c for c in df_lga.columns
    if c not in EXCLUDE
    and pd.api.types.is_numeric_dtype(df_lga[c])
    and coverage(c) >= 0.5
]
text_cols = ["SA2 Name", "Region (SA3)", "LGA Name"]

rows = []
for _, row in df_lga.iterrows():
    r = {c: row[c] for c in text_cols if pd.notna(row.get(c))}
    for c in metric_cols:
        v = row.get(c)
        if pd.notna(v):
            r[c] = round(float(v), 2) if isinstance(v, float) else v
    rows.append(r)

dataset_json = json.dumps(rows, separators=(",", ":"))
print(f"Dataset size: {len(dataset_json):,} chars across {len(metric_cols)} metric columns")

# ── Call Anthropic ────────────────────────────────────────────────────
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not set")
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)

system_prompt = f"""You are a senior regional economist writing an intelligence report for Central Coast Council (NSW).
Write a structured Markdown report about the Central Coast LGA using ONLY the dataset provided.
Do NOT use outside knowledge. All statistics must come directly from the dataset.

Report structure (use these exact headings):
# Central Coast SA2 Intelligence Report
(subtitle line: Prepared date, indicators period, data coverage)

## Executive Summary
(4-6 sentence overview with 5 headline findings as a numbered list)

## 1. Population & Demographics
(population, growth, age profile, migration, indigenous, language)

## 2. Economic Activity & Business
(businesses by type, labour force, unemployment, JobSeeker, income)

## 3. Housing & Affordability
(house/unit prices and rents, dwellings approved, building value, price-to-income ratio)

## 4. Socioeconomic Wellbeing
(SEIFA indices, welfare payments, homelessness, education)

## 5. Crime & Safety
(assault, theft, drug offences, malicious damage, intimidation rates per 1,000 — compare SA2s; note if data sparse)

## 6. Tourism & Visitor Economy
(Airbnb metrics, visitor vs resident spend)

## 7. Regional Divide: Gosford vs Wyong
(compare the two SA3 sub-regions across key indicators)

## 8. Key Challenges & Opportunities
(3-5 dot points each)

## Data Notes
(coverage, period, sources)

Formatting rules:
- Use **bold** for key numbers and suburb names
- Use tables where comparing multiple SA2s side by side
- Be specific: always name suburbs, give exact numbers
- Concise but comprehensive — aim for ~800-1200 words body text
- Date header: "Prepared: {datetime.now().strftime('%B %Y')} | Indicators: {latest_period_label} | Data Coverage: {len(df_lga)} SA2 areas, Central Coast LGA (NSW)"
"""

user_prompt = f"""Generate the Central Coast SA2 Intelligence Report using this dataset:

{dataset_json}"""

print("Calling Anthropic claude-sonnet-4-5 ...")
message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": user_prompt}
    ],
    system=system_prompt,
)

report_md = message.content[0].text
print(f"Generated {len(report_md):,} chars, {report_md.count(chr(10))} lines")

# ── Write output ──────────────────────────────────────────────────────
OUTPUT_MD.write_text(report_md, encoding="utf-8")
print(f"Written: {OUTPUT_MD}")
print("Done.")
