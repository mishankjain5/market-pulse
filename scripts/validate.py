"""
Hour 4 — Data Quality Gate (the inspector)
Runs quality checks against a dataset and reports pass/fail per check.
NEVER fixes anything — fixing is clean_data.py's job.
Exits with code 1 if any check fails, so a pipeline can refuse to continue.

Usage:
    python scripts/validate.py                      # checks cleaned/prices_clean.csv
    python scripts/validate.py raw/prices_messy.csv # checks any other file
"""
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = BASE / "cleaned" / "prices_clean.csv"

VALID_TICKERS = {"AAPL", "MSFT", "TSLA", "JPM", "RELIANCE.NS"}
ROWS_PER_TICKER = (480, 520)   # ~2y of trading days, tolerant of holiday calendars
MAX_STALENESS_DAYS = 7         # data older than this is stale (timeliness)


def run_checks(df: pd.DataFrame) -> list[tuple[str, str, bool, str]]:
    """Returns list of (dimension, check name, passed, detail)."""
    results = []

    def check(dimension: str, name: str, passed: bool, detail: str = "") -> None:
        results.append((dimension, name, bool(passed), detail))

    # --- Validity: dates must parse
    dates = pd.to_datetime(df["Date"], errors="coerce")
    bad_dates = dates.isna().sum()
    check("Validity", "All dates parseable", bad_dates == 0, f"{bad_dates} unparseable")

    # --- Validity: tickers from the approved set
    unknown = set(df["Ticker"].unique()) - VALID_TICKERS
    check("Validity", "Tickers in valid set", not unknown, f"unknown: {unknown or '—'}")

    # --- Completeness: no nulls anywhere
    nulls = df.isna().sum().sum()
    check("Completeness", "No null values", nulls == 0, f"{nulls} nulls")

    # --- Completeness: plausible row count per ticker
    counts = df["Ticker"].value_counts()
    lo, hi = ROWS_PER_TICKER
    bad_counts = counts[(counts < lo) | (counts > hi)]
    check("Completeness", f"Rows per ticker in [{lo}, {hi}]", bad_counts.empty,
          f"out of range: {bad_counts.to_dict() or '—'}")

    # --- Uniqueness: one row per (Ticker, Date)
    dupes = df.duplicated(subset=["Ticker", "Date"]).sum()
    check("Uniqueness", "Business key (Ticker, Date) unique", dupes == 0, f"{dupes} dupes")

    # --- Validity: prices positive
    bad_prices = (df[["Open", "High", "Low", "Close"]] <= 0).sum().sum()
    check("Validity", "All prices > 0", bad_prices == 0, f"{bad_prices} non-positive")

    # --- Validity: volume non-negative
    neg_vol = (df["Volume"] < 0).sum()
    check("Validity", "Volume >= 0", neg_vol == 0, f"{neg_vol} negative")

    # --- Consistency: High >= Low on every row
    incons = (df["High"] < df["Low"]).sum()
    check("Consistency", "High >= Low", incons == 0, f"{incons} violations")

    # --- Accuracy: no price wildly beyond its ticker median (fat-finger net)
    med = df.groupby("Ticker")["Close"].transform("median")
    wild = (df["Close"] > 5 * med).sum()
    check("Accuracy", "No close > 5x ticker median", wild == 0, f"{wild} suspects")

    # --- Timeliness: freshest date within threshold
    age_days = (pd.Timestamp.today().normalize() - dates.max()).days
    check("Timeliness", f"Latest date within {MAX_STALENESS_DAYS} days",
          age_days <= MAX_STALENESS_DAYS, f"newest data is {age_days} days old")

    return results


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TARGET
    if not target.is_absolute():
        target = BASE / target
    df = pd.read_csv(target)

    results = run_checks(df)
    failed = [r for r in results if not r[2]]

    print(f"\nQUALITY REPORT — {target.name} ({len(df)} rows)")
    print("-" * 72)
    for dimension, name, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {dimension:<13} {name:<38} {detail}")
    print("-" * 72)
    print(f"{len(results) - len(failed)}/{len(results)} checks passed")

    if failed:
        sys.exit(1)  # non-zero exit = pipeline must stop


if __name__ == "__main__":
    main()
