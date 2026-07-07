import smtplib
from email.message import EmailMessage
from config import settings


def send_smtp_email(to_email, subject, body, attachment_path=None, html_body=None):
    if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
        return {
            "tool": "Email MCP",
            "status": "skipped",
            "to": to_email,
            "subject": subject,
            "note": "SMTP credentials are not configured",
        }

    msg = EmailMessage()
    msg["From"] = settings.EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    if attachment_path:
        with open(attachment_path, "rb") as f:
            data = f.read()

        filename = attachment_path.split("/")[-1].split("\\")[-1]

        msg.add_attachment(
            data,
            maintype="application",
            subtype="pdf",
            filename=filename,
        )

    if settings.SMTP_PORT == 465:
        server_context = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
    else:
        server_context = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)

    with server_context as server:
        if settings.SMTP_PORT != 465:
            server.starttls()
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.send_message(msg)

    return {
        "tool": "Email MCP",
        "status": "sent",
        "to": to_email,
        "subject": subject,
    }
