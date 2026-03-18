from __future__ import annotations
import json
from urllib.parse import parse_qs

from db import create_session, get_session, latest_logs, log_event, touch_session, verify_login


def _json(data: dict) -> bytes:
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


def handle_api(query_string: str, body: bytes) -> bytes:
    params = {k: v[0] for k, v in parse_qs(query_string, keep_blank_values=True).items()}
    method = params.get("meth", "")

    try:
        payload = json.loads(body.decode("utf-8")) if body else {}
    except Exception:
        payload = {}

    if method == "api_login":
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", "")).strip()
        row = verify_login(username, password)
        if row is None:
            log_event("WARN", "login_failed", f"Login failed for '{username}'", {"username": username}, source="api")
            return _json({"server": {"allow": 0, "msg": "invalid login"}})
        ses = create_session(row["id"], {"username": username})
        log_event("INFO", "login_ok", f"Login success for '{username}'", {"username": username, "ses": ses}, source="api")
        return _json({"server": {"allow": 1}, "ses": ses, "go": f"/cgi-bin/p?app=start&ses={ses}"})

    if method == "api_status":
        ses = str(payload.get("ses") or params.get("ses") or "")
        row = get_session(ses) if ses else None
        if row is None:
            return _json({"server": {"allow": 0, "msg": "invalid session"}})
        touch_session(ses)
        return _json({
            "server": {"allow": 1},
            "user": {
                "username": row["username"],
                "first_name": row["FirstName"],
                "last_name": row["LastName"],
            },
            "logs": latest_logs(20),
        })

    return _json({"server": {"allow": 0, "msg": f"unknown method '{method}'"}})
