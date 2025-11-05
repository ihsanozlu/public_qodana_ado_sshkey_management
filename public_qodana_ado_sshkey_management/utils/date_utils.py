import re
from datetime import datetime, timedelta, timezone

def calculate_expiration_from_createdTime(created_str: str, days_valid: int = 365) -> str:
    if not created_str:
        raise ValueError("Missing createdTime string")
    match = re.search(r"\d+", created_str)
    if not match:
        raise ValueError(f"Invalid createdTime format: {created_str}")
    created_ts = int(match.group()) / 1000
    created_dt = datetime.fromtimestamp(created_ts, tz=timezone.utc)
    expire_dt = created_dt + timedelta(days=days_valid)
    return expire_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def is_expired_date(date_str: str) -> bool:
    if not date_str:
        return True 

    try:
        expire_dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"⚠️ Invalid ado_expireDate format: {date_str}")
        return True

    #now = datetime.now(timezone.utc) + timedelta(days=363)
    now = datetime.now(timezone.utc)

    expired = expire_dt < now 
    #print(f"DEBUG: expire_dt={expire_dt}, now={now}, expired={expired}")

    return expired