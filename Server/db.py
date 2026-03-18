from __future__ import annotations
import base64
import json
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from config import ADMIN_PASSWORD, ADMIN_USERNAME, DB_PATH, MACHINE_ID

Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    names = {row[1] for row in rows}
    if column not in names:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def init_db() -> None:
    admin_created = False
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                LastName TEXT NOT NULL DEFAULT '',
                FirstName TEXT NOT NULL DEFAULT '',
                Roles TEXT,
                sis TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                update_at TEXT NOT NULL,
                data TEXT
            );

            CREATE TABLE IF NOT EXISTS ses (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                update_at TEXT NOT NULL,
                data TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS gen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key1 TEXT,
                val1 TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                update_at TEXT NOT NULL,
                data TEXT
            );

            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_source TEXT NOT NULL DEFAULT 'system',
                machine_id TEXT NOT NULL DEFAULT '',
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                data TEXT
            );
            """
        )
        _ensure_column(conn, "logs", "event_source", "event_source TEXT NOT NULL DEFAULT 'system'")
        _ensure_column(conn, "logs", "machine_id", "machine_id TEXT NOT NULL DEFAULT ''")

        row = conn.execute("SELECT id FROM users WHERE username = ?", (ADMIN_USERNAME,)).fetchone()
        if row is None:
            encoded = base64.b64encode(ADMIN_PASSWORD.encode("utf-8")).decode("ascii")
            now = now_utc()
            conn.execute(
                """
                INSERT INTO users (
                    username, LastName, FirstName, Roles, sis, is_active, created_at, update_at, data
                ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
                """,
                (
                    ADMIN_USERNAME,
                    "Local",
                    "Admin",
                    json.dumps(["admin", "owner"]),
                    encoded,
                    now,
                    now,
                    json.dumps({"bootstrap": "created"}),
                ),
            )
            admin_created = True
    if admin_created:
        log_event("INFO", "bootstrap", f"Created default admin user '{ADMIN_USERNAME}'", source="bootstrap")


def log_event(level: str, event_type: str, message: str, data: dict | None = None, source: str = "system") -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO logs(level, event_type, event_source, machine_id, message, created_at, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (level, event_type, source, MACHINE_ID, message, now_utc(), json.dumps(data or {}, ensure_ascii=False)),
        )


def get_user_by_username(username: str):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,),
        ).fetchone()


def create_session(user_id: int, data: dict | None = None) -> str:
    ses = secrets.token_hex(16)
    now = now_utc()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO ses(id, user_id, is_active, created_at, update_at, data) VALUES (?, ?, 1, ?, ?, ?)",
            (ses, user_id, now, now, json.dumps(data or {}, ensure_ascii=False)),
        )
    return ses


def get_session(ses: str):
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT s.*, u.username, u.FirstName, u.LastName, u.Roles
            FROM ses s
            JOIN users u ON u.id = s.user_id
            WHERE s.id = ? AND s.is_active = 1
            """,
            (ses,),
        ).fetchone()


def touch_session(ses: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE ses SET update_at = ? WHERE id = ?", (now_utc(), ses))


def verify_login(username: str, password: str):
    row = get_user_by_username(username)
    if row is None:
        return None
    encoded = base64.b64encode(password.encode("utf-8")).decode("ascii")
    if row["sis"] != encoded:
        return None
    return row


def latest_logs(limit: int = 25):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, level, event_type, event_source, machine_id, message, created_at, data FROM logs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]
