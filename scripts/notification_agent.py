from pathlib import Path
from datetime import datetime
import platform
import subprocess


OUTPUT = Path(
    "reports/08_agent_ops/notification_log.txt"
)


def write_log(message):

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT,
        "a"
    ) as f:

        f.write(
            "\n====================\n"
        )

        f.write(
            f"{datetime.now()}\n"
        )

        f.write(
            message + "\n"
        )


def mac_notification(message):

    try:

        subprocess.run(
            [
                "osascript",
                "-e",
                f'display notification "{message}" with title "Lobster ETF Agent"'
            ],
            check=True
        )

        return True

    except Exception:

        return False



def main():

    message = (
        "Lobster Auto Refresh completed successfully."
    )


    system = platform.system()


    if system == "Darwin":

        success = mac_notification(
            message
        )

        if success:

            write_log(
                "Mode: macOS notification\n"
                "Status: Sent"
            )

        else:

            write_log(
                "Mode: macOS notification\n"
                "Status: Failed"
            )


    else:

        write_log(
            "Mode: Cloud Environment\n"
            "Status: Logged only"
        )


    print(
        "Notification Agent Completed"
    )


if __name__ == "__main__":
    main()