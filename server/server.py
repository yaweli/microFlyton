from __future__ import annotations

import logging
import threading
import webbrowser

from apis.tools.sql import init_db, log_event
from config import APP_NAME, AUTO_OPEN_BROWSER, ENV_SOURCE, HOST, LOGS_ROOT, MACHINE_ID, PORT, START_URL
from runtime.windows_http import create_server

LOGS_ROOT.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(LOGS_ROOT / "server.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def open_browser_once() -> None:
    try:
        webbrowser.open(START_URL)
    except Exception:
        logging.exception("Browser auto-open failed")


def main() -> None:
    init_db()
    log_event(
        "INFO",
        "server_start",
        f"{APP_NAME} starting",
        {"host": HOST, "port": PORT, "env_source": ENV_SOURCE},
        source="server",
    )
    httpd = create_server()
    if AUTO_OPEN_BROWSER:
        threading.Timer(1.0, open_browser_once).start()
    print(f"{APP_NAME} running on http://{HOST}:{PORT}")
    print(f"Config source: {ENV_SOURCE}")
    print(f"Machine ID: {MACHINE_ID}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"{APP_NAME} stopped.")
        log_event("INFO", "server_stop", f"{APP_NAME} stopped by user", source="server")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
