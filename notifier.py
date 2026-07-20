"""Send a digest email of new matching jobs via SMTP (Gmail app password or any SMTP provider)."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(jobs: list[dict]):
    if not jobs:
        print("No new matching jobs — skipping email.")
        return

    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ["SMTP_USER"]          # your sending email address
    smtp_pass = os.environ["SMTP_PASS"]          # Gmail app password (not your normal password)
    to_email = os.environ.get("TO_EMAIL", smtp_user)  # defaults to sending to yourself

    subject = f"{len(jobs)} new fresher job(s) matching your search"

    lines = []
    for j in jobs:
        company = j.get("company") or "Unknown company"
        lines.append(f"• {j['title']} — {company}\n  {j['url']}\n")
    body = "\n".join(lines)

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())

    print(f"Sent email with {len(jobs)} job(s) to {to_email}")
