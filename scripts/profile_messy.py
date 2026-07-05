import pandas as pd

df = pd.read_csv("raw/prices_messy.csv")

print("--- STRUCTURE ---")
print(df.info())

print("\n--- STATISTICS ---")
print(df.describe())

print("\n--- DUPLICATES ---")
print("Exact duplicate rows:", df.duplicated().sum())

print("\n--- MISSING VALUES ---")
print(df.isna().sum())

print("\n--- CATEGORY CHECK ---")
print(df["Ticker"].unique())