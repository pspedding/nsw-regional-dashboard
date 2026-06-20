#!/usr/bin/env bash
# refresh_from_dropbox.sh
# Syncs dashboard source files from Dropbox:/Moltbot/Economic-Dashboard/
# then regenerates data.js / indicator-lookup.js and deploys to GitHub Pages.
#
# Expected files in Dropbox:/Moltbot/Economic-Dashboard/:
#   Output-Mapped-SA2-Level-Data-Pivot-All-LGAs.xlsx   (required)
#   Output-Indicator-Lookup.xlsx                        (required)
#   Output-Trends.csv                                   (required)
#   Output-Mapped-SA2-Level-Data-Pivot-All-LGAs-Prior-Month.xlsx  (optional)
#
# Usage:
#   bash scripts/refresh_from_dropbox.sh
#   bash scripts/refresh_from_dropbox.sh --dry-run    (sync only, no commit/push)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
INPUTS_DIR="$REPO_DIR/inputs"
DROPBOX_PATH="dropbox:Moltbot/Economic-Dashboard"
DRY_RUN=false

[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

echo "========================================="
echo " Dashboard Refresh from Dropbox"
echo " $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "========================================="

# ── 1. Sync from Dropbox ──────────────────────────────────────────────
echo ""
echo ">> Step 1: Syncing from $DROPBOX_PATH ..."
# Use 'copy' not 'sync' -- only copy files that exist in Dropbox, never delete locals
rclone copy "$DROPBOX_PATH" "$INPUTS_DIR" \
  --include "Output-Mapped-SA2-Level-Data-Pivot-All-LGAs.xlsx" \
  --include "Output-Indicator-Lookup.xlsx" \
  --include "Output-Trends.csv" \
  --include "Output-Mapped-SA2-Level-Data-Pivot-All-LGAs-Prior-Month.xlsx" \
  --progress

echo "   Files in inputs/:"
ls -lh "$INPUTS_DIR"/*.xlsx "$INPUTS_DIR"/*.csv 2>/dev/null | awk '{print "   ", $5, $NF}'

# Check required files exist
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
echo ">> Step 2: Running import script ..."
cd "$REPO_DIR"
python3 scripts/import_dashboard_inputs.py

# ── 3. Validate ───────────────────────────────────────────────────────
echo ""
echo ">> Step 3: Validating ..."
if [[ -f "$REPO_DIR/scripts/validate_before_push.sh" ]]; then
  bash "$REPO_DIR/scripts/validate_before_push.sh"
else
  echo "   (no validate_before_push.sh found, skipping)"
fi

if $DRY_RUN; then
  echo ""
  echo ">> DRY RUN complete. No commit/push performed."
  exit 0
fi

# ── 4. Commit & push ─────────────────────────────────────────────────
echo ""
echo ">> Step 4: Committing and pushing ..."
cd "$REPO_DIR"

# Stage generated files + inputs
git add data.js indicator-lookup.js sa2_kpi_wide.csv \
        public/data/trend_series.json \
        inputs/Output-Mapped-SA2-Level-Data-Pivot-All-LGAs.xlsx \
        inputs/Output-Indicator-Lookup.xlsx \
        inputs/Output-Trends.csv 2>/dev/null || true

# Optional prior-month file
git add inputs/Output-Mapped-SA2-Level-Data-Pivot-All-LGAs-Prior-Month.xlsx 2>/dev/null || true

# Only commit if there are staged changes
if git diff --cached --quiet; then
  echo "   No changes detected -- dashboard is already up to date."
else
  PERIOD=$(python3 -c "
import json, re
src = open('indicator-lookup.js').read()
m = re.search(r'const INDICATOR_LOOKUP\s*=\s*(\{[\s\S]+?\});', src)
d = json.loads(m.group(1))
periods = sorted([v['latestPeriod'] for v in d.values() if v.get('latestPeriod') and v.get('frequency') == 'Monthly'], reverse=True)
print(periods[0][:7] if periods else 'unknown')
" 2>/dev/null || echo "unknown")

  git commit -m "chore: monthly data refresh ($PERIOD) via Dropbox sync"
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
