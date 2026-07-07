from datetime import datetime


def log_event(message: str, level: str = "info"):
    return {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "level": level,
        "message": message,
    }