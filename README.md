# Market Pulse 📈

An end-to-end data analyst project: stock market data pipeline from raw collection to Power BI dashboard.

**Author:** Mishank ([@mishankjain5](https://github.com/mishankjain5))

## The Business Problem

An investment club tracks 5 stocks and needs a monthly refreshed dashboard covering price trends, volatility, best/worst performers, and volume patterns. See [docs/BRIEF.md](docs/BRIEF.md).

## Pipeline (mirrors cloud medallion architecture)

```
raw/  (Bronze — untouched source data)
  └─► cleaned/  (Silver — validated, cleaned)
        └─► outputs/  (Gold — modeled star schema, reports)
```

## Project Structure

| Folder | Purpose |
|--------|---------|
| `raw/` | Raw data exactly as collected — never edited by hand |
| `cleaned/` | Cleaned, validated datasets |
| `outputs/` | Star-schema tables, Excel report, Power BI file |
| `scripts/` | Python: collect → clean → validate → model |
| `docs/` | Business brief, data dictionary, cleaning log |

## Lifecycle Stages Covered

Business question → Collection → Cleaning → Quality/Validation → Modeling (star schema) → EDA → Excel reporting → Power BI dashboard → Cloud architecture design → Maintenance & refresh
