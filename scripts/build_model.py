"""
Data Preparation & Modeling (Silver -> Gold)
Turns cleaned/prices_clean.csv into a star schema:
  Fact_DailyPrices  - one row per (Ticker, Date), with derived KPI columns
  Dim_Company       - one row per ticker (context that doesn't change daily)
  Dim_Date          - one row per calendar date (enables time intelligence)
Output: outputs/model/*.csv  ->  consumed by Excel (Hour 7) and Power BI (Hour 8).
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
IN_PATH = BASE / "cleaned" / "prices_clean.csv"
OUT_DIR = BASE / "outputs" / "model"

COMPANIES = [
    # Ticker,        Company,               Sector,                  Country, Currency
    ("AAPL",        "Apple Inc.",           "Technology",            "USA",   "USD"),
    ("MSFT",        "Microsoft Corp.",      "Technology",            "USA",   "USD"),
    ("TSLA",        "Tesla Inc.",           "Consumer Discretionary","USA",   "USD"),
    ("JPM",         "JPMorgan Chase & Co.", "Financials",            "USA",   "USD"),
    ("RELIANCE.NS", "Reliance Industries",  "Energy & Conglomerate", "India", "INR"),
]


def build_fact(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["Ticker", "Date"]).copy()
    g = df.groupby("Ticker")

    # KPI 1: daily return % — the currency-proof measure
    df["DailyReturnPct"] = g["Close"].pct_change() * 100

    # KPI 2: growth of 100 (cumulative return, base 100 at period start)
    df["GrowthOf100"] = g["Close"].transform(lambda s: s / s.iloc[0] * 100)

    # KPI 3: 50-day moving average (trend line)
    df["MA50"] = g["Close"].transform(lambda s: s.rolling(50).mean())

    # KPI 4: 30-day rolling volatility (std dev of daily returns)
    df["Volatility30"] = g["DailyReturnPct"].transform(lambda s: s.rolling(30).std())

    # KPI 5: volume spike — day's volume > 2x its 30-day average
    avg_vol_30 = g["Volume"].transform(lambda s: s.rolling(30).mean())
    df["VolumeSpike"] = (df["Volume"] > 2 * avg_vol_30).astype(int)

    return df


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    # Continuous calendar (not just trading days) — the BI-standard approach:
    # weekends/holidays exist in the calendar even if no fact rows point to them.
    dates = pd.date_range(df["Date"].min(), df["Date"].max(), freq="D")
    dim = pd.DataFrame({"Date": dates})
    dim["Year"] = dim["Date"].dt.year
    dim["Quarter"] = "Q" + dim["Date"].dt.quarter.astype(str)
    dim["MonthNum"] = dim["Date"].dt.month          # for sorting Jan < Feb < ...
    dim["Month"] = dim["Date"].dt.strftime("%b")    # for display
    dim["YearMonth"] = dim["Date"].dt.strftime("%Y-%m")
    dim["Weekday"] = dim["Date"].dt.day_name()
    return dim


def main() -> None:
    df = pd.read_csv(IN_PATH, parse_dates=["Date"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fact = build_fact(df)
    dim_company = pd.DataFrame(
        COMPANIES, columns=["Ticker", "Company", "Sector", "Country", "Currency"]
    )
    dim_date = build_dim_date(df)

    fact.to_csv(OUT_DIR / "fact_daily_prices.csv", index=False)
    dim_company.to_csv(OUT_DIR / "dim_company.csv", index=False)
    dim_date.to_csv(OUT_DIR / "dim_date.csv", index=False)

    print(f"Fact_DailyPrices: {len(fact)} rows x {len(fact.columns)} cols")
    print(f"Dim_Company:      {len(dim_company)} rows")
    print(f"Dim_Date:         {len(dim_date)} rows (continuous calendar)")
    print(f"Saved -> {OUT_DIR}")


if __name__ == "__main__":
    main()
