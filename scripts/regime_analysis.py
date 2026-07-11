import pandas as pd
import numpy as np

def load_close_price(ticker):
    file_path = f"data/{ticker.lower()}.csv"
    df = pd.read_csv(file_path, header=[0, 1], index_col=0)

    prices = df[("Close", ticker)].dropna()
    prices = pd.to_numeric(prices, errors="coerce").dropna()
    prices.index = pd.to_datetime(prices.index)
    prices.name = ticker

    return prices

def calculate_regime_thresholds(spy_returns):
    return spy_returns.quantile(0.10), spy_returns.quantile(0.90)


def classify_regime(spy_return, stress_threshold, strong_threshold):
    if spy_return <= stress_threshold:
        return "Stress Days"
    elif spy_return >= strong_threshold:
        return "Strong Days"
    else:
        return "Normal Days"

def main():
    tickers = ["SPY", "QQQ", "GLD", "TLT"]

    price_data = pd.DataFrame()

    for ticker in tickers:
        price_data[ticker] = load_close_price(ticker)

    returns = price_data.pct_change().dropna()

    # 用 SPY 的收益率定义市场状态
    stress_threshold, strong_threshold = calculate_regime_thresholds(returns["SPY"])

    returns["Regime"] = returns["SPY"].apply(
        lambda spy_return: classify_regime(spy_return, stress_threshold, strong_threshold)
    )

    # 计算不同市场状态下各 ETF 的平均日收益率
    regime_summary = returns.groupby("Regime")[tickers].mean()

    # 计算每个市场状态包含多少天
    regime_counts = returns["Regime"].value_counts()
    regime_summary["Number of Days"] = regime_counts

    # 调整顺序
    regime_summary = regime_summary.loc[["Stress Days", "Normal Days", "Strong Days"]]

    # 保存未格式化数据
    regime_summary.to_csv("reports/02_regime_analysis/regime_analysis.csv")

    # 显示百分比版本
    display_df = regime_summary.copy()

    for ticker in tickers:
        display_df[ticker] = display_df[ticker].map(lambda x: f"{x:.2%}")

    print("=== Market Regime Analysis ===")
    print(display_df)

    # Downside Capture：SPY 下跌日里，各 ETF 的平均表现
    downside_days = returns[returns["SPY"] < 0]

    downside_capture = {}

    spy_down_avg = downside_days["SPY"].mean()

    for ticker in tickers:
        etf_down_avg = downside_days[ticker].mean()
        downside_capture[ticker] = etf_down_avg / spy_down_avg

    downside_capture_df = pd.DataFrame(
        list(downside_capture.items()),
        columns=["ETF", "Downside Capture Ratio"]
    )

    downside_capture_df.to_csv("reports/02_regime_analysis/downside_capture.csv", index=False)

    display_capture = downside_capture_df.copy()
    display_capture["Downside Capture Ratio"] = display_capture["Downside Capture Ratio"].map(lambda x: f"{x:.2f}")

    print()
    print("=== Downside Capture Ratio ===")
    print(display_capture)

    print()
    print("Regime analysis saved to reports/02_regime_analysis/regime_analysis.csv")
    print("Downside capture saved to reports/02_regime_analysis/downside_capture.csv")


if __name__ == "__main__":
    main()
