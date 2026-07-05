# Cleaning Log — prices_messy.csv → prices_clean.csv

**Script:** `scripts/clean_data.py` · **Date:** 2026-07-05 · **Rows:** 2,533 in → 2,503 out

| # | Issue found | Evidence | Treatment | Rationale |
|---|-------------|----------|-----------|-----------|
| 1 | Dates stored as text | `Date` dtype = object | Converted with `pd.to_datetime` | CSVs have no date type; lossless fix |
| 2 | Ticker inconsistencies (15 variants) | mixed case, stray spaces | Normalized: strip + uppercase | One rule beats hand-editing; asserted result ∈ 5 valid tickers |
| 3 | 30 duplicate rows | 28 exact + 2 near-duplicates | Dropped on business key (Ticker, Date), keeping the copy with fewest nulls | Exact-match dedupe undercounts when a twin was later corrupted |
| 4 | 3 impossible prices (~100× median) | max Close ≈ 40,858 for AAPL | Nulled (rule: Close > 5× ticker median), then filled | Fat-finger decimal shift; treat as missing rather than trust a guess |
| 5 | 5 negative volumes | min Volume < 0 | Nulled, then filled | Physically impossible value |
| 6 | 42 missing Close values | `.isna()` | Forward-fill per ticker (bfill for leading gaps) | Yesterday's close is best estimate; per-ticker groupby prevents cross-stock leakage |
| 7 | 30 missing Volume values | `.isna()` (incl. nulled negatives) | Per-ticker median fill; restored int64 type | No day-to-day trend to borrow; median robust to spikes |

**Judgment calls a reviewer might challenge:**
- ffill assumes a missing close means "no change" — acceptable for daily bars, would be wrong for sparse data.
- The 5× median outlier rule is dataset-specific; a genuinely 5×-ing stock (rare, but possible) would be wrongly flagged. Hour 4 validation adds a second safety net.
