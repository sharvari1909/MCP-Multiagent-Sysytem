import imaplib
import email
from email.header import decode_header
from config import settings


def clean_text(value):
    if not value:
        return ""

    decoded, encoding = decode_header(value)[0]

    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")

    return decoded


def read_unread_emails(limit=5):
    mailbox = imaplib.IMAP4_SSL(settings.IMAP_HOST, settings.IMAP_PORT)
    mailbox.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
    mailbox.select("INBOX")

    status, messages = mailbox.search(None, "UNSEEN")

    if status != "OK":
        mailbox.logout()
        return []

    email_ids = messages[0].split()
    email_ids = email_ids[-limit:]

    emails = []

    for email_id in email_ids:
        status, msg_data = mailbox.fetch(email_id, "(RFC822)")

        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])

        subject = clean_text(msg.get("Subject"))
        from_email = clean_text(msg.get("From"))
        to_email = clean_text(msg.get("To"))

        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in disposition:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        emails.append({
            "id": email_id.decode(),
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "body": body,
        })

    mailbox.logout()
    return emails