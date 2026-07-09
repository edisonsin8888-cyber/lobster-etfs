import yfinance as yf

ticker = "SPY"

data = yf.download(ticker, period="1y", interval="1d")

print(data.head())

data.to_csv("data/spy.csv")

print("SPY data saved to data/spy.csv")