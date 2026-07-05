# Business Brief — Market Pulse

**Date:** 2026-07-05 · **Analyst:** Mishank · **Stakeholder:** Investment club (5 members)

## The Ask (in the stakeholder's words)

> "We each track stocks separately in random spreadsheets. We want one dashboard, refreshed monthly, that shows how our 5 watchlist stocks are doing — trends, risk, and anything unusual — so our monthly meeting takes 15 minutes instead of an hour."

## Scope

- **Tickers:** AAPL, MSFT, TSLA, JPM, RELIANCE.NS (US tech, US finance, India — deliberate variety)
- **Period:** last 2 years of daily prices
- **Refresh:** monthly

## KPIs (agreed with stakeholder)

| # | KPI | Definition | Why they care |
|---|-----|------------|---------------|
| 1 | Monthly return % | (month close − prior month close) / prior close | Core performance |
| 2 | Cumulative return | Growth of ₹/$ 100 invested at period start | Long-term view |
| 3 | 50-day moving average | Rolling mean of close price | Trend direction |
| 4 | Volatility | 30-day rolling std dev of daily returns | Risk comparison |
| 5 | Volume spike flag | Daily volume > 2× its 30-day average | "Anything unusual" |

## Success Criteria

Dashboard answers in <15 min: Who won/lost this month? Which stock is riskiest? Any unusual activity? Is each stock above or below trend?

## Out of Scope

Price prediction, buy/sell recommendations, intraday data.

---
*Lesson: every deliverable traces back to a stakeholder question. If a chart doesn't answer one of the questions above, it doesn't belong on the dashboard.*
