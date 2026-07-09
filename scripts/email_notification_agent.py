import os
import smtplib

from pathlib import Path
from email.mime.text import MIMEText
from datetime import datetime


SUMMARY_FILE = Path(
    "reports/08_agent_ops/final_agent_summary.txt"
)


def load_summary():

    if SUMMARY_FILE.exists():

        return SUMMARY_FILE.read_text()

    return "No summary generated."


def send_email(content):

    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_PASSWORD"]
    receiver = os.environ["EMAIL_RECEIVER"]

    msg = MIMEText(
        content,
        "plain",
        "utf-8"
    )

    msg["Subject"] = (
        "Lobster ETF Research Update"
    )

    msg["From"] = sender
    msg["To"] = receiver


    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            sender,
            password
        )

        server.send_message(
            msg
        )


def main():

    summary = load_summary()


    email_content = f"""
Lobster ETF Research Agent

Run Time:
{datetime.now()}

====================

{summary}

====================

Generated automatically by Lobster.
"""


    send_email(
        email_content
    )


    print(
        "Email Notification Sent"
    )


if __name__ == "__main__":
    main()