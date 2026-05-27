#!/usr/bin/env bash
# validate_before_push.sh
# Run this BEFORE any git commit touching the dashboard.
# Fails loudly if protected files are missing or index.html has regressed.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

echo "=== Dashboard pre-push validation ==="

# ── 1. index.html must exist and meet minimum line count ──────────────────
INDEX="$REPO/index.html"
if [ ! -f "$INDEX" ]; then
  echo "❌ FAIL: index.html is missing"
  FAIL=1
else
  LINES=$(wc -l < "$INDEX")
  echo "   index.html: $LINES lines"
  if [ "$LINES" -lt 1500 ]; then
    echo "❌ FAIL: index.html has $LINES lines — expected ≥1500. Likely overwritten with an old version."
    FAIL=1
  else
    echo "   ✅ Line count OK"
  fi
fi

# ── 2. index.html must contain required feature signatures ────────────────
REQUIRED_STRINGS=(
  "intelligence-tab-btn"
  "intelligence-wrap"
  "analytics-panel"
  "LOCKED_LGA_CODE"
  "selectFirstSA2"
  "applyUrlParams"
  "marked.min.js"
)

for str in "${REQUIRED_STRINGS[@]}"; do
  if ! grep -q "$str" "$INDEX" 2>/dev/null; then
    echo "❌ FAIL: index.html is missing required feature: '$str'"
    FAIL=1
  else
    echo "   ✅ Feature present: $str"
  fi
done

# ── 3. reports/central-coast.md must exist ────────────────────────────────
REPORT="$REPO/reports/central-coast.md"
if [ ! -f "$REPORT" ]; then
  echo "❌ FAIL: reports/central-coast.md is missing — do not delete Intelligence Report source"
  FAIL=1
else
  RLINES=$(wc -l < "$REPORT")
  echo "   reports/central-coast.md: $RLINES lines ✅"
fi

# ── 4. data.js must exist and not be empty ───────────────────────────────
if [ ! -s "$REPO/data.js" ]; then
  echo "❌ FAIL: data.js is missing or empty"
  FAIL=1
else
  echo "   ✅ data.js present"
fi

# ── 5. Check that index.html diff only touches allowed lines ─────────────
# (only warn — can't enforce without knowing base commit intent)
DIFF_LINES=$(git -C "$REPO" diff --cached -- index.html 2>/dev/null | grep "^[+-]" | grep -v "^[+-][+-][+-]" | wc -l || echo "0")
DIFF_LINES=$(echo "$DIFF_LINES" | tr -d ' ')
if [ "${DIFF_LINES:-0}" -gt 0 ] 2>/dev/null; then
  echo ""
  echo "⚠️  WARNING: index.html has $DIFF_LINES changed lines staged."
  echo "   Data refresh commits should NOT touch index.html except script cache-bust versions."
  echo "   Allowed changes in index.html: script src ?v=XXXXXXXX version numbers only."
  echo "   If you are making a feature change, this warning is expected."
  echo ""
  # Check if any non-version-bump lines are changing
  NON_VERSION=$(git -C "$REPO" diff --cached -- index.html 2>/dev/null \
    | grep "^[+-]" | grep -v "^[+-][+-][+-]" \
    | grep -v "?v=[0-9]" || true)
  if [ -n "$NON_VERSION" ]; then
    echo "   Changed lines beyond version bumps:"
    echo "$NON_VERSION" | head -20
  fi
fi

echo ""
if [ "$FAIL" -eq 1 ]; then
  echo "❌ Validation FAILED — do not push. Fix the issues above first."
  exit 1
else
  echo "✅ All checks passed. Safe to push."
  exit 0
fi
