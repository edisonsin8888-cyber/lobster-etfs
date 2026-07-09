import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_close_price(ticker):
    file_path = f"data/{ticker.lower()}.csv"
    df = pd.read_csv(file_path, header=[0, 1], index_col=0)

    prices = df[("Close", ticker)].dropna()
    prices = pd.to_numeric(prices, errors="coerce").dropna()
    prices.index = pd.to_datetime(prices.index)
    prices.name = ticker

    return prices

def calculate_metrics(return_series):
    cumulative = (1 + return_series).cumprod()

    total_return = cumulative.iloc[-1] - 1
    annualized_volatility = return_series.std() * np.sqrt(252)

    rolling_max = cumulative.cummax()
    drawdown = cumulative / rolling_max - 1
    max_drawdown = drawdown.min()

    return total_return, annualized_volatility, max_drawdown

tickers = ["SPY", "QQQ", "GLD", "TLT"]

price_data = pd.DataFrame()

for ticker in tickers:
    price_data[ticker] = load_close_price(ticker)

returns = price_data.pct_change().dropna()

results = []

gld_weights = [0, 0.05, 0.10, 0.15, 0.20, 0.25]

for gld_weight in gld_weights:
    qqq_weight = 0.20
    tlt_weight = 0.20
    spy_weight = 1 - qqq_weight - tlt_weight - gld_weight

    portfolio_return = (
        returns["SPY"] * spy_weight +
        returns["QQQ"] * qqq_weight +
        returns["TLT"] * tlt_weight +
        returns["GLD"] * gld_weight
    )

    total_return, annualized_volatility, max_drawdown = calculate_metrics(portfolio_return)

    results.append({
        "GLD Weight": gld_weight,
        "SPY Weight": spy_weight,
        "QQQ Weight": qqq_weight,
        "TLT Weight": tlt_weight,
        "Total Return": total_return,
        "Annualized Volatility": annualized_volatility,
        "Max Drawdown": max_drawdown
    })

results_df = pd.DataFrame(results)

results_df.to_csv("reports/05_weight_sensitivity/gld_weight_sensitivity.csv", index=False)

display_df = results_df.copy()
for col in ["GLD Weight", "SPY Weight", "QQQ Weight", "TLT Weight", "Total Return", "Annualized Volatility", "Max Drawdown"]:
    display_df[col] = display_df[col].map(lambda x: f"{x:.2%}")

print("=== GLD Weight Sensitivity Analysis ===")
print(display_df)

plt.figure(figsize=(10, 6))

plt.plot(results_df["GLD Weight"], results_df["Total Return"], marker="o", label="Total Return")
plt.plot(results_df["GLD Weight"], results_df["Annualized Volatility"], marker="o", label="Annualized Volatility")
plt.plot(results_df["GLD Weight"], results_df["Max Drawdown"].abs(), marker="o", label="Max Drawdown (Absolute)")

plt.title("GLD Weight Sensitivity Analysis")
plt.xlabel("GLD Weight")
plt.ylabel("Metric Value")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("reports/05_weight_sensitivity/gld_weight_sensitivity.png", dpi=300)

print("GLD weight sensitivity table saved to reports/05_weight_sensitivity/gld_weight_sensitivity.csv")
print("GLD weight sensitivity chart saved to reports/05_weight_sensitivity/gld_weight_sensitivity.png")