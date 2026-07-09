import pandas as pd
import numpy as np

TICKERS = ["SPY", "QQQ", "GLD", "TLT"]
OUT = "reports/05_weight_sensitivity/gld_risk_budget_sensitivity.csv"


def load_close(ticker):
    df = pd.read_csv(f"data/{ticker.lower()}.csv", header=[0, 1], index_col=0)
    close = pd.to_numeric(df[("Close", ticker)], errors="coerce").dropna()
    close.index = pd.to_datetime(close.index)
    return close


def risk_contribution(cov, weights):
    w = np.array([weights[t] for t in TICKERS])
    port_vol = np.sqrt(w.T @ cov @ w)
    mctr = cov @ w / port_vol
    rc = w * mctr
    return rc / port_vol, port_vol


prices = pd.concat({t: load_close(t) for t in TICKERS}, axis=1)
returns = prices.pct_change().dropna()
cov = returns.cov().values * 252

rows = []

for gld_w in [0, 0.05, 0.10, 0.15, 0.20, 0.25]:
    weights = {
        "SPY": 0.60 - gld_w,
        "QQQ": 0.20,
        "GLD": gld_w,
        "TLT": 0.20,
    }

    pct_rc, port_vol = risk_contribution(cov, weights)

    row = {
        "GLD Weight": gld_w,
        "Portfolio Volatility": port_vol,
    }

    for ticker, rc in zip(TICKERS, pct_rc):
        row[f"{ticker} Risk Contribution"] = rc

    rows.append(row)

result = pd.DataFrame(rows)
result.to_csv(OUT, index=False)

display = result.copy()
for col in display.columns:
    display[col] = display[col].map(lambda x: f"{x:.2%}")

print("=== GLD Risk Budget Sensitivity ===")
print(display)
print(f"Saved to {OUT}")