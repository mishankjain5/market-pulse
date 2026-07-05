"""
Data Cleaning (Bronze -> Silver)
Reads raw/prices_messy.csv, applies documented fixes, writes cleaned/prices_clean.csv.
Every decision here is logged in docs/cleaning_log.md.
Golden rule: fixes live in code (repeatable), never in hand-edited files.
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
IN_PATH = BASE / "raw" / "prices_messy.csv"
OUT_PATH = BASE / "cleaned" / "prices_clean.csv"

VALID_TICKERS = {"AAPL", "MSFT", "TSLA", "JPM", "RELIANCE.NS"}
PRICE_COLS = ["Open", "High", "Low", "Close"]


def clean() -> None:
    df = pd.read_csv(IN_PATH)
    n_start = len(df)
    print(f"Loaded {n_start} rows")

    # ------------------------------------------------- 1. Fix types
    # CSVs store everything as text; dates must be converted every time.
    df["Date"] = pd.to_datetime(df["Date"])

    # ------------------------------------------------- 2. Normalize text
    # One rule kills all 15 ticker variants: strip whitespace, uppercase...
    df["Ticker"] = df["Ticker"].str.strip().str.upper()
    # ...but uppercase breaks 'RELIANCE.NS'? No - it was already upper. Verify:
    unknown = set(df["Ticker"].unique()) - VALID_TICKERS
    assert not unknown, f"Unexpected tickers after normalization: {unknown}"

    # ------------------------------------------------- 3. Flag impossible values -> null
    # Negative volume cannot exist; null it so the fill step treats it as missing.
    n_neg = (df["Volume"] < 0).sum()
    df.loc[df["Volume"] < 0, "Volume"] = pd.NA

    # Fat-finger prices: > 5x that ticker's median close is impossible for our
    # watchlist (no stock moved 5x in 2 years). Null them for filling.
    median_close = df.groupby("Ticker")["Close"].transform("median")
    is_outlier = df["Close"] > 5 * median_close
    n_out = is_outlier.sum()
    df.loc[is_outlier, "Close"] = pd.NA

    # ------------------------------------------------- 4. Deduplicate on business key
    # True key: one row per (Ticker, Date). Keep the copy with fewest nulls,
    # because some duplicates are 'better' (their twin got corrupted).
    df["_nulls"] = df[PRICE_COLS + ["Volume"]].isna().sum(axis=1)
    df = (
        df.sort_values(["Ticker", "Date", "_nulls"])
        .drop_duplicates(subset=["Ticker", "Date"], keep="first")
        .drop(columns="_nulls")
    )
    n_dupes = n_start - len(df)

    # ------------------------------------------------- 5. Fill missing values
    # Prices: forward-fill WITHIN each ticker (yesterday's price is the best
    # estimate). groupby prevents AAPL prices leaking into MSFT.
    n_close_na = df["Close"].isna().sum()
    df = df.sort_values(["Ticker", "Date"])
    df[PRICE_COLS] = df.groupby("Ticker")[PRICE_COLS].ffill()
    # bfill catches a gap on the very first day (nothing before it to copy)
    df[PRICE_COLS] = df.groupby("Ticker")[PRICE_COLS].bfill()

    # Volume: no trend to borrow -> per-ticker median (robust to spikes).
    n_vol_na = df["Volume"].isna().sum()
    df["Volume"] = df["Volume"].fillna(df.groupby("Ticker")["Volume"].transform("median"))
    df["Volume"] = df["Volume"].astype("int64")  # restore proper integer type

    # ------------------------------------------------- 6. Save Silver layer
    OUT_PATH.parent.mkdir(exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print(f"Removed {n_dupes} duplicate rows (business key: Ticker+Date)")
    print(f"Nulled {n_neg} negative volumes, {n_out} outlier prices")
    print(f"Filled {n_close_na} missing closes (ffill), {n_vol_na} missing volumes (median)")
    print(f"Remaining nulls: {df.isna().sum().sum()}")
    print(f"Saved {len(df)} rows -> {OUT_PATH}")


if __name__ == "__main__":
    clean()
