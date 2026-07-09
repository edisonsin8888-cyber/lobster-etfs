import pandas as pd
from pathlib import Path

from gold_utils import score_status, allocation_stance

BASE = "reports/06_score_and_monitor"
SCORE_FILE = f"{BASE}/gold_diversification_score.csv"
ALERT_FILE = f"{BASE}/diversification_alert.txt"
HISTORY_FILE = f"{BASE}/allocation_history.csv"
OUT = f"{BASE}/gold_signal_dashboard.txt"


def read_line(path, prefix):
    for line in Path(path).read_text().splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return "N/A"


def get_final_score(df):
    return df.loc[df["Metric"] == "Final Gold Diversification Score", "Score"].iloc[0]


def verdict(score_state, alert, stance, strategic_range):
    if alert == "Red" and stance == "Defensive":
        return f"GLD retains some diversification value, but allocation conditions are weak. Current supported range: {strategic_range}."
    if score_state in ["Moderate", "Strong"] and stance != "Defensive":
        return "GLD shows constructive diversification value and can support a moderate allocation role."
    return "GLD remains a conditional hedge and should be monitored through correlation, volatility, and stress-period performance."


def allocation_drivers(row, alert, stance):
    drivers = []

    if alert == "Red":
        drivers.append("elevated alert level")
    if stance == "Defensive":
        drivers.append("low allocation guidance score")
    if row["GLD/SPY Volatility Ratio"] > 1.7:
        drivers.append("high GLD/SPY volatility ratio")
    if row["Stress Return Gap"] <= 0:
        drivers.append("weak stress-period return support")

    if not drivers:
        return "No major negative allocation driver is currently dominant."

    return "The defensive allocation view is mainly driven by " + ", ".join(drivers) + "."


score_df = pd.read_csv(SCORE_FILE)
history = pd.read_csv(HISTORY_FILE)

latest = history.iloc[-1]
previous = history.iloc[-2]

final_score = get_final_score(score_df)
score_state = score_status(final_score)

alert = read_line(ALERT_FILE, "Alert Level:")
trend = read_line(ALERT_FILE, "Diversification Trend:")

alloc_score = latest["Allocation Guidance Score"]
stance = allocation_stance(alloc_score)
strategic_range = latest["Recommended Strategic Range"]

score_change = latest["Gold Diversification Score"] - previous["Gold Diversification Score"]
alloc_change = latest["Allocation Guidance Score"] - previous["Allocation Guidance Score"]

dashboard = f"""Gold ETF Research Dashboard v2.2

1. Research Verdict
{verdict(score_state, alert, stance, strategic_range)}

2. Current Monitor Snapshot
- Gold Diversification Score: {final_score:.2f}/100
- Score Status: {score_state}
- Alert Level: {alert}
- Diversification Trend: {trend}

3. Current Allocation View
- Allocation Guidance Score: {alloc_score:.2f}/100
- Allocation Stance: {stance}
- Recommendation Confidence: {latest["Recommendation Confidence"]}
- Recommended Strategic Range: {strategic_range}
- Best Marginal Step: {latest["Best Marginal Step"]}

4. Allocation Driver Summary
{allocation_drivers(latest, alert, stance)}

5. Latest Historical Allocation Snapshot
- Historical Date: {latest["Date"]}
- Historical Gold Diversification Score: {latest["Gold Diversification Score"]:.2f}/100
- Historical Status: {latest["Status"]}
- Historical Alert Level: {latest["Alert Level"]}
- Historical Average GLD-equity Correlation: {latest["Average GLD-Equity Correlation"]:.2f}
- Historical GLD/SPY Volatility Ratio: {latest["GLD/SPY Volatility Ratio"]:.2f}
- Historical Stress Return Gap: {latest["Stress Return Gap"]:.2%}

6. Historical Trend Diagnostics
- One-month historical score change: {score_change:.2f}
- One-month allocation guidance score change: {alloc_change:.2f}
- Previous strategic range: {previous["Recommended Strategic Range"]}
- Current strategic range: {strategic_range}
- Previous alert level: {previous["Alert Level"]}
- Current alert level: {latest["Alert Level"]}

7. Research Use
Run scripts/run_all.py to refresh the full pipeline. Use this dashboard as the top-level project view, then read the monitor, alert, weekly memo, and allocation history files for deeper diagnostics.
"""

Path(OUT).write_text(dashboard)
print(dashboard)
print(f"Saved to {OUT}")