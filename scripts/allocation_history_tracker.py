import pandas as pd
import numpy as np

from gold_utils import (
    score_status,
    alert_level,
    allocation_score,
    confidence,
    strategic_range,
    best_step,
    direction,
    range_transition,
    alert_transition,
)

TICKERS = ["SPY", "QQQ", "GLD", "TLT"]
OUT_CSV = "reports/06_score_and_monitor/allocation_history.csv"
OUT_TXT = "reports/06_score_and_monitor/allocation_history_summary.txt"


def load_close(ticker):
    df = pd.read_csv(f"data/{ticker.lower()}.csv", header=[0, 1], index_col=0)
    close = pd.to_numeric(df[("Close", ticker)], errors="coerce").dropna()
    close.index = pd.to_datetime(close.index)
    return close


prices = pd.concat({t: load_close(t) for t in TICKERS}, axis=1)
returns = prices.pct_change().dropna()

rows = []

for date in returns.resample("ME").last().index:
    sample = returns.loc[:date].tail(126)

    if len(sample) < 60:
        continue

    avg_corr = (sample["GLD"].corr(sample["SPY"]) + sample["GLD"].corr(sample["QQQ"])) / 2

    gld_vol = sample["GLD"].std() * np.sqrt(252)
    spy_vol = sample["SPY"].std() * np.sqrt(252)
    vol_ratio = gld_vol / spy_vol

    stress_cut = sample["SPY"].quantile(0.10)
    stress = sample[sample["SPY"] <= stress_cut]
    stress_gap = stress["GLD"].mean() - stress["SPY"].mean()

    corr_score = max(0, 100 * (1 - avg_corr))
    vol_score = max(0, min(100, 100 - max(vol_ratio - 1, 0) * 70))
    stress_score = max(0, min(100, 50 + stress_gap * 2000))

    gold_score = corr_score * 0.35 + vol_score * 0.30 + stress_score * 0.35
    alloc_score = allocation_score(gold_score, stress_gap, avg_corr, vol_ratio)

    rows.append({
        "Date": date.date(),
        "Gold Diversification Score": gold_score,
        "Status": score_status(gold_score),
        "Alert Level": alert_level(avg_corr, vol_ratio, gold_score),
        "Allocation Guidance Score": alloc_score,
        "Recommendation Confidence": confidence(alloc_score),
        "Best Marginal Step": best_step(gold_score, stress_gap, vol_ratio),
        "Recommended Strategic Range": strategic_range(gold_score, avg_corr, vol_ratio, stress_gap),
        "Average GLD-Equity Correlation": avg_corr,
        "GLD/SPY Volatility Ratio": vol_ratio,
        "Stress Return Gap": stress_gap,
    })

history = pd.DataFrame(rows)

latest = history.iloc[-1]
previous = history.iloc[-2]
last3 = history.tail(3)

score_change = latest["Gold Diversification Score"] - previous["Gold Diversification Score"]
alloc_change = latest["Allocation Guidance Score"] - previous["Allocation Guidance Score"]
corr_change = latest["Average GLD-Equity Correlation"] - previous["Average GLD-Equity Correlation"]
vol_change = latest["GLD/SPY Volatility Ratio"] - previous["GLD/SPY Volatility Ratio"]

history["Score Change"] = history["Gold Diversification Score"].diff()
history["Allocation Score Change"] = history["Allocation Guidance Score"].diff()

history.to_csv(OUT_CSV, index=False)

range_counts = history["Recommended Strategic Range"].value_counts()
alert_counts = history["Alert Level"].value_counts()

three_month_score_change = last3["Gold Diversification Score"].iloc[-1] - last3["Gold Diversification Score"].iloc[0]
three_month_alloc_change = last3["Allocation Guidance Score"].iloc[-1] - last3["Allocation Guidance Score"].iloc[0]

summary = f"""Historical Allocation Tracker Summary v3

Latest Date: {latest["Date"]}
Latest Gold Diversification Score: {latest["Gold Diversification Score"]:.2f}/100
Latest Status: {latest["Status"]}
Latest Alert Level: {latest["Alert Level"]}
Latest Allocation Guidance Score: {latest["Allocation Guidance Score"]:.2f}/100
Latest Recommendation Confidence: {latest["Recommendation Confidence"]}
Latest Best Marginal Step: {latest["Best Marginal Step"]}
Latest Recommended Strategic Range: {latest["Recommended Strategic Range"]}

Latest Month Change:
- Score change: {score_change:.2f}
- Allocation guidance score change: {alloc_change:.2f}
- Average GLD-equity correlation change: {corr_change:.2f}
- GLD/SPY volatility ratio change: {vol_change:.2f}

Transition Diagnostics:
- Strategic range transition: {previous["Recommended Strategic Range"]} → {latest["Recommended Strategic Range"]} ({range_transition(previous["Recommended Strategic Range"], latest["Recommended Strategic Range"])})
- Alert transition: {previous["Alert Level"]} → {latest["Alert Level"]} ({alert_transition(previous["Alert Level"], latest["Alert Level"])})

Three-Month Trend:
- Score trend: {direction(three_month_score_change)}
- Allocation stance trend: {direction(three_month_alloc_change)}
- Three-month score change: {three_month_score_change:.2f}
- Three-month allocation score change: {three_month_alloc_change:.2f}

Strategic Range Frequency:
{range_counts.to_string()}

Alert Level Frequency:
{alert_counts.to_string()}

Research Takeaway:
GLD's allocation role remains regime-dependent. The latest reading should be interpreted together with the recent score trend, alert transition, and whether the recommended allocation range is tightening or loosening over time.
"""

with open(OUT_TXT, "w") as f:
    f.write(summary)

print("=== Historical Allocation Tracker v3 ===")
print(history.tail())
print()
print(summary)
print(f"Saved to {OUT_CSV}")
print(f"Saved to {OUT_TXT}")