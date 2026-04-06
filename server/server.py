from __future__ import annotations

import logging
import os
import sys
import threading
import webbrowser
from pathlib import Path

SERVER_ROOT  = Path(__file__).resolve().parent
PROJECT_ROOT = SERVER_ROOT.parent
LOGS_ROOT    = SERVER_ROOT / "logs"
LOGS_ROOT.mkdir(parents=True, exist_ok=True)

def _load_env():
    path = PROJECT_ROOT / ".env.micro"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env()

sys.path.insert(0, str(SERVER_ROOT / "apis"))
os.chdir(str(SERVER_ROOT / "apis"))

APP_NAME          = os.getenv("APP_NAME", "MicroFlyton")
HOST              = os.getenv("HOST", "127.0.0.1")
PORT              = int(os.getenv("PORT", "8080"))
AUTO_OPEN_BROWSER = os.getenv("AUTO_OPEN_BROWSER", "1") == "1"
START_URL         = os.getenv("START_URL", f"http://{HOST}:{PORT}/pages/index.html")

logging.basicConfig(
    filename=str(LOGS_ROOT / "server.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

from runtime.windows_http import create_server


def open_browser_once() -> None:
    try:
        webbrowser.open(START_URL)
    except Exception:
        logging.exception("Browser auto-open failed")


def main() -> None:
    httpd = create_server()
    if AUTO_OPEN_BROWSER:
        threading.Timer(1.0, open_browser_once).start()
    print(f"{APP_NAME} running on http://{HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"{APP_NAME} stopped.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
