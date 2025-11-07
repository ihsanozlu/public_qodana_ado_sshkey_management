import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("data/ado_authorization_log.json")


def _load_log():
    if not LOG_FILE.exists():
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def _save_log(data):
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save ADO authorization log: {e}")


def log_ado_authorization_event(
    project_name: str,
    authorization_id: str,
    expire_date: str = "",
    event: str = "created",
):
    """
    Log when an ADO authorizationId is created or refreshed.
    """
    if not authorization_id:
        return

    data = _load_log()

    log_entry = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project": project_name,
        "authorization_id": authorization_id,
        "expire_date": expire_date,
        "event": event,
    }

    data.append(log_entry)
    _save_log(data)

    print(f"📝 Logged {event} event for {project_name} ({authorization_id})")
