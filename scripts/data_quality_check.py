from pathlib import Path
from datetime import datetime
import pandas as pd

DATA_DIR = Path("data")
OUT_DIR = Path("reports/08_agent_ops")

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_REPORT = OUT_DIR / "data_quality_report.csv"
OUT_SUMMARY = OUT_DIR / "data_quality_summary.txt"

TICKERS = ["SPY", "QQQ", "GLD", "TLT", "XLK"]

MIN_ROWS = 250
STALE_DAYS_LIMIT = 10
ABNORMAL_DAILY_RETURN = 0.15


def load_close(ticker):
    path = DATA_DIR / f"{ticker.lower()}.csv"

    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path, header=[0, 1], index_col=0)

    if df.empty:
        raise ValueError(f"Empty data file: {path}")

    close = pd.to_numeric(df[("Close", ticker)], errors="coerce")
    close.index = pd.to_datetime(close.index)

    return close.sort_index()


def check_ticker(ticker):
    status = "Passed"
    issues = []

    try:
        close = load_close(ticker)

        row_count = len(close)
        missing_values = int(close.isna().sum())
        duplicate_dates = int(close.index.duplicated().sum())

        latest_date = close.dropna().index[-1]
        days_since_latest = (pd.Timestamp.today().normalize() - latest_date.normalize()).days

        returns = close.pct_change().dropna()
        abnormal_return_count = int((returns.abs() > ABNORMAL_DAILY_RETURN).sum())

        if row_count < MIN_ROWS:
            issues.append("insufficient rows")

        if missing_values > 0:
            issues.append("missing close values")

        if duplicate_dates > 0:
            issues.append("duplicate dates")

        if days_since_latest > STALE_DAYS_LIMIT:
            issues.append("stale data")

        if abnormal_return_count > 0:
            issues.append("abnormal daily return detected")

        if issues:
            status = "Warning"

        return {
            "Ticker": ticker,
            "Status": status,
            "Rows": row_count,
            "Missing Close Values": missing_values,
            "Duplicate Dates": duplicate_dates,
            "Latest Date": latest_date.date(),
            "Days Since Latest": days_since_latest,
            "Abnormal Return Count": abnormal_return_count,
            "Issues": ", ".join(issues) if issues else "None",
        }

    except Exception as error:
        return {
            "Ticker": ticker,
            "Status": "Failed",
            "Rows": 0,
            "Missing Close Values": "N/A",
            "Duplicate Dates": "N/A",
            "Latest Date": "N/A",
            "Days Since Latest": "N/A",
            "Abnormal Return Count": "N/A",
            "Issues": str(error),
        }


def main():
    rows = [check_ticker(ticker) for ticker in TICKERS]
    report = pd.DataFrame(rows)

    report.to_csv(OUT_REPORT, index=False)

    passed = (report["Status"] == "Passed").sum()
    warning = (report["Status"] == "Warning").sum()
    failed = (report["Status"] == "Failed").sum()

    if failed > 0:
        overall_status = "Failed"
    elif warning > 0:
        overall_status = "Warning"
    else:
        overall_status = "Passed"

    summary_lines = [
        "Lobster Data Quality Check Agent",
        f"Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Overall Data Quality Status: {overall_status}",
        f"- Passed: {passed}",
        f"- Warning: {warning}",
        f"- Failed: {failed}",
        "",
        "Ticker-Level Results",
    ]

    for _, row in report.iterrows():
        summary_lines.append(
            f"- {row['Ticker']}: {row['Status']} | "
            f"Latest Date: {row['Latest Date']} | "
            f"Rows: {row['Rows']} | "
            f"Issues: {row['Issues']}"
        )

    summary_text = "\n".join(summary_lines)
    OUT_SUMMARY.write_text(summary_text)

    print(summary_text)
    print(f"\nSaved to {OUT_REPORT}")
    print(f"Saved to {OUT_SUMMARY}")

    if failed > 0:
        raise RuntimeError("Data quality check failed.")


if __name__ == "__main__":
    main()