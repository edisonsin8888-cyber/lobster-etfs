import pandas as pd
from pathlib import Path

BASE = Path("reports/07_lobster_watchlist")

WATCHLIST_FILE = BASE / "etf_watchlist_snapshot.csv"
OUT_TABLE = BASE / "etf_score_table.csv"
OUT_SUMMARY = BASE / "etf_score_summary.txt"


ROLE_SCORE = {
    "Core Equity Sleeve": 60,
    "Growth / Sector Sleeve": 65,
    "Weak Growth Sleeve": 40,
    "Defensive Diversification Sleeve": 70,
    "Rate-Sensitive Defensive Sleeve": 55,
}


def clamp(x, low=0, high=100):
    return max(low, min(high, x))


def momentum_score(row):
    return clamp(50 + row["1M Return"] * 150 + row["3M Return"] * 300)


def risk_score(row):
    return clamp(100 - row["Annualized Volatility"] * 200)


def drawdown_score(row):
    return clamp(100 + row["3M Max Drawdown"] * 500)


def role_score(row):
    return ROLE_SCORE.get(row["Role Tag"], 50)


def final_score(row):
    return (
        row["Momentum Score"] * 0.35
        + row["Risk Score"] * 0.25
        + row["Drawdown Score"] * 0.20
        + row["Role Score"] * 0.20
    )


def etf_stance(score):
    if score >= 70:
        return "Constructive"
    if score >= 55:
        return "Neutral"
    return "Defensive"


watch = pd.read_csv(WATCHLIST_FILE)

watch["Momentum Score"] = watch.apply(momentum_score, axis=1)
watch["Risk Score"] = watch.apply(risk_score, axis=1)
watch["Drawdown Score"] = watch.apply(drawdown_score, axis=1)
watch["Role Score"] = watch.apply(role_score, axis=1)
watch["Final ETF Score"] = watch.apply(final_score, axis=1)
watch["ETF Stance"] = watch["Final ETF Score"].apply(etf_stance)

score_table = watch[
    [
        "ETF",
        "Role Tag",
        "Research Priority",
        "Momentum Flag",
        "Risk Flag",
        "1M Return",
        "3M Return",
        "Annualized Volatility",
        "3M Max Drawdown",
        "Momentum Score",
        "Risk Score",
        "Drawdown Score",
        "Role Score",
        "Final ETF Score",
        "ETF Stance",
    ]
].sort_values("Final ETF Score", ascending=False)

score_table.to_csv(OUT_TABLE, index=False)

top = score_table.iloc[0]
bottom = score_table.iloc[-1]
gld = score_table.loc[score_table["ETF"] == "GLD"].iloc[0]
xlk = score_table.loc[score_table["ETF"] == "XLK"].iloc[0]

summary = f"""ETF Score Engine v1

1. Top ETF by Final Score
- ETF: {top["ETF"]}
- Final ETF Score: {top["Final ETF Score"]:.2f}/100
- ETF Stance: {top["ETF Stance"]}
- Role Tag: {top["Role Tag"]}

2. Weakest ETF by Final Score
- ETF: {bottom["ETF"]}
- Final ETF Score: {bottom["Final ETF Score"]:.2f}/100
- ETF Stance: {bottom["ETF Stance"]}
- Role Tag: {bottom["Role Tag"]}

3. GLD Score View
- Final ETF Score: {gld["Final ETF Score"]:.2f}/100
- ETF Stance: {gld["ETF Stance"]}
- Momentum Score: {gld["Momentum Score"]:.2f}
- Risk Score: {gld["Risk Score"]:.2f}
- Drawdown Score: {gld["Drawdown Score"]:.2f}
- Role Score: {gld["Role Score"]:.2f}

4. XLK Score View
- Final ETF Score: {xlk["Final ETF Score"]:.2f}/100
- ETF Stance: {xlk["ETF Stance"]}
- Momentum Score: {xlk["Momentum Score"]:.2f}
- Risk Score: {xlk["Risk Score"]:.2f}
- Drawdown Score: {xlk["Drawdown Score"]:.2f}
- Role Score: {xlk["Role Score"]:.2f}

5. Interpretation
The ETF Score Engine converts watchlist signals into a comparable ETF attractiveness score. It combines momentum, risk, drawdown control, and portfolio role. This gives Lobster a unified scoring layer before the router selects deep-dive research priorities.
"""

OUT_SUMMARY.write_text(summary)

print("=== ETF Score Table ===")
print(score_table)
print()
print(summary)
print(f"Saved to {OUT_TABLE}")
print(f"Saved to {OUT_SUMMARY}")