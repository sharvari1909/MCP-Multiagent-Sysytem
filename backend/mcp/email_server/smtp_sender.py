import base64
import json
import smtplib
import urllib.error
import urllib.request
from email.utils import formataddr
from email.message import EmailMessage
from config import settings


def send_smtp_email(to_email, subject, body, attachment_path=None, html_body=None):
    smtp_user = settings.SMTP_USERNAME or settings.EMAIL_USER
    smtp_password = settings.SMTP_PASSWORD or settings.EMAIL_PASSWORD
    from_email = settings.SMTP_FROM or settings.EMAIL_USER or smtp_user
    from_name = settings.SMTP_FROM_NAME
    from_header = formataddr((from_name, from_email)) if from_name else from_email
    provider_attempts = []

    if not smtp_user or not smtp_password:
        smtp_result = {
            "tool": "Email MCP",
            "status": "skipped",
            "to": to_email,
            "subject": subject,
            "note": "SMTP credentials are not configured",
        }
        provider_attempts.append(smtp_result)
        return _send_brevo_email(
            to_email=to_email,
            subject=subject,
            body=body,
            attachment_path=attachment_path,
            html_body=html_body,
            provider_attempts=provider_attempts,
        )

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

    attempts = []
    last_error = None

    for port in _candidate_ports(settings.SMTP_PORT):
        try:
            _send_with_port(
                host=settings.SMTP_HOST,
                port=port,
                smtp_user=smtp_user,
                smtp_password=smtp_password,
                msg=msg,
            )
            return {
                "tool": "Email MCP",
                "status": "sent",
                "provider": "smtp",
                "to": to_email,
                "subject": subject,
                "smtp_host": settings.SMTP_HOST,
                "smtp_port": port,
                "attempts": attempts + [{"port": port, "status": "sent"}],
            }
        except Exception as e:
            last_error = e
            attempts.append({
                "port": port,
                "status": "failed",
                "error": str(e),
            })

    smtp_result = {
        "tool": "Email MCP",
        "status": "failed",
        "provider": "smtp",
        "to": to_email,
        "subject": subject,
        "smtp_host": settings.SMTP_HOST,
        "error": str(last_error) if last_error else "SMTP delivery failed",
        "attempts": attempts,
    }
    provider_attempts.append(smtp_result)
    return _send_brevo_email(
        to_email=to_email,
        subject=subject,
        body=body,
        attachment_path=attachment_path,
        html_body=html_body,
        provider_attempts=provider_attempts,
    )


def _send_brevo_email(to_email, subject, body, attachment_path=None, html_body=None, provider_attempts=None):
    provider_attempts = provider_attempts or []
    api_key = settings.BREVO_API_KEY

    if not api_key:
        last_attempt = provider_attempts[-1] if provider_attempts else {}
        return {
            **last_attempt,
            "provider_attempts": provider_attempts,
            "note": "SMTP failed and BREVO_API_KEY is not configured",
        }

    sender_email = settings.BREVO_SENDER_EMAIL or settings.SMTP_FROM or settings.EMAIL_USER
    sender_name = settings.BREVO_SENDER_NAME or settings.SMTP_FROM_NAME or "Anvenssa Workflow System"

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body,
    }

    if html_body:
        payload["htmlContent"] = html_body

    if attachment_path:
        with open(attachment_path, "rb") as file:
            payload["attachment"] = [{
                "name": attachment_path.split("/")[-1].split("\\")[-1],
                "content": base64.b64encode(file.read()).decode("ascii"),
            }]

    request = urllib.request.Request(
        url="https://api.brevo.com/v3/smtp/email",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            response_body = response.read().decode("utf-8")
            brevo_response = json.loads(response_body or "{}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        provider_attempts.append({
            "provider": "brevo",
            "status": "failed",
            "http_status": e.code,
            "error": error_body or str(e),
        })
        return {
            "tool": "Email MCP",
            "status": "failed",
            "provider": "brevo",
            "to": to_email,
            "subject": subject,
            "error": error_body or str(e),
            "provider_attempts": provider_attempts,
        }
    except Exception as e:
        provider_attempts.append({
            "provider": "brevo",
            "status": "failed",
            "error": str(e),
        })
        return {
            "tool": "Email MCP",
            "status": "failed",
            "provider": "brevo",
            "to": to_email,
            "subject": subject,
            "error": str(e),
            "provider_attempts": provider_attempts,
        }

    provider_attempts.append({
        "provider": "brevo",
        "status": "sent",
        "message_id": brevo_response.get("messageId"),
    })
    return {
        "tool": "Email MCP",
        "status": "sent",
        "provider": "brevo",
        "to": to_email,
        "subject": subject,
        "message_id": brevo_response.get("messageId"),
        "provider_attempts": provider_attempts,
    }

def _candidate_ports(configured_port):
    ports = [int(configured_port), 587, 465, 2525]
    unique_ports = []
    for port in ports:
        if port not in unique_ports:
            unique_ports.append(port)
    return unique_ports


def _send_with_port(host, port, smtp_user, smtp_password, msg):
    if port == 465:
        server_context = smtplib.SMTP_SSL(host, port, timeout=10)
    else:
        server_context = smtplib.SMTP(host, port, timeout=10)

    with server_context as server:
        if port != 465:
            server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
