#!/usr/bin/env bash
# refresh_from_dropbox.sh
# Syncs dashboard source files from Dropbox:/Moltbot/Economic-Dashboard/
# then regenerates ALL dashboard components and deploys to GitHub Pages.
#
# Expected files in Dropbox:/Moltbot/Economic-Dashboard/:
#   Output-Mapped-SA2-Level-Data-Pivot-All-LGAs.xlsx   (required)
#   Output-Indicator-Lookup.xlsx                        (required)
#   Output-Trends.csv                                   (required)
#   Output-Mapped-SA2-Level-Data-Pivot-All-LGAs-Prior-Month.xlsx  (optional)
#
# Components refreshed:
#   1. Sync input files from Dropbox
#   2. data.js + indicator-lookup.js  (map/bar/dropdown)
#   3. correlations.json              (Analytics panel - Pearson correlations)
#   4. clusters.json                  (Analytics panel - k-means)
#   5. outliers.json                  (Analytics panel - Mahalanobis)
#   6. trend_series.json              (sparklines)
#   7. central-coast.md               (Intelligence Report - LLM regenerated)
#   8. central-coast.docx             (Word download)
#   9. index.html cache-bust + QA system prompt date
#  10. Validate + commit + push
#
# Usage:
#   bash scripts/refresh_from_dropbox.sh
#   bash scripts/refresh_from_dropbox.sh --dry-run    (sync + regenerate, no commit/push)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
INPUTS_DIR="$REPO_DIR/inputs"
DROPBOX_PATH="dropbox:Moltbot/Economic-Dashboard"
DRY_RUN=false

[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

echo "========================================="
echo " Dashboard Full Refresh from Dropbox"
echo " $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "========================================="

# ── 1. Sync from Dropbox ──────────────────────────────────────────────
echo ""
echo ">> Step 1: Syncing from $DROPBOX_PATH ..."
# Sync all xlsx/csv from Dropbox, then rename to canonical hyphenated names
rclone copy "$DROPBOX_PATH" "$INPUTS_DIR" \
  --include "*.xlsx" \
  --include "*.csv" \
  --progress

# Normalize Dropbox filenames (spaces/dashes vary) to canonical names expected by scripts
for SRC in \
  "Output  - Indicator Lookup.xlsx" \
  "Output - Indicator Lookup.xlsx"; do
  [[ -f "$INPUTS_DIR/$SRC" ]] && mv -f "$INPUTS_DIR/$SRC" "$INPUTS_DIR/Output-Indicator-Lookup.xlsx" && echo "   Renamed: $SRC" || true
done
for SRC in \
  "Output - Mapped SA2 Level Data (Pivot) - All LGAs.xlsx" \
  "Output - Mapped SA2 Level Data (Pivot) - All LGAs - Prior Month.xlsx"; do
  if [[ -f "$INPUTS_DIR/$SRC" ]]; then
    if [[ "$SRC" == *"Prior Month"* ]]; then
      mv -f "$INPUTS_DIR/$SRC" "$INPUTS_DIR/Output-Mapped-SA2-Level-Data-Pivot-All-LGAs-Prior-Month.xlsx" && echo "   Renamed: $SRC"
    else
      mv -f "$INPUTS_DIR/$SRC" "$INPUTS_DIR/Output-Mapped-SA2-Level-Data-Pivot-All-LGAs.xlsx" && echo "   Renamed: $SRC"
    fi
  fi
done

echo "   Files in inputs/:"
ls -lh "$INPUTS_DIR"/*.xlsx "$INPUTS_DIR"/*.csv 2>/dev/null | awk '{print "   ", $5, $NF}'

for f in \
  "$INPUTS_DIR/Output-Mapped-SA2-Level-Data-Pivot-All-LGAs.xlsx" \
  "$INPUTS_DIR/Output-Indicator-Lookup.xlsx" \
  "$INPUTS_DIR/Output-Trends.csv"; do
  if [[ ! -f "$f" ]]; then
    echo "ERROR: Required file missing: $f"
    exit 1
  fi
done

# ── 2. Regenerate data.js + indicator-lookup.js ───────────────────────
echo ""
echo ">> Step 2: Regenerating data.js + indicator-lookup.js ..."
cd "$REPO_DIR"
python3 scripts/import_dashboard_inputs.py

# ── 3. Regenerate analytics JSON files ───────────────────────────────
echo ""
echo ">> Step 3: Recomputing correlations (Analytics panel) ..."
python3 scripts/compute_correlations.py

echo ">> Step 3b: Recomputing outliers (Analytics panel) ..."
python3 scripts/compute_outliers.py

echo ">> Step 3c: Recomputing clusters (Analytics panel) ..."
if [[ -f "$REPO_DIR/scripts/compute_clusters.py" ]]; then
  python3 scripts/compute_clusters.py
else
  echo "   (compute_clusters.py not found, skipping)"
fi

echo "   Analytics JSON files updated."

# ── 4. Regenerate Intelligence Report (LLM) ──────────────────────────
echo ""
echo ">> Step 4: Regenerating Intelligence Report via LLM ..."
if python3 scripts/generate_intelligence_report.py; then
  echo "   central-coast.md regenerated."
else
  echo "   WARN: Intelligence Report generation failed. Keeping existing file."
fi

# ── 5. Regenerate Word download ───────────────────────────────────────
echo ""
echo ">> Step 5: Regenerating Word download ..."
if command -v pandoc &>/dev/null; then
  for MD in "$REPO_DIR"/reports/*.md; do
    BASE="$(basename "$MD" .md)"
    DOCX="$REPO_DIR/reports/${BASE}.docx"
    pandoc "$MD" --from markdown --to docx --standalone --output "$DOCX" 2>/dev/null \
      && echo "   Generated: reports/${BASE}.docx" \
      || echo "   WARN: docx generation failed for $BASE.md"
  done
else
  echo "   WARN: pandoc not found, skipping Word generation"
fi

# ── 6. Update cache-buster + QA system prompt date in index.html ─────
echo ""
echo ">> Step 6: Updating cache-buster and QA prompt date in index.html ..."
TS=$(date +%s)
sed -i "s/indicator-lookup\.js?v=[0-9]*/indicator-lookup.js?v=${TS}/g" "$REPO_DIR/index.html"
sed -i "s/data\.js?v=[0-9]*/data.js?v=${TS}/g" "$REPO_DIR/index.html"

# Update the "indicators as at <Month YYYY>" date in the QA system prompt
PERIOD_LABEL=$(python3 -c "
import re, json
from datetime import datetime
src = open('indicator-lookup.js').read()
periods = re.findall(r'\"latestPeriod\"\s*:\s*\"([^\"]+)\"', src)
monthly = sorted(set(p for p in periods if len(p) >= 7), reverse=True)
label = datetime.strptime(monthly[0][:7], '%Y-%m').strftime('%B %Y') if monthly else datetime.now().strftime('%B %Y')
print(label)
" 2>/dev/null || date '+%B %Y')

# Update the date in the QA system prompt (two patterns: script and index.html inline)
sed -i "s/indicators as at [A-Za-z]* [0-9]\{4\}/indicators as at ${PERIOD_LABEL}/g" "$REPO_DIR/index.html"
# Also update the Dataset(...) label passed to the model
sed -i "s/Dataset ([A-Za-z]* [0-9]\{4\})/Dataset (${PERIOD_LABEL})/g" "$REPO_DIR/index.html"

echo "   Cache-buster: $TS | QA date: $PERIOD_LABEL"

# ── 7. Validate ───────────────────────────────────────────────────────
echo ""
echo ">> Step 7: Validating ..."
bash "$REPO_DIR/scripts/validate_before_push.sh"

if $DRY_RUN; then
  echo ""
  echo ">> DRY RUN complete. No commit/push performed."
  exit 0
fi

# ── 8. Commit & push ─────────────────────────────────────────────────
echo ""
echo ">> Step 8: Committing and pushing ..."
cd "$REPO_DIR"

git add data.js index.html indicator-lookup.js sa2_kpi_wide.csv \
        public/data/correlations.json public/data/outliers.json \
        public/data/trend_series.json \
        inputs/Output-Mapped-SA2-Level-Data-Pivot-All-LGAs.xlsx \
        inputs/Output-Indicator-Lookup.xlsx \
        inputs/Output-Trends.csv \
        "inputs/Output  - Time-series Trends.xlsx" \
        reports/central-coast.md \
        reports/central-coast.docx 2>/dev/null || true

git add inputs/Output-Mapped-SA2-Level-Data-Pivot-All-LGAs-Prior-Month.xlsx 2>/dev/null || true

# Stage clusters if it exists
git add public/data/clusters.json 2>/dev/null || true

if git diff --cached --quiet; then
  echo "   No changes detected -- dashboard is already up to date."
else
  PERIOD=$(python3 -c "
import re
from datetime import datetime
src = open('indicator-lookup.js').read()
periods = re.findall(r'\"latestPeriod\"\s*:\s*\"([^\"]+)\"', src)
monthly = sorted(set(p for p in periods if len(p) >= 7), reverse=True)
label = datetime.strptime(monthly[0][:7], '%Y-%m').strftime('%b %Y') if monthly else 'unknown'
print(label)
" 2>/dev/null || echo "unknown")

  git commit -m "chore: full dashboard refresh ($PERIOD) — data, analytics, intelligence report, QA"
  git push origin main
  git push dev main:gh-pages
  echo ""
  echo "   Pushed to origin/main and dev/gh-pages."
  echo "   GitHub Pages will rebuild in ~1-2 minutes."
fi

echo ""
echo "========================================="
echo " Refresh complete!"
echo "========================================="

# ── Auto-schedule Buffer posts ────────────────────────────────────────────────
echo ""
echo "→ Scheduling Council data posts to Buffer (X + LinkedIn)..."
source /etc/clawdbot/clawdbot.env
cd /home/azureuser/council-work
python3 social_posts_from_emails.py \
  --since "$(date -d '45 days ago' +%Y-%m-%d)" \
  --schedule-mwf "$(date -d 'next Monday' +%Y-%m-%d)" \
  --schedule-time 09:00 \
  --schedule-tz Australia/Sydney \
  && echo "   ✅ Buffer posts scheduled — review at https://publish.buffer.com" \
  || echo "   ❌ Buffer scheduling failed — run social_posts_from_emails.py manually"
