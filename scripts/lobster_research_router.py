from pathlib import Path
import pandas as pd

BASE = Path("reports/07_lobster_watchlist")

WATCHLIST_FILE = BASE / "etf_watchlist_snapshot.csv"
SCORE_FILE = BASE / "etf_score_table.csv"
OUT = BASE / "lobster_research_router.txt"


PRIORITY_SCORE = {
    "High": 25,
    "Medium": 15,
    "Low": 5,
}


ROLE_SCORE = {
    "Defensive Diversification Sleeve": 20,
    "Growth / Sector Sleeve": 15,
    "Rate-Sensitive Defensive Sleeve": 12,
    "Core Equity Sleeve": 8,
    "Weak Growth Sleeve": 5,
}


DEEP_DIVE_STATUS = {
    "GLD": "Completed Deep-Dive Module",
    "XLK": "Light Deep-Dive Candidate",
    "QQQ": "Future Growth Module Candidate",
    "TLT": "Future Defensive Module Candidate",
    "SPY": "Benchmark / Core Reference",
}


DEEP_DIVE_SCORE = {
    "Completed Deep-Dive Module": 12,
    "Light Deep-Dive Candidate": 10,
    "Future Growth Module Candidate": 7,
    "Future Defensive Module Candidate": 7,
    "Benchmark / Core Reference": 3,
}


def risk_adjustment(row):
    if row["Risk Flag"] == "High Risk":
        return 10
    if row["Risk Flag"] == "Defensive":
        return 4
    return 6


def momentum_adjustment(row):
    if row["Momentum Flag"] == "Weak":
        return 10
    if row["Momentum Flag"] == "Strong":
        return 6
    return 4


def deterioration_adjustment(row):
    score = 0

    if row["3M Return"] < 0:
        score += 8

    if row["3M Max Drawdown"] < -0.05:
        score += 6

    return score


def router_score(row):
    score_component = row["Final ETF Score"] * 0.35
    priority_component = PRIORITY_SCORE.get(row["Research Priority"], 0)
    role_component = ROLE_SCORE.get(row["Role Tag"], 0)
    risk_component = risk_adjustment(row)
    momentum_component = momentum_adjustment(row)
    deterioration_component = deterioration_adjustment(row)
    deep_dive_component = DEEP_DIVE_SCORE.get(row["Deep-Dive Status"], 0)

    return (
        score_component
        + priority_component
        + role_component
        + risk_component
        + momentum_component
        + deterioration_component
        + deep_dive_component
    )


def router_reason(row):
    reasons = []

    if row["Research Priority"] == "High":
        reasons.append("high watchlist priority")

    if row["Final ETF Score"] >= 70:
        reasons.append("strong ETF score")
    elif row["Final ETF Score"] < 55:
        reasons.append("weak ETF score requiring review")

    if row["Momentum Flag"] == "Weak":
        reasons.append("weak momentum")
    elif row["Momentum Flag"] == "Strong":
        reasons.append("strong momentum")

    if row["Risk Flag"] == "High Risk":
        reasons.append("elevated risk")

    if row["3M Return"] < 0:
        reasons.append("negative 3M return")

    if row["ETF"] == "GLD":
        reasons.append("completed Gold Engine available")

    if row["ETF"] == "XLK":
        reasons.append("growth-sleeve monitor candidate")

    return ", ".join(reasons) if reasons else "stable watchlist profile"


watch = pd.read_csv(WATCHLIST_FILE)
scores = pd.read_csv(SCORE_FILE)

merged = watch.merge(
    scores[["ETF", "Final ETF Score", "ETF Stance"]],
    on="ETF",
    how="left",
)

merged["Deep-Dive Status"] = merged["ETF"].map(DEEP_DIVE_STATUS).fillna("No Module")
merged["Router v2 Score"] = merged.apply(router_score, axis=1)
merged["Router Reason"] = merged.apply(router_reason, axis=1)

ranked = merged.sort_values("Router v2 Score", ascending=False).reset_index(drop=True)

top = ranked.iloc[0]

queue_lines = []

for i, row in ranked.iterrows():
    queue_lines.append(
        f"""{i + 1}. {row["ETF"]}
- Role Tag: {row["Role Tag"]}
- Research Priority: {row["Research Priority"]}
- ETF Stance: {row["ETF Stance"]}
- Final ETF Score: {row["Final ETF Score"]:.2f}/100
- Momentum Flag: {row["Momentum Flag"]}
- Risk Flag: {row["Risk Flag"]}
- 3M Return: {row["3M Return"]:.2%}
- 3M Max Drawdown: {row["3M Max Drawdown"]:.2%}
- Deep-Dive Status: {row["Deep-Dive Status"]}
- Router v2 Score: {row["Router v2 Score"]:.2f}
- Router Reason: {row["Router Reason"]}"""
    )

queue_text = "\n\n".join(queue_lines)

report = f"""Lobster Research Router v2

1. Next Deep-Dive Candidate
- ETF: {top["ETF"]}
- Role Tag: {top["Role Tag"]}
- Research Priority: {top["Research Priority"]}
- ETF Stance: {top["ETF Stance"]}
- Final ETF Score: {top["Final ETF Score"]:.2f}/100
- Deep-Dive Status: {top["Deep-Dive Status"]}
- Router v2 Score: {top["Router v2 Score"]:.2f}
- Router Reason: {top["Router Reason"]}

2. Ranked Research Queue
{queue_text}

3. Router v2 Interpretation
The Router v2 combines ETF attractiveness score, watchlist priority, portfolio role, risk condition, momentum condition, recent deterioration, and deep-dive module availability. This gives Lobster a stronger research routing layer than the original rule-based router.

4. Current System Link
If GLD remains the top-ranked ETF, the completed Gold Engine remains the active deep-dive module. If XLK ranks highly, it becomes the next growth-sleeve monitoring candidate for the v2 system.
"""

OUT.write_text(report)

print(report)
print(f"Saved to {OUT}")