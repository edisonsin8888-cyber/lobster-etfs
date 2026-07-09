import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

TICKERS = ["SPY", "QQQ", "GLD", "TLT"]
WINDOW = 30


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


def classify_regime(spy_return, stress_threshold, strong_threshold):
    if spy_return <= stress_threshold:
        return "Stress Days"
    elif spy_return >= strong_threshold:
        return "Strong Days"
    else:
        return "Normal Days"


price_data = load_price_data(TICKERS)
returns = price_data.pct_change().dropna()

# ---------- Regime-based diversification ----------

stress_threshold = returns["SPY"].quantile(0.10)
strong_threshold = returns["SPY"].quantile(0.90)

returns["Regime"] = returns["SPY"].apply(
    lambda x: classify_regime(x, stress_threshold, strong_threshold)
)

regime_counts = returns["Regime"].value_counts()

regime_display = pd.DataFrame(index=["Stress Days", "Normal Days", "Strong Days"])

for ticker in TICKERS:
    regime_display[f"{ticker} Avg Return"] = returns.groupby("Regime")[ticker].mean()
    regime_display[f"{ticker} Volatility"] = returns.groupby("Regime")[ticker].std()

regime_display["Number of Days"] = regime_counts
regime_display = regime_display.loc[["Stress Days", "Normal Days", "Strong Days"]]

regime_display.to_csv("reports/02_regime_analysis/regime_diversification_detailed.csv")

print("=== Regime-based Diversification Analysis ===")
print(regime_display)

# ---------- Rolling correlation ----------

rolling_corr = pd.DataFrame()
rolling_corr["GLD-SPY"] = returns["GLD"].rolling(WINDOW).corr(returns["SPY"])
rolling_corr["GLD-QQQ"] = returns["GLD"].rolling(WINDOW).corr(returns["QQQ"])
rolling_corr["GLD-TLT"] = returns["GLD"].rolling(WINDOW).corr(returns["TLT"])

rolling_corr.to_csv("reports/03_rolling_analysis/rolling_correlation_detailed.csv")

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
plt.savefig("reports/03_rolling_analysis/rolling_correlation_detailed.png", dpi=300)

# ---------- Rolling volatility ----------

rolling_vol = returns[TICKERS].rolling(WINDOW).std() * np.sqrt(252)
rolling_vol.to_csv("reports/03_rolling_analysis/rolling_volatility_detailed.csv")

plt.figure(figsize=(10, 6))

for ticker in TICKERS:
    plt.plot(rolling_vol.index, rolling_vol[ticker], label=ticker)

plt.title("30-Day Rolling Annualized Volatility")
plt.xlabel("Date")
plt.ylabel("Annualized Volatility")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("reports/03_rolling_analysis/rolling_volatility_detailed.png", dpi=300)

print()
print("Saved files:")
print("reports/02_regime_analysis/regime_diversification_detailed.csv")
print("reports/03_rolling_analysis/rolling_correlation_detailed.csv")
print("reports/03_rolling_analysis/rolling_correlation_detailed.png")
print("reports/03_rolling_analysis/rolling_volatility_detailed.csv")
print("reports/03_rolling_analysis/rolling_volatility_detailed.png")