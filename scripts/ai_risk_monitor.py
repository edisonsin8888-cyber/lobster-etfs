import pandas as pd

from gold_utils import score_status, confidence

SCORE_FILE = "reports/06_score_and_monitor/gold_diversification_score.csv"
WEIGHT_FILE = "reports/05_weight_sensitivity/gld_weight_sensitivity.csv"
RISK_BUDGET_FILE = "reports/05_weight_sensitivity/gld_risk_budget_sensitivity.csv"
DELTA_FILE = "reports/02_regime_analysis/regime_portfolio_delta.csv"

MONITOR_OUT = "reports/06_score_and_monitor/ai_risk_monitor_report.txt"
MEMO_OUT = "reports/weekly_reports/gold_weekly_memo.txt"


def metric(df, name, col="Value"):
    return df.loc[df["Metric"] == name, col].iloc[0]


def at_weight(df, weight):
    return df.loc[df["GLD Weight"].round(2) == weight].iloc[0]


def strategic_range_from_risk(stress_ret, rb10, rb15, rb25):
    if stress_ret > 0 and rb10 <= 0.15 and rb15 <= 0.25 and rb25 >= 0.35:
        return "5%–15%"
    if stress_ret > 0 and rb10 <= 0.15:
        return "5%–10%"
    return "0%–5%"


def marginal_efficiency(weight_df, risk_df):
    merged = weight_df.merge(
        risk_df[["GLD Weight", "GLD Risk Contribution"]],
        on="GLD Weight",
        how="left",
    )

    rows = []
    for i in range(1, len(merged)):
        prev, curr = merged.iloc[i - 1], merged.iloc[i]

        ret_change = curr["Total Return"] - prev["Total Return"]
        vol_change = curr["Annualized Volatility"] - prev["Annualized Volatility"]
        dd_change = curr["Max Drawdown"] - prev["Max Drawdown"]
        rc_change = curr["GLD Risk Contribution"] - prev["GLD Risk Contribution"]

        score = (
            ret_change * 120
            - max(vol_change, 0) * 100
            + dd_change * 80
            - rc_change * 35
        )

        rows.append({
            "Range": f'{prev["GLD Weight"]:.0%} to {curr["GLD Weight"]:.0%}',
            "Return Change": ret_change,
            "Volatility Change": vol_change,
            "Drawdown Change": dd_change,
            "Risk Contribution Change": rc_change,
            "Efficiency Score": score,
        })

    return pd.DataFrame(rows)


score_df = pd.read_csv(SCORE_FILE)
weight_df = pd.read_csv(WEIGHT_FILE)
risk_df = pd.read_csv(RISK_BUDGET_FILE)
delta_df = pd.read_csv(DELTA_FILE)

final_score = metric(score_df, "Final Gold Diversification Score", "Score")
status = score_status(final_score)

corr = metric(score_df, "Average GLD-Equity Rolling Correlation")
vol_ratio = metric(score_df, "GLD / SPY Rolling Volatility Ratio")
stress_gap = metric(score_df, "GLD Stress Return Minus SPY Stress Return")
gld_rc = metric(score_df, "GLD % Risk Contribution")

stress = delta_df.loc[delta_df["Regime"] == "Stress Days"].iloc[0]
normal = delta_df.loc[delta_df["Regime"] == "Normal Days"].iloc[0]
strong = delta_df.loc[delta_df["Regime"] == "Strong Days"].iloc[0]

rb10 = at_weight(risk_df, 0.10)
rb15 = at_weight(risk_df, 0.15)
rb25 = at_weight(risk_df, 0.25)

eff = marginal_efficiency(weight_df, risk_df)
best_step = eff.loc[eff["Efficiency Score"].idxmax(), "Range"]

recommended_range = strategic_range_from_risk(
    stress["Delta Total Return"],
    rb10["GLD Risk Contribution"],
    rb15["GLD Risk Contribution"],
    rb25["GLD Risk Contribution"],
)

allocation_score = 50
allocation_score += 15 if stress["Delta Total Return"] > 0 else 0
allocation_score -= 5 if normal["Delta Total Return"] < 0 else 0
allocation_score += 10 if rb10["GLD Risk Contribution"] <= 0.15 else 0
allocation_score += 10 if rb15["GLD Risk Contribution"] <= 0.25 else 0
allocation_score -= 10 if rb25["GLD Risk Contribution"] >= 0.35 else 0
allocation_score += 10 if final_score >= 60 else -10 if final_score < 50 else 0
allocation_score = max(0, min(100, allocation_score))

eff_display = eff.copy()
for col in ["Return Change", "Volatility Change", "Drawdown Change", "Risk Contribution Change"]:
    eff_display[col] = eff_display[col].map(lambda x: f"{x:.2%}")
eff_display["Efficiency Score"] = eff_display["Efficiency Score"].map(lambda x: f"{x:.2f}")

monitor = f"""AI Portfolio Risk Monitor v4.4

Gold Diversification Score: {final_score:.2f}/100
Diversification Status: {status}

Key Signals:
- Average GLD-equity rolling correlation: {corr:.2f}
- GLD / SPY rolling volatility ratio: {vol_ratio:.2f}
- GLD stress return minus SPY stress return: {stress_gap:.2%}
- GLD portfolio risk contribution: {gld_rc:.2%}

Regime Impact:
- Stress Days: total return impact {stress["Delta Total Return"]:.2%}; drawdown impact {stress["Delta Max Drawdown"]:.2%}
- Normal Days: total return impact {normal["Delta Total Return"]:.2%}
- Strong Days: total return impact {strong["Delta Total Return"]:.2%}

Risk Budget:
- 10% GLD: {rb10["GLD Risk Contribution"]:.2%} risk contribution
- 15% GLD: {rb15["GLD Risk Contribution"]:.2%} risk contribution
- 25% GLD: {rb25["GLD Risk Contribution"]:.2%} risk contribution

Marginal Allocation Efficiency:
{eff_display.to_string(index=False)}

Dynamic Allocation Guidance:
- Allocation Guidance Score: {allocation_score:.2f}/100
- Recommendation Confidence: {confidence(allocation_score)}
- Best marginal step: {best_step}
- Recommended strategic range: {recommended_range}
- 5%–10%: efficient diversification zone
- 10%–15%: acceptable tactical range
- 20%–25%: aggressive range; GLD consumes disproportionate risk budget

Allocation Rationale:
The best marginal step identifies the single most efficient incremental GLD increase. The recommended strategic range reflects the broader allocation zone supported by stress-regime protection and risk-budget control.

Research Note:
This monitor is not a trading signal. It is a research tool for tracking GLD's diversification conditions within a multi-asset ETF portfolio.
"""

memo = f"""Weekly Gold Diversification Research Memo

1. Executive Summary
GLD currently shows {status.lower()} diversification value, with a Gold Diversification Score of {final_score:.2f}/100. The current evidence supports moderate GLD exposure rather than aggressive overweighting.

2. Portfolio Diagnosis
The main weakness is elevated GLD-equity correlation at {corr:.2f}, while GLD volatility remains high relative to SPY at {vol_ratio:.2f}x.

3. Regime Diagnostics
During stress days, adding GLD improved total return by {stress["Delta Total Return"]:.2%} and max drawdown by {stress["Delta Max Drawdown"]:.2%}. In normal and strong regimes, GLD reduced total return by {normal["Delta Total Return"]:.2%} and {strong["Delta Total Return"]:.2%}, respectively.

4. Risk Budget Diagnostics
At 10% GLD, risk contribution is {rb10["GLD Risk Contribution"]:.2%}. At 15%, it rises to {rb15["GLD Risk Contribution"]:.2%}. At 25%, it reaches {rb25["GLD Risk Contribution"]:.2%}, indicating disproportionate risk budget consumption at higher allocations.

5. Allocation Recommendation
Allocation Guidance Score: {allocation_score:.2f}/100.
Recommendation Confidence: {confidence(allocation_score)}.
Best marginal step: {best_step}.
Recommended strategic range: {recommended_range}.
The first GLD allocation step can be efficient, but the broader allocation range should remain moderate because risk contribution rises quickly at higher weights.

6. Bottom Line
GLD is best treated as a conditional hedge sleeve rather than an all-weather return enhancer in the current sample.

Research Note
This memo is generated from quantitative indicators and should be treated as a research aid, not as investment advice.
"""

for path, text in [(MONITOR_OUT, monitor), (MEMO_OUT, memo)]:
    with open(path, "w") as f:
        f.write(text)

print(monitor)
print(f"Saved monitor to {MONITOR_OUT}")
print(f"Saved memo to {MEMO_OUT}")