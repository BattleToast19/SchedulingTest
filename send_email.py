"""
Send an email from a Gmail account to itself (or any recipient) via SMTP.

Usage:
    python send_email.py              # sends the daily test email
    python send_email.py --dry-run    # prints what would be sent, sends nothing

Every run (success or failure) is appended to send_email.log next to this file.
"""
import argparse
import os
import smtplib
import ssl
import sys
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")  # works no matter which folder the scheduler runs from

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO") or GMAIL_ADDRESS

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL
LOG_FILE = BASE_DIR / "send_email.log"


def log(line: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{stamp}] {line}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


def require_config() -> None:
    missing = [
        name
        for name, val in (
            ("GMAIL_ADDRESS", GMAIL_ADDRESS),
            ("GMAIL_APP_PASSWORD", GMAIL_APP_PASSWORD),
        )
        if not val
    ]
    if missing:
        log(f"ERROR: missing in .env: {', '.join(missing)}")
        sys.exit(1)


def build_message() -> EmailMessage:
    now = datetime.now()
    msg = EmailMessage()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = EMAIL_TO
    msg["Subject"] = f"Daily agent check-in {now:%Y-%m-%d}"
    msg.set_content(
        "This is your scheduled daily email.\n\n"
        f"Sent at: {now:%Y-%m-%d %H:%M:%S} (local time of the machine running the agent)\n"
    )
    return msg


def send(msg: EmailMessage) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=30) as smtp:
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD.replace(" ", ""))
        smtp.send_message(msg)


def main() -> None:
    parser = argparse.ArgumentParser(description="Send the daily Gmail self-email.")
    parser.add_argument("--dry-run", action="store_true", help="print the email, do not send")
    args = parser.parse_args()

    require_config()
    msg = build_message()

    if args.dry_run:
        log(f"[dry-run] Would send to {msg['To']} | Subject: {msg['Subject']}")
        return

    try:
        send(msg)
    except smtplib.SMTPAuthenticationError as e:
        log(f"FAILED: authentication error ({e.smtp_code}). Check GMAIL_ADDRESS / app password.")
        sys.exit(1)
    except Exception as e:  # network down, timeout, etc.
        log(f"FAILED: {type(e).__name__}: {e}")
        sys.exit(1)

    log(f"SENT to {msg['To']} | Subject: {msg['Subject']}")


if __name__ == "__main__":
    main()
