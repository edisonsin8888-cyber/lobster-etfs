from pathlib import Path
from datetime import datetime

OUT_DIR = Path("reports/08_agent_ops")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_STATUS = OUT_DIR / "lobster_system_status.txt"

CRITICAL_OUTPUTS = [
    "reports/08_agent_ops/data_update_log.txt",
    "reports/08_agent_ops/data_quality_report.csv",
    "reports/08_agent_ops/data_quality_summary.txt",
    "reports/08_agent_ops/pipeline_run_log.txt",

    "reports/06_score_and_monitor/gold_diversification_score.csv",
    "reports/06_score_and_monitor/diversification_alert.txt",
    "reports/06_score_and_monitor/ai_risk_monitor_report.txt",
    "reports/06_score_and_monitor/allocation_history.csv",
    "reports/06_score_and_monitor/allocation_history_summary.txt",
    "reports/06_score_and_monitor/gold_signal_dashboard.txt",
    "reports/06_score_and_monitor/gold_dashboard_pack.md",
    "reports/06_score_and_monitor/gold_div_score_history.png",
    "reports/06_score_and_monitor/allocation_guidance_history.png",
    "reports/06_score_and_monitor/gld_risk_budget_curve.png",

    "reports/07_lobster_watchlist/etf_watchlist_snapshot.csv",
    "reports/07_lobster_watchlist/etf_watchlist_summary.txt",
    "reports/07_lobster_watchlist/etf_score_table.csv",
    "reports/07_lobster_watchlist/etf_score_summary.txt",
    "reports/07_lobster_watchlist/lobster_dashboard.txt",
    "reports/07_lobster_watchlist/lobster_research_router.txt",
    "reports/07_lobster_watchlist/lobster_weekly_memo.txt",

    "reports/08_growth_sleeve/xlk_vs_spy_summary.csv",
    "reports/08_growth_sleeve/xlk_growth_monitor.txt",
]


def file_status(path):
    file_path = Path(path)

    if not file_path.exists():
        return {
            "path": path,
            "status": "Missing",
            "size": 0,
        }

    size = file_path.stat().st_size

    if size == 0:
        return {
            "path": path,
            "status": "Empty",
            "size": size,
        }

    return {
        "path": path,
        "status": "OK",
        "size": size,
    }


def main():
    results = [file_status(path) for path in CRITICAL_OUTPUTS]

    missing = [r for r in results if r["status"] == "Missing"]
    empty = [r for r in results if r["status"] == "Empty"]
    ok = [r for r in results if r["status"] == "OK"]

    if missing:
        overall_status = "Failed"
    elif empty:
        overall_status = "Warning"
    else:
        overall_status = "Healthy"

    lines = [
        "Lobster System Status Agent",
        f"Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"System Status: {overall_status}",
        f"- OK Files: {len(ok)}",
        f"- Empty Files: {len(empty)}",
        f"- Missing Files: {len(missing)}",
        "",
        "Critical Output Check",
    ]

    for result in results:
        lines.append(
            f"- {result['status']}: {result['path']} "
            f"({result['size']} bytes)"
        )

    if missing:
        lines.append("")
        lines.append("Missing Files")
        for result in missing:
            lines.append(f"- {result['path']}")

    if empty:
        lines.append("")
        lines.append("Empty Files")
        for result in empty:
            lines.append(f"- {result['path']}")

    status_text = "\n".join(lines)
    OUT_STATUS.write_text(status_text)

    print(status_text)
    print(f"\nSaved to {OUT_STATUS}")

    if overall_status == "Failed":
        raise RuntimeError("System status check failed.")


if __name__ == "__main__":
    main()