# Maintenance & Refresh Plan - Market Pulse

## Monthly refresh procedure (~5 minutes)

1. `python scripts/run_pipeline.py` - collects fresh data, cleans, validates, remodels, re-analyzes. Stops automatically at the first failure.
2. Open `Market_Pulse_Report.xlsx` → Data → Refresh All.
3. Open `Market_Pulse.pbix` → Home → Refresh.
4. Skim `docs/insights.md` - update any insight the new month contradicts.
5. Commit: `git commit -am "Monthly refresh <YYYY-MM>"`.

In a cloud deployment, steps 1–3 would be a scheduled Data Factory pipeline plus
Power BI Service scheduled refresh; step 4 is the part that stays human.

## Known refresh behaviors (not bugs)

- **History can restate.** Prices are dividend/split adjusted, so a refresh can
  change historical values slightly - even flip near-tied rankings (observed:
  MSFT's biggest single-day move changed after one refresh). Raw snapshots in
  `raw/` allow diffing what changed.
- **The 2-year window rolls.** Oldest days drop off with each refresh; long-run
  stats drift accordingly.

## What breaks, and how it fails (designed failure modes)

| Change | What happens | Fix |
|--------|--------------|-----|
| Yahoo API down / no internet | Collect exits 1, pipeline stops, old data intact | Rerun later |
| Ticker renamed/delisted | Collect warns; validation fails row-count check | Update ticker in collect + validate + dim_company |
| Column renamed upstream | Clean or model crashes loudly (never silently) | Update column references |
| Bad values in fresh data | Quality gate fails with named check, reports don't update | Inspect, extend cleaning rules if legitimate |
| Data goes stale (>7 days) | Timeliness check fails | Investigate source |

## Adding a new stock to the watchlist

1. `scripts/collect_data.py` → add to `TICKERS`
2. `scripts/validate.py` → add to `VALID_TICKERS`
3. `scripts/build_model.py` → add row to `COMPANIES`
4. Rerun pipeline; refresh reports. Slicers pick up the new ticker automatically.

*Known improvement:* the ticker list lives in three places - a future refactor
would move it to one shared config file (single source of truth).
