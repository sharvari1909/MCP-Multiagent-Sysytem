import json
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

AUDIT_FILE = LOG_DIR / "audit.json"


def _load():
    if not AUDIT_FILE.exists():
        return []

    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_audit_event(event_type, payload):
    data = _load()

    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "payload": payload,
    }

    data.append(event)
    _save(data)

    return {
        "tool": "Audit MCP",
        "status": "saved",
        "event": event,
    }


def get_audit_logs():
    return {
        "tool": "Audit MCP",
        "logs": _load(),
    }
    