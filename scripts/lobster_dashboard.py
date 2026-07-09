from pathlib import Path
import pandas as pd

BASE_GOLD = Path("reports/06_score_and_monitor")
BASE_LOBSTER = Path("reports/07_lobster_watchlist")
BASE_GROWTH = Path("reports/08_growth_sleeve")

OUT = BASE_LOBSTER / "lobster_dashboard.txt"

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
bottom_score = scores.iloc[-1]

best_3m = watch.loc[watch["3M Return"].idxmax()]
weakest_3m = watch.loc[watch["3M Return"].idxmin()]
highest_vol = watch.loc[watch["Annualized Volatility"].idxmax()]

gld_row = scores.loc[scores["ETF"] == "GLD"].iloc[0]
xlk_score_row = scores.loc[scores["ETF"] == "XLK"].iloc[0]

router_etf = read_line(ROUTER_FILE, "- ETF:")
router_reason = read_line(ROUTER_FILE, "- Router Reason:")
router_score = read_line(ROUTER_FILE, "- Router v2 Score:")

gold_score = read_line(GOLD_DASHBOARD, "- Gold Diversification Score:")
gold_status = read_line(GOLD_DASHBOARD, "- Score Status:")
gold_alert = read_line(GOLD_DASHBOARD, "- Alert Level:")
gold_stance = read_line(GOLD_DASHBOARD, "- Allocation Stance:")
gold_range = read_line(GOLD_DASHBOARD, "- Recommended Strategic Range:")

dashboard = f"""Lobster ETF Research Dashboard v2

1. System View
Lobster v2 combines ETF watchlist scanning, ETF scoring, research routing, GLD defensive deep-dive analysis, and XLK growth-sleeve monitoring.

2. ETF Watchlist Snapshot
- Best 3M performer: {best_3m["ETF"]} ({best_3m["3M Return"]:.2%})
- Weakest 3M performer: {weakest_3m["ETF"]} ({weakest_3m["3M Return"]:.2%})
- Highest-volatility ETF: {highest_vol["ETF"]} ({highest_vol["Annualized Volatility"]:.2%})

3. ETF Score Ranking
- Top ETF by Final Score: {top_score["ETF"]} ({top_score["Final ETF Score"]:.2f}/100, {top_score["ETF Stance"]})
- Weakest ETF by Final Score: {bottom_score["ETF"]} ({bottom_score["Final ETF Score"]:.2f}/100, {bottom_score["ETF Stance"]})

4. Defensive Sleeve Update: GLD
- ETF Score: {gld_row["Final ETF Score"]:.2f}/100
- ETF Stance: {gld_row["ETF Stance"]}
- Gold Diversification Score: {gold_score}
- Score Status: {gold_status}
- Alert Level: {gold_alert}
- Allocation Stance: {gold_stance}
- Recommended Strategic Range: {gold_range}

5. Growth Sleeve Update: XLK
- ETF Score: {xlk_score_row["Final ETF Score"]:.2f}/100
- ETF Stance: {xlk_score_row["ETF Stance"]}
- XLK 3M Return: {xlk["XLK 3M Return"]:.2%}
- SPY 3M Return: {xlk["SPY 3M Return"]:.2%}
- XLK 3M Excess Return: {xlk["XLK 3M Excess Return"]:.2%}
- XLK Volatility Premium: {xlk["XLK Volatility Premium"]:.2%}
- Growth Sleeve Score: {xlk["Growth Sleeve Score"]:.2f}/100
- Growth Sleeve Risk Flag: {xlk["Growth Sleeve Risk Flag"]}
- Tactical Growth Stance: {xlk["Tactical Growth Stance"]}

6. Router v2 Decision
- Next Deep-Dive Candidate: {router_etf}
- Router v2 Score: {router_score}
- Router Reason: {router_reason}

7. Portfolio Research Stance
The system currently has two active research sleeves. GLD remains the defensive diversification sleeve, but the Gold Engine supports only a cautious allocation range. XLK shows strong growth leadership relative to SPY, but this comes with elevated volatility and drawdown risk.

8. Next Action
Maintain GLD as the completed defensive deep-dive module. Continue monitoring XLK as the first growth / sector sleeve prototype. Future work can expand the same framework to TLT or QQQ.
"""

OUT.write_text(dashboard)

print(dashboard)
print(f"Saved to {OUT}")