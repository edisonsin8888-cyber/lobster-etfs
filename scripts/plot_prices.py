import pandas as pd
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

# 标准化：让每个 ETF 都从 1 开始
normalized_prices = price_data / price_data.iloc[0]

plt.figure(figsize=(10, 6))

for ticker in tickers:
    plt.plot(normalized_prices.index, normalized_prices[ticker], label=ticker)

plt.title("Normalized ETF Price Performance")
plt.xlabel("Date")
plt.ylabel("Normalized Price")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("reports/normalized_prices.png", dpi=300)

print("Normalized price chart saved to reports/normalized_prices.png")