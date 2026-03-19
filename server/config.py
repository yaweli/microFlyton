from __future__ import annotations
from pathlib import Path
import hashlib
import os
import platform

SERVER_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVER_ROOT.parent
CLIENT_ROOT = PROJECT_ROOT / "Client"


def _load_env_file(path: Path) -> bool:
    if not path.exists():
        return False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
    return True


def _resolve_env_file() -> str:
    primary = PROJECT_ROOT / ".env.micro"
    fallback = PROJECT_ROOT / ".env.micro.example"
    if _load_env_file(primary):
        return primary.name
    if _load_env_file(fallback):
        return fallback.name
    raise FileNotFoundError("Missing .env.micro and .env.micro.example")


def _machine_id() -> str:
    raw = "|".join([
        platform.node() or "",
        platform.system() or "",
        platform.release() or "",
        os.environ.get("COMPUTERNAME", ""),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


ENV_SOURCE = _resolve_env_file()
APP_NAME = os.getenv("APP_NAME", "Bridgekey MiniFlyton")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8080"))
AUTO_OPEN_BROWSER = os.getenv("AUTO_OPEN_BROWSER", "1") == "1"
DB_PATH = str((PROJECT_ROOT / os.getenv("DB_PATH", "./Server/data/microflyton.db")).resolve())
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "fly123")
START_URL = os.getenv("START_URL", f"http://{HOST}:{PORT}/pages/index.html")
MACHINE_ID = os.getenv("MACHINE_ID", _machine_id())
