from __future__ import annotations

import base64

from apis.tools.sql import create_session, log_event, verify_login


def _decode_password(raw: str) -> str:
    if not raw:
        return ""
    try:
        return base64.b64decode(raw).decode("utf-8")
    except Exception:
        return raw


def api_login(data: dict) -> dict:
    payload = data.get("post", {})
    info = payload.get("info", {})
    user_input = payload.get("input", {})

    username = str(user_input.get("u") or payload.get("username") or "").strip()
    password = _decode_password(str(user_input.get("p") or payload.get("password") or "").strip())

    row = verify_login(username, password)
    if row is None:
        log_event("WARN", "login_failed", f"Login failed for '{username}'", {"username": username, "os": info.get("os", "")}, source="api")
        return {"server": {"user": username, "allow": 0}}

    ses = create_session(row["user_id"], {"username": username, "os": info.get("os", "web")})
    log_event("INFO", "login_ok", f"Login success for '{username}'", {"username": username, "ses": ses}, source="api")
    return {"server": {"user": username, "allow": 1, "ses": ses}}
