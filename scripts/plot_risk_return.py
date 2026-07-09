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

tickers = ["SPY", "QQQ", "GLD", "TLT"]

results = []

for ticker in tickers:
    prices = load_close_price(ticker)
    returns = prices.pct_change().dropna()

    total_return = prices.iloc[-1] / prices.iloc[0] - 1
    annualized_volatility = returns.std() * np.sqrt(252)

    results.append({
        "ETF": ticker,
        "Total Return": total_return,
        "Annualized Volatility": annualized_volatility
    })

results_df = pd.DataFrame(results)

plt.figure(figsize=(8, 6))

plt.scatter(
    results_df["Annualized Volatility"],
    results_df["Total Return"],
    s=100
)

for _, row in results_df.iterrows():
    plt.text(
        row["Annualized Volatility"] + 0.002,
        row["Total Return"] + 0.002,
        row["ETF"]
    )

plt.title("ETF Risk-Return Scatter Plot")
plt.xlabel("Annualized Volatility")
plt.ylabel("Total Return")
plt.grid(True)
plt.tight_layout()

plt.savefig("reports/risk_return_scatter.png", dpi=300)

print(results_df)
print("Risk-return scatter plot saved to reports/risk_return_scatter.png")