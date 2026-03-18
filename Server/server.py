from __future__ import annotations
import json
import logging
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from api.router import handle_api
from config import APP_NAME, AUTO_OPEN_BROWSER, CLIENT_ROOT, ENV_SOURCE, HOST, MACHINE_ID, PORT, SERVER_ROOT, START_URL
from db import init_db, log_event
from flyton_core import client_pages_root, guess_type, render_app

logging.basicConfig(
    filename=str(SERVER_ROOT / "logs" / "server.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

STATIC_DIRS = {
    "/pages/": client_pages_root(),
    "/lib/": SERVER_ROOT / "lib",
}


class MiniFlytonHandler(BaseHTTPRequestHandler):
    server_version = "MiniFlyton/1.2"

    def log_message(self, fmt: str, *args):
        logging.info("%s - %s", self.address_string(), fmt % args)

    def _send_bytes(self, code: int, data: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            data = (f'<html><body><script>location.href="/pages/index.html";</script>'
                    f'<a href="/pages/index.html">{APP_NAME}</a></body></html>').encode("utf-8")
            return self._send_bytes(200, data, "text/html; charset=utf-8")

        if parsed.path == "/health":
            body = json.dumps({
                "ok": True,
                "app": APP_NAME,
                "env_source": ENV_SOURCE,
                "machine_id": MACHINE_ID,
                "server_root": str(SERVER_ROOT),
                "client_root": str(CLIENT_ROOT),
            }).encode("utf-8")
            return self._send_bytes(200, body, "application/json; charset=utf-8")

        if parsed.path == "/cgi-bin/p":
            try:
                data = render_app(parsed.query)
                return self._send_bytes(200, data, "text/html; charset=utf-8")
            except Exception as exc:
                logging.exception("CGI render failed")
                log_event("ERROR", "cgi_render", str(exc), {"path": self.path}, source="server")
                return self._send_bytes(500, f"<h1>Server error</h1><pre>{exc}</pre>".encode("utf-8"), "text/html; charset=utf-8")

        for prefix, folder in STATIC_DIRS.items():
            if parsed.path.startswith(prefix):
                rel = parsed.path[len(prefix):]
                file_path = (folder / rel).resolve()
                if not str(file_path).startswith(str(folder.resolve())) or not file_path.exists() or not file_path.is_file():
                    return self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")
                return self._send_bytes(200, file_path.read_bytes(), guess_type(file_path))

        return self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/cgi-bin/api":
            return self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        try:
            data = handle_api(parsed.query, body)
            return self._send_bytes(200, data, "application/json; charset=utf-8")
        except Exception as exc:
            logging.exception("API failed")
            log_event("ERROR", "api_error", str(exc), {"path": self.path}, source="api")
            return self._send_bytes(500, b'{"server":{"allow":0,"err":"server error"}}', "application/json; charset=utf-8")


def open_browser_once():
    try:
        webbrowser.open(START_URL)
    except Exception:
        logging.exception("Browser auto-open failed")


def main():
    init_db()
    log_event("INFO", "server_start", f"{APP_NAME} starting", {"host": HOST, "port": PORT, "env_source": ENV_SOURCE}, source="server")
    httpd = ThreadingHTTPServer((HOST, PORT), MiniFlytonHandler)
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
    if str(SERVER_ROOT) not in sys.path:
        sys.path.insert(0, str(SERVER_ROOT))
    main()
