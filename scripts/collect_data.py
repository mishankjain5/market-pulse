"""
Data Collection (Bronze layer)
Downloads 2 years of daily prices for the watchlist via the yfinance API
and saves them UNTOUCHED to raw/. Raw data is never edited - if collection
logic changes, we re-collect; we don't hand-edit.
"""
from pathlib import Path

import pandas as pd
import yfinance as yf

TICKERS = ["AAPL", "MSFT", "TSLA", "JPM", "RELIANCE.NS"]
PERIOD = "2y"  # last 2 years of daily bars

# Resolve paths relative to this file so it works from any working directory
RAW_DIR = Path(__file__).resolve().parents[1] / "raw"


def collect() -> None:
    RAW_DIR.mkdir(exist_ok=True)
    frames = []

    for ticker in TICKERS:
        print(f"Downloading {ticker} ...")
        df = yf.download(
            ticker,
            period=PERIOD,
            interval="1d",
            auto_adjust=True,  # adjusts prices for splits/dividends
            progress=False,
        )
        if df.empty:
            print(f"  WARNING: no data returned for {ticker} - check ticker symbol")
            continue

        df = df.reset_index()
        # Newer yfinance versions return MultiIndex columns even for one ticker
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        df["Ticker"] = ticker
        frames.append(df)
        print(f"  {len(df)} rows, {df['Date'].min().date()} -> {df['Date'].max().date()}")

    if not frames:
        raise SystemExit(
            "ERROR: no data collected for any ticker. "
            "Check your internet connection and ticker symbols, then rerun."
        )

    all_prices = pd.concat(frames, ignore_index=True)
    out_path = RAW_DIR / "prices_raw.csv"
    all_prices.to_csv(out_path, index=False)
    print(f"\nSaved {len(all_prices)} total rows -> {out_path}")


if __name__ == "__main__":
    collect()
