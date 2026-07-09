import pandas as pd

TICKERS = ["SPY", "QQQ", "GLD", "TLT"]
OUT_DIR = "reports/02_regime_analysis"

PORTFOLIOS = {
    "Without GLD": {"SPY": 0.60, "QQQ": 0.20, "TLT": 0.20},
    "With GLD": {"SPY": 0.45, "QQQ": 0.20, "TLT": 0.20, "GLD": 0.15},
}

METRIC_COLS = [
    "Avg Daily Return",
    "Daily Volatility",
    "Total Return",
    "Max Drawdown",
]


def load_close(ticker):
    df = pd.read_csv(f"data/{ticker.lower()}.csv", header=[0, 1], index_col=0)
    close = pd.to_numeric(df[("Close", ticker)], errors="coerce").dropna()
    close.index = pd.to_datetime(close.index)
    return close


def calc_metrics(returns):
    nav = (1 + returns).cumprod()
    return pd.Series({
        "Avg Daily Return": returns.mean(),
        "Daily Volatility": returns.std(),
        "Total Return": nav.iloc[-1] - 1,
        "Max Drawdown": (nav / nav.cummax() - 1).min(),
    })


prices = pd.concat({ticker: load_close(ticker) for ticker in TICKERS}, axis=1)
returns = prices.pct_change().dropna()

stress_cut = returns["SPY"].quantile(0.10)
strong_cut = returns["SPY"].quantile(0.90)

returns["Regime"] = "Normal Days"
returns.loc[returns["SPY"] <= stress_cut, "Regime"] = "Stress Days"
returns.loc[returns["SPY"] >= strong_cut, "Regime"] = "Strong Days"

rows = []

for regime, group in returns.groupby("Regime"):
    for portfolio_name, weights in PORTFOLIOS.items():
        portfolio_returns = sum(group[ticker] * weight for ticker, weight in weights.items())

        row = calc_metrics(portfolio_returns)
        row["Regime"] = regime
        row["Portfolio"] = portfolio_name
        row["Number of Days"] = len(group)
        rows.append(row)

comparison = pd.DataFrame(rows)
comparison = comparison[
    ["Regime", "Portfolio", "Number of Days"] + METRIC_COLS
]

comparison.to_csv(f"{OUT_DIR}/regime_portfolio_comparison.csv", index=False)

delta_rows = []

for regime in ["Stress Days", "Normal Days", "Strong Days"]:
    subset = comparison[comparison["Regime"] == regime].set_index("Portfolio")
    delta = subset.loc["With GLD", METRIC_COLS] - subset.loc["Without GLD", METRIC_COLS]

    delta_rows.append({
        "Regime": regime,
        **{f"Delta {col}": delta[col] for col in METRIC_COLS},
    })

delta_df = pd.DataFrame(delta_rows)
delta_df.to_csv(f"{OUT_DIR}/regime_portfolio_delta.csv", index=False)

best_regime = delta_df.loc[delta_df["Delta Max Drawdown"].idxmax(), "Regime"]
worst_regime = delta_df.loc[delta_df["Delta Total Return"].idxmin(), "Regime"]

summary = f"""Regime Portfolio Delta Summary

Best regime for GLD based on drawdown improvement: {best_regime}
Weakest regime for GLD based on total return impact: {worst_regime}

Interpretation:
Adding GLD is most useful when it improves downside outcomes during stress conditions.
If GLD increases volatility or reduces returns in normal and strong regimes, its role should be treated as conditional rather than universally beneficial.
"""

with open(f"{OUT_DIR}/regime_portfolio_summary.txt", "w") as file:
    file.write(summary)

display = delta_df.copy()
for col in display.columns[1:]:
    display[col] = display[col].map(lambda x: f"{x:.2%}")

print("=== Regime Portfolio Delta Analysis ===")
print(display)
print()
print(summary)
print(f"Saved to {OUT_DIR}")