from __future__ import annotations

from apis.tools.sql import latest_logs, touch_session


def api_status(data: dict) -> dict:
    payload = data.get("post", {})
    ses = str(payload.get("info", {}).get("ses") or payload.get("ses") or "")
    row = payload.get("session")
    if not isinstance(row, dict):
        return {"server": {"allow": 0, "err": "invalid session"}}

    touch_session(ses)
    return {
        "server": {"allow": 1},
        "user": {
            "username": row["username"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
        },
        "logs": latest_logs(20),
    }
