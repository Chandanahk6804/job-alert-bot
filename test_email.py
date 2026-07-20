"""Standalone test: sends one fake job email so you can verify SMTP setup
without running the actual scrapers. Run this BEFORE relying on main.py.

Usage:
    export SMTP_USER="youraddress@gmail.com"
    export SMTP_PASS="your16charapppassword"
    export TO_EMAIL="youraddress@gmail.com"
    python test_email.py
"""
from notifier import send_email

fake_job = [{
    "title": "Test SDE Role - Fresher",
    "company": "Job Alert Bot (test)",
    "url": "https://example.com/this-is-a-test",
}]

send_email(fake_job)
print("If you see this with no error above, check your inbox (and spam folder).")
