from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
OUT_DIR = Path("reports/08_growth_sleeve")

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_SUMMARY = OUT_DIR / "xlk_vs_spy_summary.csv"
OUT_REPORT = OUT_DIR / "xlk_growth_monitor.txt"


def load_close(ticker):
    path = DATA_DIR / f"{ticker.lower()}.csv"

    df = pd.read_csv(path, header=[0, 1], index_col=0)
    close = pd.to_numeric(df[("Close", ticker)], errors="coerce").dropna()
    close.index = pd.to_datetime(close.index)

    return close.sort_index()


def max_drawdown(series):
    cumulative_peak = series.cummax()
    drawdown = series / cumulative_peak - 1
    return drawdown.min()


def annualized_volatility(returns):
    return returns.std() * (252 ** 0.5)


def stance_from_score(score):
    if score >= 70:
        return "Constructive Growth Sleeve"
    if score >= 55:
        return "Neutral Growth Sleeve"
    return "Defensive / Watch Only"


spy = load_close("SPY")
xlk = load_close("XLK")

prices = pd.concat(
    {
        "SPY": spy,
        "XLK": xlk,
    },
    axis=1,
).dropna()

returns = prices.pct_change().dropna()

latest = prices.index[-1]

spy_1m = prices["SPY"].iloc[-1] / prices["SPY"].iloc[-21] - 1
xlk_1m = prices["XLK"].iloc[-1] / prices["XLK"].iloc[-21] - 1

spy_3m = prices["SPY"].iloc[-1] / prices["SPY"].iloc[-63] - 1
xlk_3m = prices["XLK"].iloc[-1] / prices["XLK"].iloc[-63] - 1

spy_vol = annualized_volatility(returns["SPY"].iloc[-63:])
xlk_vol = annualized_volatility(returns["XLK"].iloc[-63:])

spy_dd = max_drawdown(prices["SPY"].iloc[-63:])
xlk_dd = max_drawdown(prices["XLK"].iloc[-63:])

excess_3m_return = xlk_3m - spy_3m
volatility_premium = xlk_vol - spy_vol
drawdown_gap = xlk_dd - spy_dd

risk_adjusted_growth = excess_3m_return / xlk_vol if xlk_vol != 0 else 0

growth_score = 50
growth_score += excess_3m_return * 120
growth_score -= volatility_premium * 50
growth_score += drawdown_gap * 80
growth_score += risk_adjusted_growth * 20

growth_score = max(0, min(100, growth_score))
growth_stance = stance_from_score(growth_score)

if xlk_vol > spy_vol * 1.3:
    risk_flag = "High Growth Risk"
elif xlk_vol < spy_vol:
    risk_flag = "Controlled Growth Risk"
else:
    risk_flag = "Normal Growth Risk"

if excess_3m_return > 0.05 and xlk_dd >= spy_dd:
    tactical_view = "Strong growth leadership with controlled drawdown."
elif excess_3m_return > 0.05 and xlk_dd < spy_dd:
    tactical_view = "Strong growth rebound, but drawdown risk remains elevated."
elif excess_3m_return > 0:
    tactical_view = "Moderate growth outperformance."
else:
    tactical_view = "Growth sleeve is not outperforming SPY."

summary = pd.DataFrame(
    [
        {
            "Date": latest,
            "XLK 1M Return": xlk_1m,
            "SPY 1M Return": spy_1m,
            "XLK 3M Return": xlk_3m,
            "SPY 3M Return": spy_3m,
            "XLK 3M Excess Return": excess_3m_return,
            "XLK Annualized Volatility": xlk_vol,
            "SPY Annualized Volatility": spy_vol,
            "XLK Volatility Premium": volatility_premium,
            "XLK 3M Max Drawdown": xlk_dd,
            "SPY 3M Max Drawdown": spy_dd,
            "Drawdown Gap": drawdown_gap,
            "Risk-Adjusted Growth Score": risk_adjusted_growth,
            "Growth Sleeve Score": growth_score,
            "Growth Sleeve Risk Flag": risk_flag,
            "Tactical Growth Stance": growth_stance,
        }
    ]
)

summary.to_csv(OUT_SUMMARY, index=False)

report = f"""XLK Growth Sleeve Monitor v1

1. Growth Sleeve Question
This module evaluates whether XLK currently deserves attention as a growth / technology sector sleeve relative to SPY.

2. XLK vs SPY Performance
- Latest Date: {latest.date()}
- XLK 1M Return: {xlk_1m:.2%}
- SPY 1M Return: {spy_1m:.2%}
- XLK 3M Return: {xlk_3m:.2%}
- SPY 3M Return: {spy_3m:.2%}
- XLK 3M Excess Return: {excess_3m_return:.2%}

3. Risk Comparison
- XLK Annualized Volatility: {xlk_vol:.2%}
- SPY Annualized Volatility: {spy_vol:.2%}
- XLK Volatility Premium: {volatility_premium:.2%}
- XLK 3M Max Drawdown: {xlk_dd:.2%}
- SPY 3M Max Drawdown: {spy_dd:.2%}
- Drawdown Gap: {drawdown_gap:.2%}

4. Growth Sleeve Assessment
- Growth Sleeve Score: {growth_score:.2f}/100
- Growth Sleeve Risk Flag: {risk_flag}
- Tactical Growth Stance: {growth_stance}

5. Interpretation
{tactical_view}

6. System Link
XLK is used as the first growth / sector sleeve monitor in Lobster v2. Together with the completed GLD defensive diversification engine, it helps the system compare defensive and growth ETF sleeves.
"""

OUT_REPORT.write_text(report)

print(report)
print(f"Saved to {OUT_SUMMARY}")
print(f"Saved to {OUT_REPORT}")