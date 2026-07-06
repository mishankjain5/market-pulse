"""
Exploratory Data Analysis
Interrogates the star schema to answer the brief's four questions:
  1. Who performed best/worst?
  2. Which stock is riskiest (most volatile)?
  3. Do any stocks move together (correlation)?
  4. Any unusual activity (volume spikes)?
Prints stats + saves charts to outputs/figures/.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # render to files, no display window needed
import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
FACT = BASE / "outputs" / "model" / "fact_daily_prices.csv"
FIG_DIR = BASE / "outputs" / "figures"


def main() -> None:
    df = pd.read_csv(FACT, parse_dates=["Date"])
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    tickers = sorted(df["Ticker"].unique())

    # ---------- Q1: performance (currency-proof: growth of 100) ----------
    final_growth = (
        df.sort_values("Date").groupby("Ticker")["GrowthOf100"].last().sort_values(ascending=False)
    )
    print("Q1. Growth of 100 over 2 years (rank):")
    print(final_growth.round(1).to_string(), "\n")

    fig, ax = plt.subplots(figsize=(10, 5))
    for t in tickers:
        sub = df[df["Ticker"] == t]
        ax.plot(sub["Date"], sub["GrowthOf100"], label=t, linewidth=1.2)
    ax.axhline(100, color="gray", linestyle="--", linewidth=0.8)
    ax.set_title("Growth of 100 invested, by ticker")
    ax.set_ylabel("Value of 100 invested at start")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "1_growth_of_100.png", dpi=120)

    # ---------- Q2: risk (average 30-day volatility) ----------
    avg_vol = df.groupby("Ticker")["Volatility30"].mean().sort_values(ascending=False)
    print("Q2. Average 30-day volatility (rank, higher = riskier):")
    print(avg_vol.round(2).to_string(), "\n")

    fig, ax = plt.subplots(figsize=(10, 5))
    for t in tickers:
        sub = df[df["Ticker"] == t]
        ax.plot(sub["Date"], sub["Volatility30"], label=t, linewidth=1.2)
    ax.set_title("30-day rolling volatility (std dev of daily returns)")
    ax.set_ylabel("Volatility (%)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "2_volatility.png", dpi=120)

    # ---------- Q3: correlation of daily returns ----------
    returns_wide = df.pivot(index="Date", columns="Ticker", values="DailyReturnPct")
    corr = returns_wide.corr()
    print("Q3. Correlation of daily returns:")
    print(corr.round(2).to_string(), "\n")

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(corr, cmap="RdYlGn", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns, rotation=45)
    ax.set_yticks(range(len(corr)), corr.columns)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9)
    ax.set_title("Daily return correlation")
    fig.colorbar(im, shrink=0.8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "3_correlation.png", dpi=120)

    # ---------- Q4: unusual activity (volume spikes) ----------
    spikes = df.groupby("Ticker")["VolumeSpike"].sum().sort_values(ascending=False)
    print("Q4. Number of volume-spike days (volume > 2x 30-day avg):")
    print(spikes.to_string(), "\n")

    biggest_moves = df.loc[
        df.groupby("Ticker")["DailyReturnPct"].apply(lambda s: s.abs().idxmax()).values,
        ["Ticker", "Date", "DailyReturnPct", "VolumeSpike"],
    ]
    print("Biggest single-day move per ticker (did volume spike that day?):")
    print(biggest_moves.to_string(index=False))

    print(f"\nCharts saved -> {FIG_DIR}")


if __name__ == "__main__":
    main()
