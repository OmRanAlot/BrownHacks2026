import json
import os
import ssl
import smtplib
from dotenv import load_dotenv, find_dotenv
from email.message import EmailMessage
from pathlib import Path

load_dotenv(find_dotenv())

EMAIL_JSON_PATH = Path("inventory_status_email.json")


def load_email_payload(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Email payload JSON not found: {path.resolve()}")

    payload = json.loads(path.read_text(encoding="utf-8"))

    # Minimal validation
    if "subject" not in payload or "body_text" not in payload:
        raise ValueError("Email JSON must contain 'subject' and 'body_text' fields.")

    return payload


def send_email_smtp(
    *,
    smtp_host: str,
    smtp_port: int,
    username: str,
    app_password: str,
    sender_email: str,
    to_emails: list[str],
    subject: str,
    body_text: str,
) -> None:
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = ", ".join(to_emails)
    msg["Subject"] = subject
    msg.set_content(body_text)

    context = ssl.create_default_context()

    # Gmail SMTP supports STARTTLS on 587
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(username, app_password)
        server.send_message(msg)


def parse_recipients(env_value: str) -> list[str]:
    # Accept comma-separated list
    emails = [e.strip() for e in env_value.split(",") if e.strip()]
    if not emails:
        raise ValueError("No recipient emails provided in DEMO_TO_EMAILS.")
    return emails


def main():
    # --- Required env vars ---
    # For Gmail demo:
    # DEMO_SMTP_HOST=smtp.gmail.com
    # DEMO_SMTP_PORT=587
    # DEMO_SMTP_USERNAME=yourgmail@gmail.com
    # DEMO_SMTP_APP_PASSWORD=xxxx xxxx xxxx xxxx   (Google App Password)
    # DEMO_FROM_EMAIL=yourgmail@gmail.com
    # DEMO_TO_EMAILS=friend1@gmail.com,friend2@gmail.com

    smtp_host = os.getenv("DEMO_SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("DEMO_SMTP_PORT", "587"))

    username = os.getenv("DEMO_SMTP_USERNAME", "")
    app_password = os.getenv("DEMO_SMTP_APP_PASSWORD", "")
    sender_email = os.getenv("DEMO_FROM_EMAIL", "")

    to_env = os.getenv("DEMO_TO_EMAILS", "")
    if not all([username, app_password, sender_email, to_env]):
        raise EnvironmentError(
            "Missing env vars. Set: DEMO_SMTP_USERNAME, DEMO_SMTP_APP_PASSWORD, DEMO_FROM_EMAIL, DEMO_TO_EMAILS "
            "(and optionally DEMO_SMTP_HOST, DEMO_SMTP_PORT)."
        )

    to_emails = parse_recipients(to_env)

    payload = load_email_payload(EMAIL_JSON_PATH)
    subject = payload["subject"]
    body_text = payload["body_text"]

    send_email_smtp(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        username=username,
        app_password=app_password,
        sender_email=sender_email,
        to_emails=to_emails,
        subject=subject,
        body_text=body_text,
    )

    print(f"Sent demo email to: {', '.join(to_emails)}")


if __name__ == "__main__":
    main()
