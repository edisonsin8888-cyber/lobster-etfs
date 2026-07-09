from pathlib import Path
from datetime import datetime
import subprocess

OUT_DIR = Path("reports/08_agent_ops")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL_SUMMARY = OUT_DIR / "final_agent_summary.txt"
OUT_LOG = OUT_DIR / "notification_log.txt"


def read_overall_status():
    if not FINAL_SUMMARY.exists():
        return "Unknown", "final_agent_summary.txt not found"

    text = FINAL_SUMMARY.read_text()

    for line in text.splitlines():
        if line.startswith("Overall Auto Refresh Status:"):
            status = line.split(":", 1)[1].strip()
            return status, text

    return "Unknown", text


def send_macos_notification(title, message):
    safe_title = title.replace('"', "'")
    safe_message = message.replace('"', "'")

    command = [
        "osascript",
        "-e",
        f'display notification "{safe_message}" with title "{safe_title}"',
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    return result


def main():
    status, summary_text = read_overall_status()

    if status == "Passed":
        title = "Lobster ETF Agent"
        message = "Auto refresh completed successfully."
    elif status == "Failed":
        title = "Lobster ETF Agent"
        message = "Auto refresh failed. Please check the logs."
    else:
        title = "Lobster ETF Agent"
        message = "Auto refresh status is unknown."

    result = send_macos_notification(title, message)

    log_lines = [
        "Lobster Notification Agent",
        f"Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Detected Status: {status}",
        f"Notification Title: {title}",
        f"Notification Message: {message}",
        "",
        "Notification Result",
        f"- Return Code: {result.returncode}",
        f"- STDOUT: {result.stdout if result.stdout else 'No stdout.'}",
        f"- STDERR: {result.stderr if result.stderr else 'No stderr.'}",
    ]

    log_text = "\n".join(log_lines)
    OUT_LOG.write_text(log_text)

    print(log_text)
    print(f"\nSaved to {OUT_LOG}")

    if result.returncode != 0:
        raise RuntimeError("Notification failed.")


if __name__ == "__main__":
    main()