"""
Creates a deliberately messy copy of the raw data for cleaning practice.
Injects the 5 most common real-world data defects:
  1. Duplicate rows        (system exported twice)
  2. Missing values        (feed dropped some closes)
  3. Impossible outliers   (fat-finger data entry)
  4. Inconsistent text     (ticker typed in mixed case / extra spaces)
  5. Invalid values        (negative volume - impossible in reality)

Seeded so everyone gets the same mess (reproducibility matters).
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "raw"
SEED = 42


def make_messy() -> None:
    rng = np.random.default_rng(SEED)
    df = pd.read_csv(RAW_DIR / "prices_raw.csv")
    n = len(df)

    # 1. Duplicates: re-append 30 random rows
    dupes = df.sample(30, random_state=SEED)
    df = pd.concat([df, dupes], ignore_index=True)

    # 2. Missing values: blank out 40 Close and 25 Volume entries
    df.loc[rng.choice(n, 40, replace=False), "Close"] = np.nan
    df.loc[rng.choice(n, 25, replace=False), "Volume"] = np.nan

    # 3. Outliers: 3 fat-finger prices (decimal shifted by 100x)
    outlier_idx = rng.choice(n, 3, replace=False)
    df.loc[outlier_idx, "Close"] = df.loc[outlier_idx, "Close"] * 100

    # 4. Inconsistent text: mixed case + stray whitespace in Ticker
    lower_idx = rng.choice(n, 50, replace=False)
    df.loc[lower_idx, "Ticker"] = df.loc[lower_idx, "Ticker"].str.lower()
    space_idx = rng.choice(n, 30, replace=False)
    df.loc[space_idx, "Ticker"] = " " + df.loc[space_idx, "Ticker"] + " "

    # 5. Invalid values: 5 negative volumes
    neg_idx = rng.choice(n, 5, replace=False)
    df.loc[neg_idx, "Volume"] = -df.loc[neg_idx, "Volume"].abs()

    # Shuffle so problems aren't conveniently grouped
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

    out = RAW_DIR / "prices_messy.csv"
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} rows (incl. 30 duplicates) -> {out}")
    print("Defects injected: 30 dupes, 40+25 nulls, 3 outliers, 80 text issues, 5 negative volumes")


if __name__ == "__main__":
    make_messy()
