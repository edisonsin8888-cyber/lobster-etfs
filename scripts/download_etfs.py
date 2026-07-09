import yfinance as yf

tickers = ["SPY", "QQQ", "GLD", "TLT"]

for ticker in tickers:
    print(f"Downloading {ticker}...")

    data = yf.download(ticker, period="1y", interval="1d")

    filename = f"data/{ticker.lower()}.csv"
    data.to_csv(filename)

    print(f"{ticker} data saved to {filename}")
    print("-" * 40)