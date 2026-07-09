from pathlib import Path
import pandas as pd

BASE_GOLD = Path("reports/06_score_and_monitor")
BASE_LOBSTER = Path("reports/07_lobster_watchlist")
BASE_GROWTH = Path("reports/08_growth_sleeve")

OUT = BASE_LOBSTER / "lobster_weekly_memo.txt"

WATCHLIST_FILE = BASE_LOBSTER / "etf_watchlist_snapshot.csv"
SCORE_FILE = BASE_LOBSTER / "etf_score_table.csv"
ROUTER_FILE = BASE_LOBSTER / "lobster_research_router.txt"
GOLD_DASHBOARD = BASE_GOLD / "gold_signal_dashboard.txt"
XLK_SUMMARY = BASE_GROWTH / "xlk_vs_spy_summary.csv"


def read_line(path, prefix):
    if not path.exists():
        return "N/A"

    for line in path.read_text().splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()

    return "N/A"


watch = pd.read_csv(WATCHLIST_FILE)
scores = pd.read_csv(SCORE_FILE)
xlk = pd.read_csv(XLK_SUMMARY).iloc[0]

top_score = scores.iloc[0]
second_score = scores.iloc[1]
bottom_score = scores.iloc[-1]

best_3m = watch.loc[watch["3M Return"].idxmax()]
weakest_3m = watch.loc[watch["3M Return"].idxmin()]
highest_vol = watch.loc[watch["Annualized Volatility"].idxmax()]

gld = scores.loc[scores["ETF"] == "GLD"].iloc[0]
xlk_score = scores.loc[scores["ETF"] == "XLK"].iloc[0]

router_etf = read_line(ROUTER_FILE, "- ETF:")
router_role = read_line(ROUTER_FILE, "- Role Tag:")
router_priority = read_line(ROUTER_FILE, "- Research Priority:")
router_stance = read_line(ROUTER_FILE, "- ETF Stance:")
router_final_score = read_line(ROUTER_FILE, "- Final ETF Score:")
router_v2_score = read_line(ROUTER_FILE, "- Router v2 Score:")
router_reason = read_line(ROUTER_FILE, "- Router Reason:")

gold_score = read_line(GOLD_DASHBOARD, "- Gold Diversification Score:")
gold_status = read_line(GOLD_DASHBOARD, "- Score Status:")
gold_alert = read_line(GOLD_DASHBOARD, "- Alert Level:")
gold_stance = read_line(GOLD_DASHBOARD, "- Allocation Stance:")
gold_range = read_line(GOLD_DASHBOARD, "- Recommended Strategic Range:")

score_ranking_text = "\n".join(
    [
        f"{i + 1}. {row['ETF']} — {row['Final ETF Score']:.2f}/100, {row['ETF Stance']}, {row['Role Tag']}"
        for i, row in scores.iterrows()
    ]
)

memo = f"""Lobster Weekly Research Memo v2

1. Weekly Research Focus
The current Router v2 deep-dive candidate is {router_etf}.

- Role Tag: {router_role}
- Research Priority: {router_priority}
- ETF Stance: {router_stance}
- Final ETF Score: {router_final_score}
- Router v2 Score: {router_v2_score}
- Router Reason: {router_reason}

2. ETF Market Snapshot
- Best 3M performer: {best_3m["ETF"]} ({best_3m["3M Return"]:.2%})
- Weakest 3M performer: {weakest_3m["ETF"]} ({weakest_3m["3M Return"]:.2%})
- Highest-volatility ETF: {highest_vol["ETF"]} ({highest_vol["Annualized Volatility"]:.2%})

3. ETF Score Ranking
{score_ranking_text}

4. Defensive Sleeve Update: GLD
- GLD ETF Score: {gld["Final ETF Score"]:.2f}/100
- GLD ETF Stance: {gld["ETF Stance"]}
- Gold Diversification Score: {gold_score}
- Score Status: {gold_status}
- Alert Level: {gold_alert}
- Allocation Stance: {gold_stance}
- Recommended Strategic Range: {gold_range}

Interpretation:
GLD remains the completed defensive diversification deep-dive module. However, the Gold Engine remains cautious, so the system does not support aggressive GLD allocation under current conditions.

5. Growth Sleeve Update: XLK
- XLK ETF Score: {xlk_score["Final ETF Score"]:.2f}/100
- XLK ETF Stance: {xlk_score["ETF Stance"]}
- XLK 3M Return: {xlk["XLK 3M Return"]:.2%}
- SPY 3M Return: {xlk["SPY 3M Return"]:.2%}
- XLK 3M Excess Return: {xlk["XLK 3M Excess Return"]:.2%}
- XLK Volatility Premium: {xlk["XLK Volatility Premium"]:.2%}
- Growth Sleeve Score: {xlk["Growth Sleeve Score"]:.2f}/100
- Growth Sleeve Risk Flag: {xlk["Growth Sleeve Risk Flag"]}
- Tactical Growth Stance: {xlk["Tactical Growth Stance"]}

Interpretation:
XLK shows strong growth leadership relative to SPY, but the growth signal comes with elevated volatility. It should be monitored as a constructive but high-risk growth / sector sleeve.

6. Router v2 Decision
The Router v2 combines ETF score, watchlist priority, portfolio role, momentum condition, risk condition, recent deterioration, and deep-dive module availability.

Current decision:
- Active deep-dive candidate: {router_etf}
- Main reason: {router_reason}

7. Weekly Research Conclusion
Lobster v2 currently shows a two-sleeve research structure:

- GLD is the defensive diversification sleeve with a completed deep-dive engine.
- XLK is the growth / sector sleeve with strong recent performance but high volatility risk.

The portfolio research stance is therefore mixed: GLD remains useful for defensive monitoring, while XLK provides growth leadership but requires risk control.

8. Next Action
Maintain GLD as the active completed defensive module. Continue monitoring XLK as the first growth-sleeve prototype. The next possible system extension should be either a TLT defensive-rate module or a QQQ growth comparison module.
"""

OUT.write_text(memo)

print(memo)
print(f"Saved to {OUT}")