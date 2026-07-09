import smtplib
import base64
import json
import urllib.request
import urllib.error
from email.utils import formataddr
from email.message import EmailMessage
from config import settings


def send_resend_email(to_email, subject, body, attachment_path=None, html_body=None):
    api_key = settings.RESEND_API_KEY
    from_email = settings.SMTP_FROM or settings.EMAIL_USER or "onboarding@resend.dev"
    from_name = settings.SMTP_FROM_NAME or "Anvenssa Workflow System"
    from_header = f"{from_name} <{from_email}>" if "@" in from_email else from_email
    if "onboarding@resend.dev" in from_email or not settings.SMTP_FROM:
        from_header = "onboarding@resend.dev"

    payload = {
        "from": from_header,
        "to": [to_email],
        "subject": subject,
        "text": body,
    }
    if html_body:
        payload["html"] = html_body

    if attachment_path:
        try:
            with open(attachment_path, "rb") as f:
                content_bytes = f.read()
            filename = attachment_path.split("/")[-1].split("\\")[-1]
            payload["attachments"] = [
                {
                    "content": base64.b64encode(content_bytes).decode("utf-8"),
                    "filename": filename,
                }
            ]
        except Exception as e:
            print(f"Failed to attach file for Resend: {e}")

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            res_data = json.loads(res_body)
            return {
                "tool": "Email MCP",
                "status": "sent",
                "provider": "resend",
                "to": to_email,
                "subject": subject,
                "resend_id": res_data.get("id"),
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_json = json.loads(error_body)
            error_msg = error_json.get("message") or error_body
        except Exception:
            error_msg = error_body
        return {
            "tool": "Email MCP",
            "status": "failed",
            "provider": "resend",
            "to": to_email,
            "subject": subject,
            "error": f"HTTP {e.code}: {error_msg}",
        }
    except Exception as e:
        return {
            "tool": "Email MCP",
            "status": "failed",
            "provider": "resend",
            "to": to_email,
            "subject": subject,
            "error": str(e),
        }


def send_smtp_email(to_email, subject, body, attachment_path=None, html_body=None):
    if settings.RESEND_API_KEY:
        return send_resend_email(
            to_email=to_email,
            subject=subject,
            body=body,
            attachment_path=attachment_path,
            html_body=html_body,
        )

    smtp_user = settings.SMTP_USERNAME or settings.EMAIL_USER
    smtp_password = settings.SMTP_PASSWORD or settings.EMAIL_PASSWORD
    from_email = settings.SMTP_FROM or settings.EMAIL_USER or smtp_user
    from_name = settings.SMTP_FROM_NAME
    from_header = formataddr((from_name, from_email)) if from_name else from_email

    if not smtp_user or not smtp_password:
        return {
            "tool": "Email MCP",
            "status": "skipped",
            "provider": "smtp",
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

    return {
        "tool": "Email MCP",
        "status": "failed",
        "provider": "smtp",
        "to": to_email,
        "subject": subject,
        "smtp_host": settings.SMTP_HOST,
        "error": str(last_error) if last_error else "SMTP delivery failed",
        "attempts": attempts,
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
