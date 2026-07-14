from pathlib import Path
from datetime import datetime
import subprocess
import sys

OUT_DIR = Path("reports/08_agent_ops")
OUT_DIR.mkdir(parents=True, exist_ok=True)

AUTO_LOG = OUT_DIR / "auto_refresh_log.txt"
FINAL_SUMMARY = OUT_DIR / "final_agent_summary.txt"

AGENT_STEPS = [
    ("Data Update Agent", "scripts/data_update_agent.py"),
    ("Data Quality Check Agent", "scripts/data_quality_check.py"),
    ("Pipeline Run Logger", "scripts/pipeline_run_logger.py"),
    ("System Status Agent", "scripts/lobster_system_status.py"),
    ("Research Task Generator", "scripts/lobster_research_tasks.py"),
    ("Notification Agent", "scripts/notification_agent.py"),
]


def run_step(name, script):
    start = datetime.now()

    result = subprocess.run(
    [sys.executable, script],
    capture_output=True,
    text=True,
    )

    end = datetime.now()
    duration = (end - start).total_seconds()

    status = "Passed" if result.returncode == 0 else "Failed"

    return {
        "name": name,
        "script": script,
        "status": status,
        "duration": duration,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def read_file(path):
    file_path = Path(path)
    if file_path.exists():
        return file_path.read_text()
    return "File not found."


def main():
    start_time = datetime.now()

    log_lines = [
        "Lobster Auto Refresh Agent",
        f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    results = []

    for name, script in AGENT_STEPS:
        print(f"\nRunning: {name}")
        result = run_step(name, script)
        results.append(result)

        print(f"Status: {result['status']}")
        print(f"Duration: {result['duration']:.2f} seconds")

        log_lines.append(f"Step: {name}")
        log_lines.append(f"- Script: {script}")
        log_lines.append(f"- Status: {result['status']}")
        log_lines.append(f"- Duration Seconds: {result['duration']:.2f}")
        log_lines.append("")

        log_lines.append("STDOUT:")
        log_lines.append(result["stdout"] if result["stdout"] else "No stdout.")
        log_lines.append("")

        log_lines.append("STDERR:")
        log_lines.append(result["stderr"] if result["stderr"] else "No stderr.")
        log_lines.append("")
        log_lines.append("-" * 60)
        log_lines.append("")

        if result["returncode"] != 0:
            break

    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    failed_steps = [r for r in results if r["status"] == "Failed"]

    if failed_steps:
        overall_status = "Failed"
    else:
        overall_status = "Passed"

    log_lines.append("Final Auto Refresh Status")
    log_lines.append(f"- Overall Status: {overall_status}")
    log_lines.append(f"- Total Duration Seconds: {total_duration:.2f}")
    log_lines.append(f"- Completed Steps: {len(results)} / {len(AGENT_STEPS)}")
    log_lines.append(f"- Failed Steps: {len(failed_steps)}")

    AUTO_LOG.write_text("\n".join(log_lines))

    system_status = read_file("reports/08_agent_ops/lobster_system_status.txt")
    research_tasks = read_file("reports/08_agent_ops/lobster_research_tasks.txt")
    data_quality = read_file("reports/08_agent_ops/data_quality_summary.txt")

    summary_lines = [
        "Lobster Final Agent Summary",
        f"Run Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Overall Auto Refresh Status: {overall_status}",
        f"Total Duration Seconds: {total_duration:.2f}",
        "",
        "1. Agent Step Results",
    ]

    for result in results:
        summary_lines.append(
            f"- {result['name']}: {result['status']} "
            f"({result['duration']:.2f} seconds)"
        )

    summary_lines.extend(
        [
            "",
            "2. Data Quality Summary",
            data_quality,
            "",
            "3. System Status Summary",
            system_status,
            "",
            "4. Research Tasks",
            research_tasks,
            "",
            "5. Final Interpretation",
        ]
    )

    if overall_status == "Passed":
        summary_lines.append(
            "The Lobster automated ETF research agent completed all steps successfully. "
            "The system updated data, validated data quality, refreshed the full research pipeline, "
            "checked system outputs, and generated the next research tasks."
        )
    else:
        summary_lines.append(
            "The Lobster automated ETF research agent did not complete all steps successfully. "
            "Review the auto refresh log to identify the failed step."
        )

    FINAL_SUMMARY.write_text("\n".join(summary_lines))

    print("\n=== Final Auto Refresh Status ===")
    print(f"Overall Status: {overall_status}")
    print(f"Completed Steps: {len(results)} / {len(AGENT_STEPS)}")
    print(f"Saved to {AUTO_LOG}")
    print(f"Saved to {FINAL_SUMMARY}")

    if overall_status == "Failed":
        raise RuntimeError("Auto refresh failed.")


if __name__ == "__main__":
    main()