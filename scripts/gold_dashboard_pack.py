import pandas as pd
from pathlib import Path

BASE = Path("reports/06_score_and_monitor")
WEEKLY = Path("reports/weekly_reports")

SCORE_FILE = BASE / "gold_diversification_score.csv"
ALERT_FILE = BASE / "diversification_alert.txt"
HISTORY_FILE = BASE / "allocation_history.csv"
OUT = BASE / "gold_dashboard_pack.md"


def read_line_value(path, prefix):
    text = Path(path).read_text()
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return "N/A"


def score_status(score):
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Moderate"
    if score >= 40:
        return "Mixed"
    return "Weak"


def allocation_stance(score):
    if score >= 75:
        return "Constructive"
    if score >= 55:
        return "Neutral"
    return "Defensive"


def executive_verdict(score_status_value, alert, stance, strategic_range):
    if alert == "Red" and stance == "Defensive":
        return (
            f"GLD still offers some diversification value, but current allocation conditions remain weak. "
            f"The system supports only a limited strategic range of {strategic_range}."
        )
    if score_status_value in ["Moderate", "Strong"] and stance != "Defensive":
        return (
            "GLD currently shows constructive diversification value and can support a moderate allocation role."
        )
    return (
        "GLD's diversification role remains conditional and should be monitored through correlation, volatility, and stress-period performance."
    )


def allocation_driver_text(alert, allocation_score, vol_ratio, stress_gap):
    drivers = []

    if alert == "Red":
        drivers.append("elevated alert level")
    if allocation_score < 55:
        drivers.append(f"weak allocation guidance score ({allocation_score:.2f}/100)")
    if vol_ratio >= 1.7:
        drivers.append(f"high GLD/SPY volatility ratio ({vol_ratio:.2f})")
    if stress_gap <= 0:
        drivers.append(f"weak stress-period return support ({stress_gap:.2%})")

    if not drivers:
        return "The current allocation view is broadly supported by stable diversification signals and acceptable risk-budget conditions."

    return "The current allocation stance is constrained mainly by " + ", ".join(drivers) + "."


def historical_verdict(score_change, alloc_change, prev_range, curr_range, prev_alert, curr_alert):
    parts = []

    if score_change > 2:
        parts.append("historical diversification score improved meaningfully")
    elif score_change > 0:
        parts.append("historical diversification score improved slightly")
    elif score_change < -2:
        parts.append("historical diversification score deteriorated meaningfully")
    elif score_change < 0:
        parts.append("historical diversification score softened slightly")
    else:
        parts.append("historical diversification score was broadly unchanged")

    if alloc_change > 5:
        parts.append("allocation conditions strengthened")
    elif alloc_change < -5:
        parts.append("allocation conditions weakened")
    else:
        parts.append("allocation conditions were broadly stable")

    if prev_range != curr_range:
        parts.append(f"supported allocation range shifted from {prev_range} to {curr_range}")
    else:
        parts.append(f"supported allocation range remained at {curr_range}")

    if prev_alert != curr_alert:
        parts.append(f"alert level moved from {prev_alert} to {curr_alert}")
    else:
        parts.append(f"alert level stayed at {curr_alert}")

    return "Historically, " + "; ".join(parts) + "."


score_df = pd.read_csv(SCORE_FILE)
history = pd.read_csv(HISTORY_FILE)

final_score = score_df.loc[
    score_df["Metric"] == "Final Gold Diversification Score", "Score"
].iloc[0]

corr = score_df.loc[
    score_df["Metric"] == "Average GLD-Equity Rolling Correlation", "Value"
].iloc[0]

vol_ratio = score_df.loc[
    score_df["Metric"] == "GLD / SPY Rolling Volatility Ratio", "Value"
].iloc[0]

stress_gap = score_df.loc[
    score_df["Metric"] == "GLD Stress Return Minus SPY Stress Return", "Value"
].iloc[0]

latest = history.iloc[-1]
previous = history.iloc[-2]

alert_level = read_line_value(ALERT_FILE, "Alert Level:")
trend = read_line_value(ALERT_FILE, "Diversification Trend:")

score_status_value = score_status(final_score)
allocation_score = latest["Allocation Guidance Score"]
allocation_stance_value = allocation_stance(allocation_score)
strategic_range = latest["Recommended Strategic Range"]

score_change = latest["Gold Diversification Score"] - previous["Gold Diversification Score"]
allocation_change = latest["Allocation Guidance Score"] - previous["Allocation Guidance Score"]

verdict = executive_verdict(
    score_status_value,
    alert_level,
    allocation_stance_value,
    strategic_range,
)

allocation_driver = allocation_driver_text(
    alert_level,
    allocation_score,
    latest["GLD/SPY Volatility Ratio"],
    latest["Stress Return Gap"],
)

history_view = historical_verdict(
    score_change,
    allocation_change,
    previous["Recommended Strategic Range"],
    latest["Recommended Strategic Range"],
    previous["Alert Level"],
    latest["Alert Level"],
)

pack = f"""# Gold ETF Research Pack

## 1. Executive Summary
{verdict}

## 2. Current Diversification Condition
- Gold Diversification Score: {final_score:.2f}/100
- Score Status: {score_status_value}
- Alert Level: {alert_level}
- Diversification Trend: {trend}

## 3. Current Allocation Decision
- Allocation Guidance Score: {allocation_score:.2f}/100
- Allocation Stance: {allocation_stance_value}
- Recommendation Confidence: {latest["Recommendation Confidence"]}
- Recommended Strategic Range: {strategic_range}
- Best Marginal Step: {latest["Best Marginal Step"]}

## 4. Why the Current Allocation Stance Looks This Way
{allocation_driver}

## 5. Historical Allocation Evidence
- Latest historical date: {latest["Date"]}
- Historical gold diversification score: {latest["Gold Diversification Score"]:.2f}/100
- Historical status: {latest["Status"]}
- Historical alert level: {latest["Alert Level"]}
- Historical average GLD-equity correlation: {latest["Average GLD-Equity Correlation"]:.2f}
- Historical GLD/SPY volatility ratio: {latest["GLD/SPY Volatility Ratio"]:.2f}
- Historical stress return gap: {latest["Stress Return Gap"]:.2%}

## 6. Historical Trend Verdict
{history_view}

## 7. Charts

### Gold Diversification Score History
![Gold Diversification Score History](gold_div_score_history.png)

This chart tracks the historical diversification score. It helps show whether GLD's diversification condition is strengthening or weakening over time.

### Allocation Guidance Score History
![Allocation Guidance Score History](allocation_guidance_history.png)

This chart tracks the allocation guidance score over time. The latest defensive stance is consistent with a compressed allocation score and limited supported range.

### GLD Risk Budget Curve
![GLD Risk Budget Curve](gld_risk_budget_curve.png)

This curve shows how GLD's share of total portfolio risk rises as its portfolio weight increases. A steep rise at higher weights suggests that GLD begins to consume disproportionate risk budget.

## 8. Method Note
This project treats GLD as a potential diversification sleeve inside a multi-asset ETF portfolio and evaluates it through four linked lenses: rolling correlation, relative volatility, stress-period performance, and allocation efficiency under different portfolio weights.

## 9. File Map
For deeper diagnostics, read:
- `reports/06_score_and_monitor/ai_risk_monitor_report.txt`
- `reports/06_score_and_monitor/diversification_alert.txt`
- `reports/weekly_reports/gold_weekly_memo.txt`
- `reports/06_score_and_monitor/allocation_history_summary.txt`
- `reports/06_score_and_monitor/gold_signal_dashboard.txt`
"""

OUT.write_text(pack)
print("Gold dashboard pack generated.")
print(f"Saved to {OUT}")