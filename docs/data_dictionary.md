# Data Dictionary - Market Pulse

## Source

| Property | Value |
|----------|-------|
| Provider | Yahoo Finance via `yfinance` Python library |
| Method | API download (`scripts/collect_data.py`) |
| Period | Rolling last 2 years, daily bars |
| Prices | **Split/dividend adjusted** (`auto_adjust=True`) |
| Collected | 2026-07-05 |

## Files in raw/

| File | Description |
|------|-------------|
| `prices_raw.csv` | Untouched API output. Never hand-edited. |
| `prices_messy.csv` | Training copy with injected defects (`scripts/make_messy.py`) - used for the cleaning exercise. |

## Columns (prices_raw.csv)

| Column | Type | Description | Valid range |
|--------|------|-------------|-------------|
| Date | date (YYYY-MM-DD) | Trading day | 2024-07-03 to present; weekdays only |
| Open | float | First traded price of the day | > 0 |
| High | float | Highest price of the day | ≥ Low, > 0 |
| Low | float | Lowest price of the day | ≤ High, > 0 |
| Close | float | Last traded price (adjusted) | > 0 |
| Volume | int | Shares traded | ≥ 0 |
| Ticker | text | Stock symbol | One of: AAPL, MSFT, TSLA, JPM, RELIANCE.NS |

## Known Caveats

- **Currency mix:** RELIANCE.NS is priced in INR; others in USD. Cross-stock comparisons must use % returns, never absolute prices.
- **Calendar mismatch:** RELIANCE.NS has ~499 rows vs 501 for US tickers - India (NSE) and US (NYSE/NASDAQ) observe different market holidays. A missing date is not automatically missing data.
- **Adjusted prices:** historical prices won't match "what the price actually was that day" if a split/dividend occurred since - this is intentional and correct for trend analysis.
