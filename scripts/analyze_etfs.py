import pandas as pd
import numpy as np

tickers = ["SPY", "QQQ", "GLD", "TLT"]

results = []

for ticker in tickers:
    file_path = f"data/{ticker.lower()}.csv"

    # 读取 yfinance 保存的双层表头 CSV
    df = pd.read_csv(file_path, header=[0, 1], index_col=0)

    # 取该 ETF 的 Close 价格
    prices = df[("Close", ticker)].dropna()

    # 确保价格是数字
    prices = pd.to_numeric(prices, errors="coerce").dropna()

    returns = prices.pct_change().dropna()

    total_return = prices.iloc[-1] / prices.iloc[0] - 1
    annualized_vol = returns.std() * np.sqrt(252)

    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = cumulative / rolling_max - 1
    max_drawdown = drawdown.min()

    results.append({
        "ETF": ticker,
        "Total Return": total_return,
        "Annualized Volatility": annualized_vol,
        "Max Drawdown": max_drawdown
    })

results_df = pd.DataFrame(results)

results_df["Total Return"] = results_df["Total Return"].map(lambda x: f"{x:.2%}")
results_df["Annualized Volatility"] = results_df["Annualized Volatility"].map(lambda x: f"{x:.2%}")
results_df["Max Drawdown"] = results_df["Max Drawdown"].map(lambda x: f"{x:.2%}")

print(results_df)
results_df.to_csv("reports/01_summary/etf_summary.csv", index=False)
print("ETF summary saved to reports/01_summary/etf_summary.csv")