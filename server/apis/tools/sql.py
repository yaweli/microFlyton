from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from config import ADMIN_PASSWORD, ADMIN_USERNAME, DB_BACKEND, DB_PATH


class UnsupportedBackendError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_parent() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


def _sqlite_connect() -> sqlite3.Connection:
    _ensure_parent()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _connect():
    if DB_BACKEND == "sqlite":
        return _sqlite_connect()
    raise UnsupportedBackendError(f"DB backend '{DB_BACKEND}' is not implemented in this package")


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _default_user_payload() -> dict[str, Any]:
    return {
        "name": ADMIN_USERNAME,
        "username": ADMIN_USERNAME,
        "email": f"{ADMIN_USERNAME}@local",
        "is_active": 1,
        "first_name": "Admin",
        "last_name": "User",
        "data": {},
    }


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                username TEXT UNIQUE,
                email TEXT,
                password_hash TEXT,
                is_active INTEGER DEFAULT 1,
                first_name TEXT,
                last_name TEXT,
                created_at TEXT,
                updated_at TEXT,
                data TEXT
            );

            CREATE TABLE IF NOT EXISTS ses (
                ses_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ses TEXT UNIQUE,
                user_id INTEGER,
                username TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT,
                data TEXT
            );

            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                code TEXT,
                msg TEXT,
                source TEXT,
                created_at TEXT,
                data TEXT
            );
            """
        )
        now = _utc_now()
        row = conn.execute("SELECT user_id FROM users WHERE username = ?", (ADMIN_USERNAME,)).fetchone()
        if row is None:
            user = _default_user_payload()
            conn.execute(
                """
                INSERT INTO users (name, username, email, password_hash, is_active, first_name, last_name, created_at, updated_at, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user["name"],
                    user["username"],
                    user["email"],
                    _hash_password(ADMIN_PASSWORD),
                    user["is_active"],
                    user["first_name"],
                    user["last_name"],
                    now,
                    now,
                    json.dumps(user["data"], ensure_ascii=False),
                ),
            )
        conn.commit()


def verify_login(username: str, password: str):
    with _connect() as conn:
        row = conn.execute(
            "SELECT user_id, username, first_name, last_name, is_active FROM users WHERE username = ? AND password_hash = ?",
            (username, _hash_password(password)),
        ).fetchone()
        if row is None or int(row["is_active"] or 0) != 1:
            return None
        return dict(row)


def create_session(user_id: int, data: dict[str, Any] | None = None) -> str:
    ses = hashlib.sha256(f"{user_id}|{_utc_now()}".encode("utf-8")).hexdigest()[:24]
    now = _utc_now()
    payload = data or {}
    with _connect() as conn:
        user = conn.execute(
            "SELECT username FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        username = (user["username"] if user else "")
        conn.execute(
            "INSERT INTO ses (ses, user_id, username, is_active, created_at, updated_at, data) VALUES (?, ?, ?, 1, ?, ?, ?)",
            (ses, user_id, username, now, now, json.dumps(payload, ensure_ascii=False)),
        )
        conn.commit()
    return ses


def get_session(ses: str):
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT s.ses, s.user_id, s.username, u.first_name, u.last_name
            FROM ses s
            JOIN users u ON u.user_id = s.user_id
            WHERE s.ses = ? AND s.is_active = 1 AND u.is_active = 1
            """,
            (ses,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)


def touch_session(ses: str) -> None:
    with _connect() as conn:
        conn.execute("UPDATE ses SET updated_at = ? WHERE ses = ?", (_utc_now(), ses))
        conn.commit()


def log_event(level: str, code: str, msg: str, data: dict[str, Any] | None = None, source: str = "system") -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO logs (level, code, msg, source, created_at, data) VALUES (?, ?, ?, ?, ?, ?)",
            (level, code, msg, source, _utc_now(), json.dumps(data or {}, ensure_ascii=False)),
        )
        conn.commit()


def latest_logs(limit: int = 20) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT log_id, level, code, msg, source, created_at, data FROM logs ORDER BY log_id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            try:
                item["data"] = json.loads(item.get("data") or "{}")
            except Exception:
                pass
            result.append(item)
        return result
