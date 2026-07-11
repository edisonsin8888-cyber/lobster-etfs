import subprocess
import sys
from pathlib import Path
import pandas as pd

from gold_utils import score_status, allocation_stance

PIPELINE = [

    ("Data Quality Check", "scripts/data_quality_check.py"),

    ("Market Regime Analysis", "scripts/regime_analysis.py"),

    ("Gold Diversification Score", "scripts/gold_diversification_score.py"),

    ("Diversification Alert", "scripts/diversification_alert.py"),

    ("AI Risk Monitor", "scripts/ai_risk_monitor.py"),

    ("Allocation History Tracker", "scripts/allocation_history_tracker.py"),

    ("AI-Readable Research Packet", "scripts/generate_research_packet.py"),


    # Gold Research Layer

    ("Gold Signal Dashboard", "scripts/gold_signal_dashboard.py"),

    ("Gold Dashboard Charts", "scripts/gold_dashboard_charts.py"),

    ("Gold Dashboard Pack", "scripts/gold_dashboard_pack.py"),


    # ETF Monitoring Layer

    ("ETF Watchlist Monitor", "scripts/etf_watchlist_monitor.py"),

    ("ETF Score Engine", "scripts/etf_score_engine.py"),


    # Lobster Research Agent Layer

    ("Lobster Dashboard", "scripts/lobster_dashboard.py"),

    ("Lobster Research Router", "scripts/lobster_research_router.py"),

    ("XLK Growth Monitor", "scripts/xlk_growth_monitor.py"),

    ("Lobster Weekly Memo", "scripts/lobster_weekly_memo.py"),


    # Interpretation Layer

    (
        "Metric Interpretation Engine",
        "scripts/metric_interpretation_engine.py"
    ),


    # AI Analyst Layer

    (
        "AI Portfolio Commentary",
        "scripts/ai_portfolio_commentary.py"
    ),


    # Web Layer

    (
        "Web Dashboard Generator",
        "scripts/generate_web_dashboard.py"
    ),
]

EXPECTED_OUTPUTS = [
    "reports/06_score_and_monitor/gold_diversification_score.csv",
    "reports/06_score_and_monitor/diversification_alert.txt",
    "reports/06_score_and_monitor/ai_risk_monitor_report.txt",
    "reports/weekly_reports/gold_weekly_memo.txt",
    "reports/06_score_and_monitor/allocation_history.csv",
    "reports/06_score_and_monitor/allocation_history_summary.txt",
    "reports/07_ai_research/research_packet.json",
    "reports/06_score_and_monitor/gold_signal_dashboard.txt",
    "reports/06_score_and_monitor/gold_div_score_history.png",
    "reports/06_score_and_monitor/allocation_guidance_history.png",
    "reports/06_score_and_monitor/gld_risk_budget_curve.png",
    "reports/06_score_and_monitor/gold_dashboard_pack.md",
    "reports/07_lobster_watchlist/etf_watchlist_snapshot.csv",
    "reports/07_lobster_watchlist/etf_watchlist_summary.txt",
    "reports/07_lobster_watchlist/etf_score_table.csv",
    "reports/07_lobster_watchlist/etf_score_summary.txt",
    "reports/07_lobster_watchlist/lobster_dashboard.txt",
    "reports/07_lobster_watchlist/lobster_research_router.txt",
    "reports/08_growth_sleeve/xlk_vs_spy_summary.csv",
    "reports/08_growth_sleeve/xlk_growth_monitor.txt",
    "reports/07_lobster_watchlist/lobster_weekly_memo.txt",
    "reports/08_agent_ops/metric_interpretation.txt",
    "reports/08_agent_ops/ai_portfolio_commentary.txt",
    "docs/dashboard.html",
]

BASE = Path("reports/06_score_and_monitor")
SCORE_FILE = BASE / "gold_diversification_score.csv"
ALERT_FILE = BASE / "diversification_alert.txt"
HISTORY_FILE = BASE / "allocation_history.csv"


def run_task(name, script):
    print(f"\nRunning: {name}")
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError(f"{name} failed with return code {result.returncode}.")

    print(f"Completed: {name}")


def check_outputs(paths):
    print("\n=== Pipeline Output Check ===")
    missing = []

    for path in paths:
        if Path(path).exists():
            print(f"OK: {path}")
        else:
            print(f"MISSING: {path}")
            missing.append(path)

    if missing:
        raise FileNotFoundError("Some pipeline outputs are missing.")


def read_line(path, prefix):
    for line in Path(path).read_text().splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return "N/A"


def latest_snapshot():
    score_df = pd.read_csv(SCORE_FILE)
    history = pd.read_csv(HISTORY_FILE)

    final_score = score_df.loc[
        score_df["Metric"] == "Final Gold Diversification Score",
        "Score"
    ].iloc[0]

    latest = history.iloc[-1]
    alert = read_line(ALERT_FILE, "Alert Level:")
    allocation_score = latest["Allocation Guidance Score"]

    print("\n=== Latest Research Snapshot ===")
    print(f"Gold Diversification Score: {final_score:.2f}/100")
    print(f"Score Status: {score_status(final_score)}")
    print(f"Alert Level: {alert}")
    print(f"Allocation Guidance Score: {allocation_score:.2f}/100")
    print(f"Allocation Stance: {allocation_stance(allocation_score)}")
    print(f"Recommendation Confidence: {latest['Recommendation Confidence']}")
    print(f"Best Marginal Step: {latest['Best Marginal Step']}")
    print(f"Recommended Strategic Range: {latest['Recommended Strategic Range']}")


def main():
    for name, script in PIPELINE:
        run_task(name, script)

    check_outputs(EXPECTED_OUTPUTS)
    latest_snapshot()

    print("\nAll core reports refreshed successfully.")


if __name__ == "__main__":
    main()
