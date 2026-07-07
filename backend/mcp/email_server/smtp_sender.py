import smtplib
from email.utils import formataddr
from email.message import EmailMessage
from config import settings


def send_smtp_email(to_email, subject, body, attachment_path=None, html_body=None):
    smtp_user = settings.SMTP_USERNAME or settings.EMAIL_USER
    smtp_password = settings.SMTP_PASSWORD or settings.EMAIL_PASSWORD
    from_email = settings.SMTP_FROM or settings.EMAIL_USER or smtp_user
    from_name = settings.SMTP_FROM_NAME
    from_header = formataddr((from_name, from_email)) if from_name else from_email

    if not smtp_user or not smtp_password:
        return {
            "tool": "Email MCP",
            "status": "skipped",
            "to": to_email,
            "subject": subject,
            "note": "SMTP credentials are not configured",
        }

    msg = EmailMessage()
    msg["From"] = from_header
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
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

    return {
        "tool": "Email MCP",
        "status": "sent",
        "to": to_email,
        "subject": subject,
    }
