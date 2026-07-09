from pathlib import Path
from datetime import datetime
import subprocess
import sys

OUT_DIR = Path("reports/08_agent_ops")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_LOG = OUT_DIR / "pipeline_run_log.txt"


def main():
    start_time = datetime.now()

    log_lines = [
        "Lobster Pipeline Run Logger",
        f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Command:",
        "python scripts/run_all.py",
        "",
    ]

    result = subprocess.run(
    [sys.executable, "scripts/run_all.py"],
    capture_output=True,
    text=True,
    )

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    log_lines.append("Pipeline Status:")
    if result.returncode == 0:
        log_lines.append("Passed")
    else:
        log_lines.append("Failed")

    log_lines.append("")
    log_lines.append(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log_lines.append(f"Duration Seconds: {duration:.2f}")

    log_lines.append("")
    log_lines.append("STDOUT:")
    log_lines.append(result.stdout if result.stdout else "No stdout.")

    log_lines.append("")
    log_lines.append("STDERR:")
    log_lines.append(result.stderr if result.stderr else "No stderr.")

    log_text = "\n".join(log_lines)
    OUT_LOG.write_text(log_text)

    print(log_text)
    print(f"\nSaved to {OUT_LOG}")

    if result.returncode != 0:
        raise RuntimeError("Research pipeline failed.")


if __name__ == "__main__":
    main()