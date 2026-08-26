import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import quote

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# SMTP configuration 
# ---------------------------------------------------------------------------
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)

# Base URL used to build the Approve/Reject links in the notification email.
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")

# ===========================================================================
# Registration notification email content
# ===========================================================================
REGISTRATION_EMAIL_RECIPIENTS = [
    # test recipient for development
    "chen.chen@ga4gh.org",
    "chen.chen@ga4gh.org",
]

REGISTRATION_EMAIL_TITLE = "New Standard DOI Registration - {batch_id}"

REGISTRATION_EMAIL_BODY = """
A new standard DOI batch has been registered and is awaiting review.

Batch ID: {batch_id}

The CSV file is attached. Choose Approve or Reject below.
"""
# ===========================================================================


def _send_email(recipients, subject, html_body, attachment_filename=None, attachment_bytes=None):
    message = MIMEMultipart()
    message["From"] = FROM_EMAIL
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))

    if attachment_filename and attachment_bytes is not None:
        attachment = MIMEApplication(attachment_bytes, Name=attachment_filename)
        attachment["Content-Disposition"] = f'attachment; filename="{attachment_filename}"'
        message.attach(attachment)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        if SMTP_USERNAME:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, recipients, message.as_string())


def _approve_reject_buttons(batch_id: str, approver_email: str) -> str:
    # approver_email is passed through the Approve link to identify the reviewer.
    approve_url = f"{APP_BASE_URL}/standards/approve/{batch_id}?approver_email={quote(approver_email)}"
    reject_url = f"{APP_BASE_URL}/standards/reject/{batch_id}"
    button_style = (
        "display:inline-block;padding:10px 20px;margin-right:12px;"
        "color:#fff;text-decoration:none;border-radius:4px;font-family:sans-serif;"
    )
    return f"""
    <div style="margin-top:24px;">
      <a href="{approve_url}" style="{button_style}background:#17ca35;">Approve</a>
      <a href="{reject_url}" style="{button_style}background:#dc2626;">Reject</a>
    </div>
    """


def send_registration_notification(batch_id: str, csv_content: str) -> None:
    # Sends one email per recipient, each with its own Approve link carrying
    # that recipient's address as approver_email.
    subject = REGISTRATION_EMAIL_TITLE.format(batch_id=batch_id)
    body_text = REGISTRATION_EMAIL_BODY.format(batch_id=batch_id)

    for recipient in REGISTRATION_EMAIL_RECIPIENTS:
        html_body = (
            f"<pre style='font-family:sans-serif;white-space:pre-wrap;'>{body_text}</pre>"
            f"{_approve_reject_buttons(batch_id, recipient)}"
        )
        _send_email(
            recipients=[recipient],
            subject=subject,
            html_body=html_body,
            attachment_filename=f"{batch_id}.csv",
            attachment_bytes=csv_content.encode("utf-8"),
        )


def send_rejection_email(to_email: str, batch_id: str) -> None:
    subject = f"DOI Submission Rejected - {batch_id}"
    html_body = f"<p>Your DOI submission (batch {batch_id}) has been rejected.</p>"
    _send_email(recipients=[to_email], subject=subject, html_body=html_body)


def send_success_email(to_email: str, batch_id: str) -> None:
    subject = f"DOI Submission Approved - {batch_id}"
    html_body = f"<p>Your DOI submission (batch {batch_id}) has been approved.</p>"
    _send_email(recipients=[to_email], subject=subject, html_body=html_body)


def send_submission_failed_email(depositor_email: str, approver_email: str, batch_id: str, details: str = "") -> None:
    subject = f"DOI Submission Failed - {batch_id}"
    html_body = f"<p>Batch {batch_id} was approved and submitted to Crossref, but Crossref failed the submission.</p>"
    if details:
        html_body += f"<pre style='white-space:pre-wrap;'>{details}</pre>"

    recipients = {email for email in (depositor_email, approver_email) if email}
    for recipient in recipients:
        _send_email(recipients=[recipient], subject=subject, html_body=html_body)
