import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

TICKERS = ["SPY", "QQQ", "GLD", "TLT"]

# 你可以先固定一个基础组合权重
WEIGHTS = {
    "SPY": 0.35,
    "QQQ": 0.25,
    "GLD": 0.20,
    "TLT": 0.20
}


def load_close_price(ticker):
    file_path = f"data/{ticker.lower()}.csv"
    df = pd.read_csv(file_path, header=[0, 1], index_col=0)

    prices = df[("Close", ticker)].dropna()
    prices = pd.to_numeric(prices, errors="coerce").dropna()
    prices.index = pd.to_datetime(prices.index)
    prices.name = ticker

    return prices


def load_price_data(tickers):
    price_data = pd.DataFrame()

    for ticker in tickers:
        price_data[ticker] = load_close_price(ticker)

    return price_data


# =========================
# 1. Load returns
# =========================
price_data = load_price_data(TICKERS)
returns = price_data.pct_change().dropna()

# 年化协方差矩阵
cov_matrix = returns.cov() * 252

# 权重向量
w = np.array([WEIGHTS[ticker] for ticker in TICKERS])

# =========================
# 2. Portfolio volatility
# =========================
portfolio_variance = np.dot(w.T, np.dot(cov_matrix.values, w))
portfolio_vol = np.sqrt(portfolio_variance)

# =========================
# 3. Marginal contribution to risk
# =========================
mctr = np.dot(cov_matrix.values, w) / portfolio_vol

# =========================
# 4. Risk contribution
# =========================
rc = w * mctr
pct_rc = rc / portfolio_vol

# =========================
# 5. Build summary table
# =========================
summary = pd.DataFrame({
    "ETF": TICKERS,
    "Weight": w,
    "Marginal Contribution to Risk": mctr,
    "Risk Contribution": rc,
    "% Risk Contribution": pct_rc
})

summary["Weight"] = summary["Weight"].map(lambda x: f"{x:.2%}")
summary["Marginal Contribution to Risk"] = summary["Marginal Contribution to Risk"].map(lambda x: f"{x:.2%}")
summary["Risk Contribution"] = summary["Risk Contribution"].map(lambda x: f"{x:.2%}")
summary["% Risk Contribution"] = summary["% Risk Contribution"].map(lambda x: f"{x:.2%}")

summary.to_csv("reports/04_risk_contribution/risk_contribution_summary.csv", index=False)

print("=== Portfolio Risk Contribution Analysis ===")
print(summary)
print()
print(f"Portfolio annualized volatility: {portfolio_vol:.2%}")

# =========================
# 6. Pie chart of % risk contribution
# =========================
# 注意：画图要用原始数值，所以重新算一份数值版
summary_plot = pd.DataFrame({
    "ETF": TICKERS,
    "pct_rc": pct_rc
})

plt.figure(figsize=(8, 8))
plt.pie(
    summary_plot["pct_rc"],
    labels=summary_plot["ETF"],
    autopct="%1.1f%%",
    startangle=90
)
plt.title("Portfolio Risk Contribution Share")
plt.tight_layout()
plt.savefig("reports/04_risk_contribution/risk_contribution_pie.png", dpi=300)

print("risk contribution summary saved to reports/04_risk_contribution/risk_contribution_summary.csv")
print("risk contribution pie chart saved to reports/04_risk_contribution/risk_contribution_pie.png")