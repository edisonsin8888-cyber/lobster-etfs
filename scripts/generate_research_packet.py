"""Generate a structured, AI-readable packet from existing research artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any

import pandas as pd

from regime_analysis import calculate_regime_thresholds, classify_regime


SCHEMA_VERSION = "1.1.0"
CORE_TICKERS = {"SPY", "QQQ", "GLD", "TLT"}

DATA_QUALITY_FILE = Path("reports/08_agent_ops/data_quality_report.csv")
SCORE_FILE = Path("reports/06_score_and_monitor/gold_diversification_score.csv")
HISTORY_FILE = Path("reports/06_score_and_monitor/allocation_history.csv")
ALERT_FILE = Path("reports/06_score_and_monitor/diversification_alert.txt")
REGIME_SUMMARY_FILE = Path("reports/02_regime_analysis/regime_analysis.csv")
SPY_DATA_FILE = Path("data/spy.csv")
REGIME_METHOD_FILE = Path("scripts/regime_analysis.py")
README_FILE = Path("README.md")
OUTPUT_FILE = Path("reports/07_ai_research/research_packet.json")

SOURCE_REPORT_PATHS = {
    "data_quality_report": str(DATA_QUALITY_FILE),
    "gold_diversification_score": str(SCORE_FILE),
    "allocation_history": str(HISTORY_FILE),
    "diversification_alert": str(ALERT_FILE),
    "regime_summary": str(REGIME_SUMMARY_FILE),
    "market_data": str(SPY_DATA_FILE),
    "regime_methodology": str(REGIME_METHOD_FILE),
    "limitations": str(README_FILE),
}

DATA_QUALITY_COLUMNS = [
    "Ticker",
    "Status",
    "Rows",
    "Missing Close Values",
    "Duplicate Dates",
    "Latest Date",
    "Days Since Latest",
    "Abnormal Return Count",
    "Issues",
]
SCORE_COLUMNS = ["Metric", "Value", "Score"]
SCORE_COMPONENTS = [
    "Average GLD-Equity Rolling Correlation",
    "GLD / SPY Rolling Volatility Ratio",
    "GLD Stress Return Minus SPY Stress Return",
    "GLD % Risk Contribution",
]
FINAL_SCORE_METRIC = "Final Gold Diversification Score"
HISTORY_COLUMNS = [
    "Date",
    "Gold Diversification Score",
    "Status",
    "Alert Level",
    "Allocation Guidance Score",
    "Recommendation Confidence",
    "Best Marginal Step",
    "Recommended Strategic Range",
]
REGIME_SUMMARY_COLUMNS = ["Regime", "SPY", "QQQ", "GLD", "TLT", "Number of Days"]


class RequiredSourceError(RuntimeError):
    """A required source cannot safely populate the packet."""


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def empty_packet() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": utc_timestamp(),
        "git_commit": git_commit(),
        "analysis_readiness": {
            "status": "blocked",
            "blocking_issues": [],
            "review_warnings": [],
        },
        "dates": {
            "analysis_as_of_date": None,
            "analysis_as_of_date_note": (
                "No single directly attributable unified analysis date is available: "
                "the score CSV is intrinsically undated and allocation history uses period-end labels."
            ),
            "core_market_data_as_of_date": None,
            "all_tracked_market_data_as_of_date": None,
            "allocation_history_period_label": None,
            "ticker_latest_dates": {},
        },
        "data_quality": {
            "source_as_of_date": None,
            "overall_status": None,
            "ticker_checks": [],
        },
        "gold_diversification_score": {
            "source_as_of_date": None,
            "source_as_of_date_note": "The source CSV has no date column.",
            "final_score": None,
            "components": [],
        },
        "market_regime": {
            "current": {
                "source_as_of_date": None,
                "regime_label": None,
                "observation_date": None,
                "spy_return": None,
                "thresholds": {
                    "stress_return_threshold": None,
                    "strong_return_threshold": None,
                },
                "methodology_reference": str(REGIME_METHOD_FILE),
                "source_path": str(SPY_DATA_FILE),
            },
            "regime_summary": {
                "source_as_of_date": None,
                "source_path": str(REGIME_SUMMARY_FILE),
                "rows": [],
            },
        },
        "allocation_guidance": {
            "source_as_of_date": None,
            "allocation_guidance_score": None,
            "recommendation_confidence": None,
            "best_marginal_step": None,
            "recommended_strategic_range": None,
            "allocation_history_status": None,
            "allocation_history_alert_level": None,
        },
        "alert": {
            "source_as_of_date": None,
            "alert_level": None,
            "diversification_trend": None,
            "unstructured_context": {
                "source_path": str(ALERT_FILE),
                "remaining_text": None,
                "content_type": "unstructured_text_not_numeric_source_of_truth",
            },
        },
        "recent_score_changes": {
            "source_as_of_date": None,
            "one_month": {
                "gold_diversification_score_change": None,
                "allocation_guidance_score_change": None,
                "explanation": None,
            },
            "three_month": {
                "gold_diversification_score_change": None,
                "allocation_guidance_score_change": None,
                "explanation": None,
            },
        },
        "methodology_limitations": [],
        "source_report_paths": SOURCE_REPORT_PATHS,
    }


def write_packet(packet: dict[str, Any]) -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n")


def require_csv(path: Path, columns: list[str]) -> pd.DataFrame:
    if not path.exists():
        raise RequiredSourceError(f"Required source is missing: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as error:
        raise RequiredSourceError(f"Required source is unreadable: {path} ({error})") from error

    missing_columns = [column for column in columns if column not in df.columns]
    if missing_columns:
        raise RequiredSourceError(
            f"Required source is incompatible: {path} is missing columns {missing_columns}"
        )
    if df.empty:
        raise RequiredSourceError(f"Required source is empty: {path}")
    return df


def require_text(path: Path) -> str:
    if not path.exists():
        raise RequiredSourceError(f"Required source is missing: {path}")
    try:
        return path.read_text()
    except Exception as error:
        raise RequiredSourceError(f"Required source is unreadable: {path} ({error})") from error


def number_or_null(value: Any) -> float | None:
    if pd.isna(value):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def required_number(value: Any, description: str) -> float:
    parsed = number_or_null(value)
    if parsed is None:
        raise RequiredSourceError(f"Required numeric value is unavailable or invalid: {description}")
    return parsed


def parse_date(value: Any, description: str) -> pd.Timestamp:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        raise RequiredSourceError(f"Required date is unavailable or invalid: {description}")
    return pd.Timestamp(parsed).normalize()


def date_string(value: pd.Timestamp | None) -> str | None:
    return value.date().isoformat() if value is not None else None


def read_data_quality(
    warnings: list[str],
) -> tuple[dict[str, Any], dict[str, str | None], str | None, str | None]:
    df = require_csv(DATA_QUALITY_FILE, DATA_QUALITY_COLUMNS)
    tickers = df["Ticker"].astype(str).str.strip()
    if tickers.duplicated().any():
        duplicates = sorted(tickers[tickers.duplicated()].unique())
        raise RequiredSourceError(f"Duplicate ticker rows in {DATA_QUALITY_FILE}: {duplicates}")

    rows: list[dict[str, Any]] = []
    ticker_dates: dict[str, str | None] = {}
    valid_dates: list[pd.Timestamp] = []
    core_valid_dates: list[pd.Timestamp] = []
    core_rows: dict[str, pd.Series] = {}

    for index, row in df.iterrows():
        ticker = tickers.iloc[index]
        status = str(row["Status"]).strip() if not pd.isna(row["Status"]) else None
        latest_date: pd.Timestamp | None = None
        if not pd.isna(row["Latest Date"]):
            parsed = pd.to_datetime(row["Latest Date"], errors="coerce")
            if not pd.isna(parsed):
                latest_date = pd.Timestamp(parsed).normalize()

        ticker_dates[ticker] = date_string(latest_date)
        if status != "Failed" and latest_date is not None:
            valid_dates.append(latest_date)

        rows.append(
            {
                "ticker": ticker,
                "status": status,
                "rows": number_or_null(row["Rows"]),
                "missing_close_values": number_or_null(row["Missing Close Values"]),
                "duplicate_dates": number_or_null(row["Duplicate Dates"]),
                "latest_date": date_string(latest_date),
                "days_since_latest": number_or_null(row["Days Since Latest"]),
                "abnormal_return_count": number_or_null(row["Abnormal Return Count"]),
                "issues": None if pd.isna(row["Issues"]) else str(row["Issues"]),
            }
        )
        if ticker in CORE_TICKERS:
            core_rows[ticker] = row

    missing_core = sorted(CORE_TICKERS - set(core_rows))
    if missing_core:
        raise RequiredSourceError(f"Core tickers missing from {DATA_QUALITY_FILE}: {missing_core}")

    for ticker in sorted(CORE_TICKERS):
        row = core_rows[ticker]
        status = str(row["Status"]).strip() if not pd.isna(row["Status"]) else None
        if status == "Failed":
            raise RequiredSourceError(f"Core ticker failed data quality: {ticker}")
        if status != "Passed":
            warnings.append(f"Core ticker data quality is {status}: {ticker}")
        core_valid_dates.append(
            parse_date(row["Latest Date"], f"{DATA_QUALITY_FILE} Latest Date for {ticker}")
        )

    for row in rows:
        if row["ticker"] not in CORE_TICKERS and row["status"] != "Passed":
            warnings.append(
                f"Additional monitored ticker data quality is {row['status']}: {row['ticker']}"
            )

    if not valid_dates:
        raise RequiredSourceError(f"No valid ticker latest dates in {DATA_QUALITY_FILE}")

    statuses = {row["status"] for row in rows}
    overall_status = "Failed" if "Failed" in statuses else "Warning" if "Warning" in statuses else "Passed"
    all_tracked_date = min(valid_dates)
    core_market_data_date = min(core_valid_dates)

    return (
        {
            "source_as_of_date": date_string(all_tracked_date),
            "overall_status": overall_status,
            "ticker_checks": rows,
        },
        ticker_dates,
        date_string(core_market_data_date),
        date_string(all_tracked_date),
    )


def metric_row(df: pd.DataFrame, metric: str) -> pd.Series:
    rows = df.loc[df["Metric"] == metric]
    if len(rows) != 1:
        raise RequiredSourceError(
            f"Expected exactly one '{metric}' row in {SCORE_FILE}; found {len(rows)}"
        )
    return rows.iloc[0]


def score_source_date(df: pd.DataFrame, warnings: list[str]) -> str | None:
    date_columns = ["Source As Of Date", "As Of Date", "Date"]
    source_column = next((column for column in date_columns if column in df.columns), None)
    if source_column is None:
        warnings.append(
            "gold_diversification_score.csv lacks intrinsic date metadata; "
            "gold_diversification_score.source_as_of_date is null."
        )
        return None

    parsed_dates = pd.to_datetime(df[source_column], errors="coerce").dropna().unique()
    if len(parsed_dates) != 1:
        warnings.append(
            "gold_diversification_score.csv has unavailable or inconsistent intrinsic date metadata; "
            "gold_diversification_score.source_as_of_date is null."
        )
        return None
    return date_string(pd.Timestamp(parsed_dates[0]).normalize())


def read_score(warnings: list[str]) -> dict[str, Any]:
    df = require_csv(SCORE_FILE, SCORE_COLUMNS)
    final_row = metric_row(df, FINAL_SCORE_METRIC)
    components = []
    for metric in SCORE_COMPONENTS:
        row = metric_row(df, metric)
        components.append(
            {
                "source_metric": metric,
                "value": required_number(row["Value"], f"{SCORE_FILE} {metric} Value"),
                "score": required_number(row["Score"], f"{SCORE_FILE} {metric} Score"),
            }
        )

    return {
        "source_as_of_date": score_source_date(df, warnings),
        "source_as_of_date_note": "The source CSV has no date column."
        if not any(column in df.columns for column in ["Source As Of Date", "As Of Date", "Date"])
        else None,
        "final_score": required_number(final_row["Score"], f"{SCORE_FILE} {FINAL_SCORE_METRIC} Score"),
        "components": components,
    }


def previous_month_value(history: pd.DataFrame, latest: pd.Series, months_back: int) -> dict[str, Any]:
    target_period = latest["_date"].to_period("M") - months_back
    matches = history.loc[history["_date"].dt.to_period("M") == target_period]
    label = "one-month" if months_back == 1 else "three-month"
    if matches.empty:
        return {
            "gold_diversification_score_change": None,
            "allocation_guidance_score_change": None,
            "explanation": f"No valid observation exists for the required {label}-prior calendar month.",
        }

    previous = matches.iloc[-1]
    current_score = number_or_null(latest["Gold Diversification Score"])
    previous_score = number_or_null(previous["Gold Diversification Score"])
    current_allocation = number_or_null(latest["Allocation Guidance Score"])
    previous_allocation = number_or_null(previous["Allocation Guidance Score"])
    if None in (current_score, previous_score, current_allocation, previous_allocation):
        return {
            "gold_diversification_score_change": None,
            "allocation_guidance_score_change": None,
            "explanation": f"A required value is unavailable for the {label} comparison.",
        }

    return {
        "gold_diversification_score_change": current_score - previous_score,
        "allocation_guidance_score_change": current_allocation - previous_allocation,
        "explanation": None,
    }


def read_history() -> tuple[dict[str, Any], dict[str, Any], str]:
    history = require_csv(HISTORY_FILE, HISTORY_COLUMNS)
    history = history.copy()
    history["_date"] = pd.to_datetime(history["Date"], errors="coerce")
    if history["_date"].isna().any():
        raise RequiredSourceError(f"Invalid Date values in {HISTORY_FILE}")
    history["_date"] = history["_date"].dt.normalize()
    if history["_date"].duplicated().any():
        raise RequiredSourceError(f"Duplicate Date values in {HISTORY_FILE}")
    history = history.sort_values("_date").reset_index(drop=True)

    latest = history.iloc[-1]
    period_label = date_string(latest["_date"])
    allocation = {
        "source_as_of_date": None,
        "source_period_label": period_label,
        "allocation_guidance_score": required_number(
            latest["Allocation Guidance Score"], f"{HISTORY_FILE} latest Allocation Guidance Score"
        ),
        "recommendation_confidence": None
        if pd.isna(latest["Recommendation Confidence"])
        else str(latest["Recommendation Confidence"]),
        "best_marginal_step": None if pd.isna(latest["Best Marginal Step"]) else str(latest["Best Marginal Step"]),
        "recommended_strategic_range": None
        if pd.isna(latest["Recommended Strategic Range"])
        else str(latest["Recommended Strategic Range"]),
        "allocation_history_status": None if pd.isna(latest["Status"]) else str(latest["Status"]),
        "allocation_history_alert_level": None
        if pd.isna(latest["Alert Level"])
        else str(latest["Alert Level"]),
    }
    changes = {
        "source_as_of_date": None,
        "source_period_label": period_label,
        "one_month": previous_month_value(history, latest, 1),
        "three_month": previous_month_value(history, latest, 3),
    }
    return allocation, changes, period_label


def read_alert() -> dict[str, Any]:
    text = require_text(ALERT_FILE)
    labels = {"Alert Level:": None, "Diversification Trend:": None}
    remaining_lines = []

    for line in text.splitlines():
        matched = False
        for label in labels:
            if line.startswith(label):
                if labels[label] is not None:
                    raise RequiredSourceError(f"Duplicate '{label}' label in {ALERT_FILE}")
                value = line[len(label):].strip()
                if not value:
                    raise RequiredSourceError(f"Empty '{label}' label in {ALERT_FILE}")
                labels[label] = value
                matched = True
                break
        if not matched:
            remaining_lines.append(line)

    missing_labels = [label for label, value in labels.items() if value is None]
    if missing_labels:
        raise RequiredSourceError(f"Required labels missing from {ALERT_FILE}: {missing_labels}")

    return {
        "source_as_of_date": None,
        "alert_level": labels["Alert Level:"],
        "diversification_trend": labels["Diversification Trend:"],
        "unstructured_context": {
            "source_path": str(ALERT_FILE),
            "remaining_text": "\n".join(remaining_lines),
            "content_type": "unstructured_text_not_numeric_source_of_truth",
        },
    }


def read_market_regime() -> dict[str, Any]:
    if not SPY_DATA_FILE.exists():
        raise RequiredSourceError(f"Required source is missing: {SPY_DATA_FILE}")
    if not REGIME_METHOD_FILE.exists():
        raise RequiredSourceError(f"Required source is missing: {REGIME_METHOD_FILE}")

    try:
        spy_data = pd.read_csv(SPY_DATA_FILE, header=[0, 1], index_col=0)
        close = pd.to_numeric(spy_data[("Close", "SPY")], errors="coerce").dropna()
        close.index = pd.to_datetime(close.index, errors="coerce")
        close = close.loc[~close.index.isna()].sort_index()
    except Exception as error:
        raise RequiredSourceError(f"Required source is malformed: {SPY_DATA_FILE} ({error})") from error

    returns = close.pct_change().dropna()
    if returns.empty:
        raise RequiredSourceError(f"Insufficient valid SPY data to classify market regime: {SPY_DATA_FILE}")

    stress_threshold, strong_threshold = calculate_regime_thresholds(returns)
    latest_return = required_number(returns.iloc[-1], f"latest SPY return from {SPY_DATA_FILE}")
    observation_date = date_string(pd.Timestamp(returns.index[-1]).normalize())

    return {
        "source_as_of_date": observation_date,
        "regime_label": classify_regime(latest_return, stress_threshold, strong_threshold),
        "observation_date": observation_date,
        "spy_return": latest_return,
        "thresholds": {
            "stress_return_threshold": required_number(stress_threshold, "SPY stress threshold"),
            "strong_return_threshold": required_number(strong_threshold, "SPY strong threshold"),
        },
        "methodology_reference": str(REGIME_METHOD_FILE),
        "source_path": str(SPY_DATA_FILE),
    }


def read_regime_summary() -> dict[str, Any]:
    summary = require_csv(REGIME_SUMMARY_FILE, REGIME_SUMMARY_COLUMNS)
    rows = []
    for _, row in summary.iterrows():
        rows.append(
            {
                "regime": None if pd.isna(row["Regime"]) else str(row["Regime"]),
                "spy": number_or_null(row["SPY"]),
                "qqq": number_or_null(row["QQQ"]),
                "gld": number_or_null(row["GLD"]),
                "tlt": number_or_null(row["TLT"]),
                "number_of_days": number_or_null(row["Number of Days"]),
            }
        )
    return {
        "source_as_of_date": None,
        "source_path": str(REGIME_SUMMARY_FILE),
        "rows": rows,
    }


def slugify(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "_" for character in value).strip("_")


def read_methodology_limitations() -> list[dict[str, str]]:
    text = require_text(README_FILE)
    start = text.find("## 14. Limitations")
    end = text.find("## 15.", start + 1)
    if start == -1 or end == -1:
        raise RequiredSourceError(f"Limitations section is missing or malformed in {README_FILE}")

    section = text[start:end]
    limitations = []
    current_title: str | None = None
    paragraphs: list[str] = []

    def append_current() -> None:
        if current_title and paragraphs:
            limitations.append(
                {
                    "id": slugify(current_title),
                    "description": " ".join(paragraphs),
                    "source_path": str(README_FILE),
                }
            )

    for line in section.splitlines()[1:]:
        if line.startswith("### "):
            append_current()
            current_title = line[4:].strip()
            paragraphs = []
        elif current_title and line.strip():
            paragraphs.append(line.strip())
    append_current()

    if not limitations:
        raise RequiredSourceError(f"No limitations were found in {README_FILE}")
    return limitations


def build_packet() -> dict[str, Any]:
    warnings: list[str] = []
    data_quality, ticker_dates, core_market_data_date, all_tracked_market_data_date = read_data_quality(warnings)
    score = read_score(warnings)
    allocation, changes, allocation_history_period_label = read_history()
    if (
        allocation_history_period_label is not None
        and core_market_data_date is not None
        and pd.Timestamp(allocation_history_period_label) > pd.Timestamp(core_market_data_date)
    ):
        warnings.append(
            "allocation_history_period_label is later than core_market_data_as_of_date; "
            "it is a period-end label, not observed data coverage."
        )
    alert = read_alert()
    market_regime = {
        "current": read_market_regime(),
        "regime_summary": read_regime_summary(),
    }

    packet = empty_packet()
    packet["analysis_readiness"] = {
        "status": "needs_review" if warnings else "ready",
        "blocking_issues": [],
        "review_warnings": warnings,
    }
    packet["dates"] = {
        "analysis_as_of_date": None,
        "analysis_as_of_date_note": (
            "No single directly attributable unified analysis date is available: "
            "the score CSV is intrinsically undated and allocation history uses period-end labels."
        ),
        "core_market_data_as_of_date": core_market_data_date,
        "all_tracked_market_data_as_of_date": all_tracked_market_data_date,
        "allocation_history_period_label": allocation_history_period_label,
        "ticker_latest_dates": ticker_dates,
    }
    packet["data_quality"] = data_quality
    packet["gold_diversification_score"] = score
    packet["market_regime"] = market_regime
    packet["allocation_guidance"] = allocation
    packet["alert"] = alert
    packet["recent_score_changes"] = changes
    packet["methodology_limitations"] = read_methodology_limitations()
    return packet


def main() -> None:
    try:
        packet = build_packet()
    except RequiredSourceError as error:
        packet = empty_packet()
        packet["analysis_readiness"]["blocking_issues"] = [str(error)]
        write_packet(packet)
        print(f"Blocked research packet written to {OUTPUT_FILE}: {error}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as error:
        packet = empty_packet()
        packet["analysis_readiness"]["blocking_issues"] = [
            f"Packet generation failed while reading required sources: {type(error).__name__}: {error}"
        ]
        write_packet(packet)
        print(f"Blocked research packet written to {OUTPUT_FILE}: {error}", file=sys.stderr)
        raise SystemExit(1)

    write_packet(packet)
    print(f"Research packet written to {OUTPUT_FILE}")
    print(f"Analysis readiness: {packet['analysis_readiness']['status']}")


if __name__ == "__main__":
    main()
