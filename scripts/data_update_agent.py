from pathlib import Path
from datetime import datetime
import yfinance as yf

DATA_DIR = Path("data")
OUT_DIR = Path("reports/08_agent_ops")

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = OUT_DIR / "data_update_log.txt"

TICKERS = ["SPY", "QQQ", "GLD", "TLT", "XLK"]
START_DATE = "2022-01-01"


def download_ticker(ticker):
    path = DATA_DIR / f"{ticker.lower()}.csv"

    df = yf.download(
        ticker,
        start=START_DATE,
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if df.empty:
        if path.exists() and path.stat().st_size > 0:
            return {
                "ticker": ticker,
                "path": path,
                "status": "Warning",
                "message": "Download returned empty data. Existing local file was kept.",
                "latest_date": "Existing file kept",
                "rows": "N/A",
            }

        raise ValueError(
            f"No data downloaded for {ticker}, and no existing local file is available."
        )

    df.to_csv(path)

    latest_date = df.index[-1].date()
    rows = len(df)

    return {
        "ticker": ticker,
        "path": path,
        "status": "OK",
        "message": "Downloaded successfully.",
        "latest_date": latest_date,
        "rows": rows,
    }


def main():
    log_lines = [
        "Lobster Data Update Agent",
        f"Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    success = []
    warning = []
    failed = []

    for ticker in TICKERS:
        try:
            result = download_ticker(ticker)

            if result["status"] == "OK":
                success.append(result)
                log_lines.append(f"OK: {ticker}")
            else:
                warning.append(result)
                log_lines.append(f"WARNING: {ticker}")

            log_lines.append(f"- Saved to: {result['path']}")
            log_lines.append(f"- Latest Date: {result['latest_date']}")
            log_lines.append(f"- Rows: {result['rows']}")
            log_lines.append(f"- Message: {result['message']}")
            log_lines.append("")

        except Exception as error:
            failed.append((ticker, str(error)))

            log_lines.append(f"FAILED: {ticker}")
            log_lines.append(f"- Error: {error}")
            log_lines.append("")

    log_lines.append("Summary")
    log_lines.append(f"- Successful updates: {len(success)}")
    log_lines.append(f"- Warnings using existing data: {len(warning)}")
    log_lines.append(f"- Failed updates: {len(failed)}")

    if failed:
        log_lines.append("")
        log_lines.append("Failed Tickers")
        for ticker, error in failed:
            log_lines.append(f"- {ticker}: {error}")

    log_text = "\n".join(log_lines)
    LOG_FILE.write_text(log_text)

    print(log_text)
    print(f"\nSaved to {LOG_FILE}")

    if failed:
        raise RuntimeError(
            "Some ticker updates failed and no existing local backup was available."
        )


if __name__ == "__main__":
    main()