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

price_data = pd.DataFrame()

for ticker in tickers:
    price_data[ticker] = load_close_price(ticker)

returns = price_data.pct_change().dropna()

window = 30

# 1. 30-day rolling correlation with GLD
rolling_corr = pd.DataFrame()
rolling_corr["GLD-SPY"] = returns["GLD"].rolling(window).corr(returns["SPY"])
rolling_corr["GLD-QQQ"] = returns["GLD"].rolling(window).corr(returns["QQQ"])
rolling_corr["GLD-TLT"] = returns["GLD"].rolling(window).corr(returns["TLT"])

rolling_corr.to_csv("reports/03_rolling_analysis/rolling_correlation.csv")

plt.figure(figsize=(10, 6))

for col in rolling_corr.columns:
    plt.plot(rolling_corr.index, rolling_corr[col], label=col)

plt.axhline(0, linestyle="--", linewidth=1)
plt.title("30-Day Rolling Correlation with GLD")
plt.xlabel("Date")
plt.ylabel("Rolling Correlation")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("reports/03_rolling_analysis/rolling_correlation.png", dpi=300)

# 2. 30-day rolling volatility
rolling_vol = returns.rolling(window).std() * np.sqrt(252)

rolling_vol.to_csv("reports/03_rolling_analysis/rolling_volatility.csv")

plt.figure(figsize=(10, 6))

for ticker in tickers:
    plt.plot(rolling_vol.index, rolling_vol[ticker], label=ticker)

plt.title("30-Day Rolling Annualized Volatility")
plt.xlabel("Date")
plt.ylabel("Annualized Volatility")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("reports/03_rolling_analysis/rolling_volatility.png", dpi=300)

print("Rolling correlation saved to reports/03_rolling_analysis/rolling_correlation.csv")
print("Rolling correlation chart saved to reports/03_rolling_analysis/rolling_correlation.png")
print("Rolling volatility saved to reports/03_rolling_analysis/rolling_volatility.csv")
print("Rolling volatility chart saved to reports/03_rolling_analysis/rolling_volatility.png")