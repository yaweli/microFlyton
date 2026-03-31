from __future__ import annotations

from pathlib import Path
import hashlib
import os
import platform
import re

SERVER_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVER_ROOT.parent
CLIENT_ROOT = PROJECT_ROOT / "client"
CLIENT_APP_ROOT = CLIENT_ROOT / "app"
CLIENT_LIB_ROOT = CLIENT_ROOT / "lib"
CLIENT_PAGES_ROOT = CLIENT_ROOT / "pages"
LEGACY_CLIENT_ROOT = PROJECT_ROOT / "Client"
LEGACY_SERVER_APP_ROOT = SERVER_ROOT / "app"
DATA_ROOT = SERVER_ROOT / "data"
LOGS_ROOT = SERVER_ROOT / "logs"

for folder in (DATA_ROOT, LOGS_ROOT):
    folder.mkdir(parents=True, exist_ok=True)


def _load_env_file(path: Path) -> bool:
    if not path.exists():
        return False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return True


def _resolve_env_file() -> str:
    primary = PROJECT_ROOT / ".env.micro"
    if _load_env_file(primary):
        return primary.name
    raise FileNotFoundError("Missing .env.micro")


def _machine_id() -> str:
    raw = "|".join([
        platform.node() or "",
        platform.system() or "",
        platform.release() or "",
        os.environ.get("COMPUTERNAME", ""),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _resolve_runtime_path(raw_value: str, fallback: str) -> str:
    raw = (raw_value or fallback).strip()
    if re.match(r"^[A-Za-z]:[\/]", raw) or raw.startswith("\\"):
        return raw
    path = Path(raw)
    if path.is_absolute():
        return str(path)
    return str((PROJECT_ROOT / path).resolve())


ENV_SOURCE = _resolve_env_file()
APP_NAME = os.getenv("APP_NAME", "Bridgekey MicroFlyton")
APP_MODE = os.getenv("APP_MODE", "microflyton")
WEB_BACKEND = os.getenv("WEB_BACKEND", "python")
DB_BACKEND = os.getenv("DB_BACKEND", "sqlite")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8080"))
AUTO_OPEN_BROWSER = os.getenv("AUTO_OPEN_BROWSER", "1") == "1"
DB_PATH = _resolve_runtime_path(os.getenv("DB_PATH", "./server/data/microflyton.db"), "./server/data/microflyton.db")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "fly123")
START_URL = os.getenv("START_URL", f"http://{HOST}:{PORT}/pages/index.html")
MACHINE_ID = os.getenv("MACHINE_ID", _machine_id())
