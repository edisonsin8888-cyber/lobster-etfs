import pandas as pd
import numpy as np

# 读取单个 ETF 的 Close 价格
def load_close_price(ticker):
    file_path = f"data/{ticker.lower()}.csv"
    df = pd.read_csv(file_path, header=[0, 1], index_col=0)

    prices = df[("Close", ticker)].dropna()
    prices = pd.to_numeric(prices, errors="coerce").dropna()

    prices.index = pd.to_datetime(prices.index)
    prices.name = ticker
    return prices


# 1. 读取四只 ETF 的价格
tickers = ["SPY", "QQQ", "GLD", "TLT"]

price_data = pd.DataFrame()

for ticker in tickers:
    price_data[ticker] = load_close_price(ticker)

# 2. 计算日收益率
returns = price_data.pct_change().dropna()

# 3. 计算相关性矩阵
correlation_matrix = returns.corr()

print("=== ETF Correlation Matrix ===")
print(correlation_matrix)
print()

# 4. 定义两个组合
weights_without_gld = {
    "SPY": 0.60,
    "QQQ": 0.20,
    "TLT": 0.20
}

weights_with_gld = {
    "SPY": 0.50,
    "QQQ": 0.20,
    "TLT": 0.15,
    "GLD": 0.15
}

# 5. 计算组合收益率序列
portfolio_without_gld = (
    returns["SPY"] * weights_without_gld["SPY"] +
    returns["QQQ"] * weights_without_gld["QQQ"] +
    returns["TLT"] * weights_without_gld["TLT"]
)

portfolio_with_gld = (
    returns["SPY"] * weights_with_gld["SPY"] +
    returns["QQQ"] * weights_with_gld["QQQ"] +
    returns["TLT"] * weights_with_gld["TLT"] +
    returns["GLD"] * weights_with_gld["GLD"]
)

# 6. 定义一个函数：计算组合指标
def calculate_metrics(return_series):
    cumulative = (1 + return_series).cumprod()

    total_return = cumulative.iloc[-1] - 1
    annualized_vol = return_series.std() * np.sqrt(252)

    rolling_max = cumulative.cummax()
    drawdown = cumulative / rolling_max - 1
    max_drawdown = drawdown.min()

    return total_return, annualized_vol, max_drawdown


# 7. 分别计算两个组合的指标
without_gld_metrics = calculate_metrics(portfolio_without_gld)
with_gld_metrics = calculate_metrics(portfolio_with_gld)

# 8. 汇总成表
portfolio_summary = pd.DataFrame([
    {
        "Portfolio": "Without GLD",
        "Total Return": without_gld_metrics[0],
        "Annualized Volatility": without_gld_metrics[1],
        "Max Drawdown": without_gld_metrics[2]
    },
    {
        "Portfolio": "With GLD",
        "Total Return": with_gld_metrics[0],
        "Annualized Volatility": with_gld_metrics[1],
        "Max Drawdown": with_gld_metrics[2]
    }
])

# 百分比格式化显示
portfolio_summary_display = portfolio_summary.copy()
portfolio_summary_display["Total Return"] = portfolio_summary_display["Total Return"].map(lambda x: f"{x:.2%}")
portfolio_summary_display["Annualized Volatility"] = portfolio_summary_display["Annualized Volatility"].map(lambda x: f"{x:.2%}")
portfolio_summary_display["Max Drawdown"] = portfolio_summary_display["Max Drawdown"].map(lambda x: f"{x:.2%}")

print("=== Portfolio Comparison ===")
print(portfolio_summary_display)

# 9. 保存结果
correlation_matrix.to_csv("reports/correlation_matrix.csv")
portfolio_summary.to_csv("reports/portfolio_summary.csv", index=False)

print()
print("Correlation matrix saved to reports/correlation_matrix.csv")
print("Portfolio summary saved to reports/portfolio_summary.csv")