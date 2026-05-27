# Dashboard Update Process

> **READ THIS BEFORE TOUCHING ANY FILE IN THIS REPO.**
> This document defines the only safe way to do a monthly data refresh.
> Deviating from it caused a major regression on 2026-05-27.

---

## What a "data refresh" is

A data refresh means updating the dashboard with new monthly indicator data.
It **only** updates data files. It does **not** change the app logic or UI.

## Step 1 — Place input files

Copy the following files from Dropbox into `inputs/`:

| File | Description |
|------|-------------|
| `Output-Mapped-SA2-Level-Data-Pivot-All-LGAs.xlsx` | Current month SA2 KPIs |
| `Output-Mapped-SA2-Level-Data-Pivot-All-LGAs-Prior-Month.xlsx` | Prior month (for trend arrows) |
| `Output-Indicator-Lookup.xlsx` | Indicator metadata |
| `Output-Trends.csv` | Monthly trend directions |
| `Output-Trends-Quarterly.xlsx` | Quarterly trend series |

## Step 2 — Run the import script

```bash
cd /home/azureuser/council-work/nsw-regional-dashboard
python3 scripts/import_dashboard_inputs.py
```

This regenerates **only these files** — nothing else should change:

| File | Changed by data refresh? |
|------|--------------------------|
| `data.js` | ✅ YES |
| `indicator-lookup.js` | ✅ YES |
| `sa2_kpi_wide.csv` | ✅ YES |
| `all_lgas_sa2.geojson` | ✅ YES (if SA2 set changes) |
| `public/data/*.json` | ✅ YES (run analytics scripts) |
| `inputs/*.xlsx / *.csv` | ✅ YES (source files copied in) |
| **`index.html`** | ❌ **NEVER** — do not touch |
| **`reports/central-coast.md`** | ❌ **NEVER** — do not delete |
| **`public/reports/*.md`** | ❌ **NEVER** — do not delete |

## Step 3 — Update the script src cache-bust version in index.html

The **only** allowed change to `index.html` during a data refresh is bumping the
`?v=XXXXXXXXXX` cache-busting parameter on the two script tags:

```html
<script src="indicator-lookup.js?v=XXXXXXXXXX"></script>
<script src="data.js?v=XXXXXXXXXX"></script>
```

Use the current unix timestamp: `date +%s`

Use a targeted edit — do NOT rewrite or overwrite `index.html`. Use `edit` or `sed`, not `write`.

## Step 4 — Run analytics scripts

```bash
python3 scripts/compute_correlations.py
python3 scripts/compute_clusters.py
python3 scripts/compute_outliers.py
```

## Step 5 — Validate before committing

```bash
bash scripts/validate_before_push.sh
```

**Do not commit if this script fails.**

## Step 6 — Commit and push

Commit only the data files. Example commit message:
```
data: refresh dashboard with June 2026 data (May indicators)
```

Push to both remotes:
```bash
git push origin main
git push dev main
```

---

## ⛔ What NOT to do

- **Never** overwrite `index.html` with a full file write during a data refresh
- **Never** use `write` tool on `index.html` — only use `edit` with targeted replacements
- **Never** delete anything in `reports/`
- **Never** commit without running `validate_before_push.sh` first
- **Never** run the import script in a context where `index.html` could be regenerated

---

## Protected files — never delete or overwrite wholesale

```
index.html                     (1500+ lines — app logic, UI, Intelligence tab, Analytics panel)
reports/central-coast.md       (418-line SA2 Intelligence Report)
```

If these files seem wrong, check git history first:
```bash
git log --oneline -- index.html
git log --oneline -- reports/central-coast.md
```

---

## What broke on 2026-05-27

1. `ba428e4` — Agent added GoatCounter snippet by **rewriting all of `index.html`** using an old
   1107-line version as a base, silently deleting:
   - Intelligence Report tab (all CSS + JS + `renderIntelligence()`)
   - Analytics popup panel (all CSS + HTML + JS)
   - `LOCKED_LGA_CODE` URL param handling (LGA filter hide, default SA2, map zoom)
   - `reports/central-coast.md` (deleted, no warning)
2. `cc849d7` — Restored `index.html` but missed `reports/central-coast.md`
3. `31d6d1b` — Restored `reports/central-coast.md`

**Root cause:** No validation gate. Agent used `write` on `index.html` instead of `edit`.

---

## Intelligence Report

The LLM-generated report lives at `reports/central-coast.md`.
It is served to the browser at runtime via `fetch('reports/central-coast.md')`.

To regenerate it with fresh data, run a separate, explicit task — it is **not** part of the
monthly data refresh script. Treat it as a separate deliverable.

Current report: **May 2026**, covers 30 SA2 areas, 418 lines.
