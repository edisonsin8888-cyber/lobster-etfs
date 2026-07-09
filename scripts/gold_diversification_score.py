import pandas as pd

REGIME_FILE = "reports/02_regime_analysis/regime_analysis.csv"
ROLLING_CORR_FILE = "reports/03_rolling_analysis/rolling_correlation.csv"
ROLLING_VOL_FILE = "reports/03_rolling_analysis/rolling_volatility.csv"
RISK_CONTRIBUTION_FILE = "reports/04_risk_contribution/risk_contribution_summary.csv"
OUTPUT_FILE = "reports/06_score_and_monitor/gold_diversification_score.csv"


def clamp(x, low=0, high=100):
    return max(low, min(high, x))


def score_correlation(avg_corr):
    return clamp(100 * (1 - avg_corr))


def score_volatility(gld_vol, spy_vol):
    ratio = gld_vol / spy_vol
    if ratio <= 1:
        return 100
    if ratio >= 2:
        return 30
    return clamp(100 - (ratio - 1) * 70)


def score_stress(gld_stress, spy_stress):
    return clamp(50 + (gld_stress - spy_stress) * 2000)


def score_risk_contribution(gld_rc):
    if gld_rc <= 0.25:
        return 90
    if gld_rc <= 0.35:
        return 70
    if gld_rc <= 0.45:
        return 50
    return 30


regime = pd.read_csv(REGIME_FILE, index_col=0)
rolling_corr = pd.read_csv(ROLLING_CORR_FILE, index_col=0).dropna()
rolling_vol = pd.read_csv(ROLLING_VOL_FILE, index_col=0).dropna()
risk_contribution = pd.read_csv(RISK_CONTRIBUTION_FILE)

latest_corr = rolling_corr.iloc[-1]
latest_vol = rolling_vol.iloc[-1]

avg_equity_corr = (latest_corr["GLD-SPY"] + latest_corr["GLD-QQQ"]) / 2
gld_vol = latest_vol["GLD"]
spy_vol = latest_vol["SPY"]

gld_stress = regime.loc["Stress Days", "GLD"]
spy_stress = regime.loc["Stress Days", "SPY"]

gld_rc_text = risk_contribution.loc[
    risk_contribution["ETF"] == "GLD", "% Risk Contribution"
].iloc[0]
gld_rc = float(gld_rc_text.replace("%", "")) / 100

scores = {
    "Correlation Score": score_correlation(avg_equity_corr),
    "Volatility Score": score_volatility(gld_vol, spy_vol),
    "Stress Performance Score": score_stress(gld_stress, spy_stress),
    "Risk Contribution Score": score_risk_contribution(gld_rc),
}

final_score = (
    scores["Correlation Score"] * 0.30
    + scores["Volatility Score"] * 0.25
    + scores["Stress Performance Score"] * 0.25
    + scores["Risk Contribution Score"] * 0.20
)

result = pd.DataFrame([
    {"Metric": "Average GLD-Equity Rolling Correlation", "Value": avg_equity_corr, "Score": scores["Correlation Score"]},
    {"Metric": "GLD / SPY Rolling Volatility Ratio", "Value": gld_vol / spy_vol, "Score": scores["Volatility Score"]},
    {"Metric": "GLD Stress Return Minus SPY Stress Return", "Value": gld_stress - spy_stress, "Score": scores["Stress Performance Score"]},
    {"Metric": "GLD % Risk Contribution", "Value": gld_rc, "Score": scores["Risk Contribution Score"]},
    {"Metric": "Final Gold Diversification Score", "Value": final_score, "Score": final_score},
])

result.to_csv(OUTPUT_FILE, index=False)

print("=== Gold Diversification Score ===")
print(result)
print()
print(f"Final Gold Diversification Score: {final_score:.2f}/100")
print(f"Saved to {OUTPUT_FILE}")