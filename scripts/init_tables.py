import sqlite3
import sys
import os

SQL = """
CREATE TABLE IF NOT EXISTS users (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT UNIQUE,
    LastName  TEXT,
    FirstName TEXT,
    Roles     TEXT DEFAULT NULL,
    sis       TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data      TEXT DEFAULT NULL
);

INSERT OR IGNORE INTO users (id, username, LastName, FirstName, is_active, Roles, sis)
VALUES (1001, 'kic', 'kic', 'admin', 1, '["admin","owner"]', 'Zmx5MTIz');

CREATE TABLE IF NOT EXISTS gen (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    key1      TEXT,
    val1      TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data      TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS ses (
    id        TEXT PRIMARY KEY,
    user_id   INTEGER,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data      TEXT DEFAULT NULL
);
"""

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not db_path:
        print("ERROR: db_path argument required")
        sys.exit(1)

    db_dir = os.path.dirname(os.path.abspath(db_path))
    os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SQL)
        conn.commit()
        print(f"Tables initialized: {db_path}")
    finally:
        conn.close()
