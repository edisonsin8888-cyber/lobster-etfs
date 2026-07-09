import pandas as pd
import numpy as np
from pathlib import Path

WATCHLIST = ["SPY", "QQQ", "GLD", "TLT", "XLK"]

DATA_DIR = Path("data")
OUT_DIR = Path("reports/07_lobster_watchlist")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SNAPSHOT_FILE = OUT_DIR / "etf_watchlist_snapshot.csv"
SUMMARY_FILE = OUT_DIR / "etf_watchlist_summary.txt"


def load_close(ticker):
    df = pd.read_csv(DATA_DIR / f"{ticker.lower()}.csv", header=[0, 1], index_col=0)
    close = pd.to_numeric(df[("Close", ticker)], errors="coerce").dropna()
    close.index = pd.to_datetime(close.index)
    return close.sort_index()


def max_drawdown(returns):
    nav = (1 + returns).cumprod()
    return (nav / nav.cummax() - 1).min()


def momentum_flag(ret_1m, ret_3m):
    if ret_1m > 0 and ret_3m > 0:
        return "Strong"
    if ret_1m < 0 and ret_3m < 0:
        return "Weak"
    return "Neutral"


def risk_flag(vol, drawdown):
    if vol >= 0.25 or drawdown <= -0.12:
        return "High Risk"
    if vol <= 0.15 and drawdown >= -0.06:
        return "Defensive"
    return "Normal"


def role_tag(ticker, momentum, risk):
    if ticker == "SPY":
        return "Core Equity Sleeve"
    if ticker in ["QQQ", "XLK"]:
        return "Growth / Sector Sleeve" if momentum != "Weak" else "Weak Growth Sleeve"
    if ticker == "GLD":
        return "Defensive Diversification Sleeve"
    if ticker == "TLT":
        return "Rate-Sensitive Defensive Sleeve"
    return "ETF Sleeve"


def research_priority(ticker, momentum, risk, role):
    if ticker == "GLD":
        return "High"
    if risk == "High Risk" or momentum == "Weak":
        return "Medium"
    if "Growth" in role and momentum == "Strong":
        return "Medium"
    return "Low"


def interpretation(ticker, ret_3m, vol, role, priority):
    return (
        f"{ticker} is classified as {role}. "
        f"Its 3M return is {ret_3m:.2%}, with annualized volatility of {vol:.2%}. "
        f"Research priority is {priority}."
    )


rows = []

for ticker in WATCHLIST:
    close = load_close(ticker)
    returns = close.pct_change().dropna()

    ret_1m = close.iloc[-1] / close.iloc[-22] - 1
    ret_3m = close.iloc[-1] / close.iloc[-63] - 1

    sample = returns.tail(63)
    vol = sample.std() * np.sqrt(252)
    drawdown = max_drawdown(sample)

    momentum = momentum_flag(ret_1m, ret_3m)
    risk = risk_flag(vol, drawdown)
    role = role_tag(ticker, momentum, risk)
    priority = research_priority(ticker, momentum, risk, role)

    rows.append({
        "ETF": ticker,
        "Latest Price": close.iloc[-1],
        "1M Return": ret_1m,
        "3M Return": ret_3m,
        "Annualized Volatility": vol,
        "3M Max Drawdown": drawdown,
        "Momentum Flag": momentum,
        "Risk Flag": risk,
        "Role Tag": role,
        "Research Priority": priority,
        "Short Interpretation": interpretation(ticker, ret_3m, vol, role, priority),
    })

priority_order = {"High": 0, "Medium": 1, "Low": 2}
watchlist = pd.DataFrame(rows)
watchlist["Priority Rank"] = watchlist["Research Priority"].map(priority_order)
watchlist = watchlist.sort_values(["Priority Rank", "3M Return"], ascending=[True, False])
watchlist = watchlist.drop(columns=["Priority Rank"]).reset_index(drop=True)
watchlist.to_csv(SNAPSHOT_FILE, index=False)

best = watchlist.loc[watchlist["3M Return"].idxmax()]
weakest = watchlist.loc[watchlist["3M Return"].idxmin()]
highest_vol = watchlist.loc[watchlist["Annualized Volatility"].idxmax()]
gld = watchlist.loc[watchlist["ETF"] == "GLD"].iloc[0]

summary = f"""ETF Watchlist Monitor v2

Watchlist:
{", ".join(WATCHLIST)}

Top-Level ETF Signals:
- Best 3M performer: {best["ETF"]} ({best["3M Return"]:.2%})
- Weakest 3M performer: {weakest["ETF"]} ({weakest["3M Return"]:.2%})
- Highest volatility ETF: {highest_vol["ETF"]} ({highest_vol["Annualized Volatility"]:.2%})

GLD Watchlist Role:
- Role Tag: {gld["Role Tag"]}
- Momentum Flag: {gld["Momentum Flag"]}
- Risk Flag: {gld["Risk Flag"]}
- Research Priority: {gld["Research Priority"]}

Lobster Interpretation:
This watchlist acts as the top-level ETF scanner. It classifies each ETF into a portfolio sleeve role and assigns research priority. GLD remains linked to the deeper Gold Engine because it is the completed defensive diversification deep-dive module.
"""

SUMMARY_FILE.write_text(summary)

print("=== ETF Watchlist Monitor v2 ===")
print(watchlist)
print()
print(summary)
print(f"Saved to {SNAPSHOT_FILE}")
print(f"Saved to {SUMMARY_FILE}")