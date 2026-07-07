from datetime import datetime
from uuid import uuid4


def log_event(message: str, level: str = "info"):
    return {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "level": level,
        "message": message,
    }


def generate_invoice_number():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = uuid4().hex[:6].upper()
    return f"INV-{timestamp}-{suffix}"
