import pandas as pd

CORR_FILE = "reports/03_rolling_analysis/rolling_correlation.csv"
VOL_FILE = "reports/03_rolling_analysis/rolling_volatility.csv"
SCORE_FILE = "reports/06_score_and_monitor/gold_diversification_score.csv"
OUT = "reports/06_score_and_monitor/diversification_alert.txt"


def get_score(df, metric):
    return df.loc[df["Metric"] == metric, "Score"].iloc[0]


def signal(value, green, red, lower_is_better=True):
    if lower_is_better:
        if value <= green:
            return "Green"
        if value >= red:
            return "Red"
    else:
        if value >= green:
            return "Green"
        if value <= red:
            return "Red"
    return "Yellow"


def alert_level(signals):
    if "Red" in signals:
        return "Red"
    if "Yellow" in signals:
        return "Yellow"
    return "Green"


def main_driver(items):
    priority = {"Red": 2, "Yellow": 1, "Green": 0}
    return max(items, key=lambda x: priority[x["Signal"]])


corr = pd.read_csv(CORR_FILE, index_col=0).dropna()
vol = pd.read_csv(VOL_FILE, index_col=0).dropna()
score_df = pd.read_csv(SCORE_FILE)

latest_corr = corr.iloc[-1]
recent_corr = corr.iloc[-20:].mean()
latest_vol = vol.iloc[-1]

avg_corr = (latest_corr["GLD-SPY"] + latest_corr["GLD-QQQ"]) / 2
recent_avg_corr = (recent_corr["GLD-SPY"] + recent_corr["GLD-QQQ"]) / 2
corr_change = avg_corr - recent_avg_corr

vol_ratio = latest_vol["GLD"] / latest_vol["SPY"]
final_score = get_score(score_df, "Final Gold Diversification Score")

diagnostics = [
    {
        "Name": "GLD-equity rolling correlation",
        "Value": avg_corr,
        "Signal": signal(avg_corr, green=0.30, red=0.60),
        "Reason": "High correlation weakens GLD's diversification role."
    },
    {
        "Name": "GLD/SPY rolling volatility ratio",
        "Value": vol_ratio,
        "Signal": signal(vol_ratio, green=1.20, red=1.70),
        "Reason": "High relative volatility makes GLD less efficient as a hedge sleeve."
    },
    {
        "Name": "Gold Diversification Score",
        "Value": final_score,
        "Signal": signal(final_score, green=70, red=45, lower_is_better=False),
        "Reason": "A low score indicates weak overall diversification quality."
    },
]

level = alert_level([d["Signal"] for d in diagnostics])
driver = main_driver(diagnostics)

if corr_change < -0.05:
    trend = "Improving"
    trend_reason = "GLD-equity correlation has declined versus its recent 20-day average."
elif corr_change > 0.05:
    trend = "Deteriorating"
    trend_reason = "GLD-equity correlation has increased versus its recent 20-day average."
else:
    trend = "Stable"
    trend_reason = "GLD-equity correlation is close to its recent 20-day average."

report = f"""Enhanced Rolling Diversification Alert v1

Alert Level: {level}
Diversification Trend: {trend}

Traffic-Light Diagnostics:
- Correlation signal: {diagnostics[0]["Signal"]} | value: {avg_corr:.2f}
- Volatility signal: {diagnostics[1]["Signal"]} | value: {vol_ratio:.2f}
- Score signal: {diagnostics[2]["Signal"]} | value: {final_score:.2f}/100

Trend Diagnostics:
- Change in GLD-equity correlation versus recent 20-day average: {corr_change:.2f}
- Trend reason: {trend_reason}

Main Alert Driver:
{driver["Name"]} is the main alert driver.
Reason: {driver["Reason"]}

Interpretation:
The current alert level is {level.lower()}. GLD's diversification condition is {trend.lower()}, but the main risk factor should still be monitored closely.

Research Action Note:
Focus on whether GLD-equity correlation remains elevated and whether GLD volatility continues to stay high relative to SPY. These are the key factors that can weaken GLD's role as a diversification sleeve.
"""

with open(OUT, "w") as f:
    f.write(report)

print(report)
print(f"Saved to {OUT}")