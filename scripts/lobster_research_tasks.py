from pathlib import Path
from datetime import datetime
import pandas as pd

BASE_GOLD = Path("reports/06_score_and_monitor")
BASE_LOBSTER = Path("reports/07_lobster_watchlist")
BASE_GROWTH = Path("reports/08_growth_sleeve")
OUT_DIR = Path("reports/08_agent_ops")

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_TASKS = OUT_DIR / "lobster_research_tasks.txt"

SCORE_FILE = BASE_LOBSTER / "etf_score_table.csv"
ROUTER_FILE = BASE_LOBSTER / "lobster_research_router.txt"
GOLD_DASHBOARD = BASE_GOLD / "gold_signal_dashboard.txt"
XLK_SUMMARY = BASE_GROWTH / "xlk_vs_spy_summary.csv"


def read_line(path, prefix):
    if not path.exists():
        return "N/A"

    for line in path.read_text().splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()

    return "N/A"


def main():
    scores = pd.read_csv(SCORE_FILE)
    xlk = pd.read_csv(XLK_SUMMARY).iloc[0]

    top_score = scores.iloc[0]
    bottom_score = scores.iloc[-1]

    router_etf = read_line(ROUTER_FILE, "- ETF:")
    router_reason = read_line(ROUTER_FILE, "- Router Reason:")
    router_score = read_line(ROUTER_FILE, "- Router v2 Score:")

    gold_score = read_line(GOLD_DASHBOARD, "- Gold Diversification Score:")
    gold_status = read_line(GOLD_DASHBOARD, "- Score Status:")
    gold_alert = read_line(GOLD_DASHBOARD, "- Alert Level:")
    gold_stance = read_line(GOLD_DASHBOARD, "- Allocation Stance:")
    gold_range = read_line(GOLD_DASHBOARD, "- Recommended Strategic Range:")

    tasks = []

    tasks.append(
        {
            "priority": "Priority 1",
            "title": f"Continue monitoring {router_etf} as the active router candidate",
            "reason": f"Router v2 selected {router_etf}. Reason: {router_reason}. Router score: {router_score}.",
        }
    )

    tasks.append(
        {
            "priority": "Priority 2",
            "title": "Maintain GLD defensive sleeve review",
            "reason": (
                f"Gold Engine status is {gold_status}, alert level is {gold_alert}, "
                f"allocation stance is {gold_stance}, and recommended range is {gold_range}. "
                f"Gold Diversification Score: {gold_score}."
            ),
        }
    )

    tasks.append(
        {
            "priority": "Priority 3",
            "title": "Track XLK growth sleeve risk",
            "reason": (
                f"XLK Growth Sleeve Score is {xlk['Growth Sleeve Score']:.2f}/100. "
                f"Risk flag: {xlk['Growth Sleeve Risk Flag']}. "
                f"Tactical stance: {xlk['Tactical Growth Stance']}. "
                f"XLK 3M excess return vs SPY: {xlk['XLK 3M Excess Return']:.2%}."
            ),
        }
    )

    tasks.append(
        {
            "priority": "Priority 4",
            "title": f"Review strongest ETF score candidate: {top_score['ETF']}",
            "reason": (
                f"{top_score['ETF']} has the highest Final ETF Score "
                f"at {top_score['Final ETF Score']:.2f}/100 with stance "
                f"{top_score['ETF Stance']}."
            ),
        }
    )

    tasks.append(
        {
            "priority": "Priority 5",
            "title": f"Review weakest ETF score candidate: {bottom_score['ETF']}",
            "reason": (
                f"{bottom_score['ETF']} has the lowest Final ETF Score "
                f"at {bottom_score['Final ETF Score']:.2f}/100 with stance "
                f"{bottom_score['ETF Stance']}."
            ),
        }
    )

    if router_etf == "GLD":
        next_extension = (
            "If GLD remains the active router candidate, keep the Gold Engine as the completed "
            "defensive module and consider building a TLT rate-sensitive defensive module next."
        )
    elif router_etf == "XLK":
        next_extension = (
            "If XLK becomes the active router candidate, upgrade the XLK Growth Monitor into a "
            "full growth-sleeve deep-dive module."
        )
    else:
        next_extension = (
            f"If {router_etf} remains highly ranked, consider creating a new sleeve-specific "
            f"deep-dive module for {router_etf}."
        )

    lines = [
        "Lobster Research Task Generator",
        f"Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "1. Current Router Decision",
        f"- Active Candidate: {router_etf}",
        f"- Router v2 Score: {router_score}",
        f"- Router Reason: {router_reason}",
        "",
        "2. Generated Research Tasks",
    ]

    for task in tasks:
        lines.append("")
        lines.append(f"{task['priority']}: {task['title']}")
        lines.append(f"- Reason: {task['reason']}")

    lines.extend(
        [
            "",
            "3. Suggested System Extension",
            next_extension,
            "",
            "4. Research Operations Interpretation",
            (
                "These tasks convert the system's quantitative outputs into a practical research "
                "workflow. The goal is not to generate automatic trading decisions, but to identify "
                "where human research attention should go next."
            ),
        ]
    )

    task_text = "\n".join(lines)
    OUT_TASKS.write_text(task_text)

    print(task_text)
    print(f"\nSaved to {OUT_TASKS}")


if __name__ == "__main__":
    main()