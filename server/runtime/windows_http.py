from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from apis.tools.sql import log_event
from config import APP_NAME, CLIENT_ROOT, ENV_SOURCE, HOST, MACHINE_ID, PORT, SERVER_ROOT
from flyton_core import guess_type
from runtime.cgi_bridge import render_api_request, render_p4web_request, render_page_request
from runtime.pathmap import CGI_API_PATHS, CGI_P4WEB_PATHS, CGI_PAGE_PATHS, resolve_static_path


class MicroFlytonHandler(BaseHTTPRequestHandler):
    server_version = "MicroFlyton/2.2"

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
            html = (
                f'<!doctype html><html><body><h1>{APP_NAME}</h1>'
                f'<p><a href="/pages/index.html">Open MicroFlyton</a></p></body></html>'
            ).encode("utf-8")
            return self._send_bytes(200, html, "text/html; charset=utf-8")
        if parsed.path == "/health":
            body = json.dumps(
                {
                    "ok": True,
                    "app": APP_NAME,
                    "env_source": ENV_SOURCE,
                    "machine_id": MACHINE_ID,
                    "server_root": str(SERVER_ROOT),
                    "client_root": str(CLIENT_ROOT),
                }
            ).encode("utf-8")
            return self._send_bytes(200, body, "application/json; charset=utf-8")
        if parsed.path in CGI_PAGE_PATHS:
            try:
                data = render_page_request(parsed.query)
                return self._send_bytes(200, data, "text/html; charset=utf-8")
            except Exception as exc:
                logging.exception("CGI render failed")
                log_event("ERROR", "cgi_render", str(exc), {"path": self.path}, source="server")
                return self._send_bytes(
                    500,
                    f"<h1>Server error</h1><pre>{exc}</pre>".encode("utf-8"),
                    "text/html; charset=utf-8",
                )
        if parsed.path in CGI_P4WEB_PATHS:
            try:
                data = render_p4web_request(parsed.query)
                return self._send_bytes(200, data, "text/html; charset=utf-8")
            except Exception as exc:
                logging.exception("P4WEB render failed")
                log_event("ERROR", "p4web_render", str(exc), {"path": self.path}, source="server")
                return self._send_bytes(
                    500,
                    f"<h1>Server error</h1><pre>{exc}</pre>".encode("utf-8"),
                    "text/html; charset=utf-8",
                )
        if parsed.path in CGI_API_PATHS:
            try:
                data = render_api_request(parsed.query, b"")
                return self._send_bytes(200, data, "application/json; charset=utf-8")
            except Exception as exc:
                logging.exception("API GET failed")
                log_event("ERROR", "api_get_error", str(exc), {"path": self.path}, source="api")
                return self._send_bytes(500, b'{"server":{"allow":0,"err":"server error"}}', "application/json; charset=utf-8")
        folder, rel = resolve_static_path(parsed.path)
        if folder is not None:
            file_path = (folder / rel).resolve()
            if rel == "":
                index_path = (folder / "index.html").resolve()
                if index_path.exists():
                    return self._send_bytes(200, index_path.read_bytes(), guess_type(index_path))
            if not str(file_path).startswith(str(folder.resolve())) or not file_path.exists() or not file_path.is_file():
                return self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")
            return self._send_bytes(200, file_path.read_bytes(), guess_type(file_path))
        return self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path not in CGI_API_PATHS:
            return self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length)
        try:
            data = render_api_request(parsed.query, body)
            return self._send_bytes(200, data, "application/json; charset=utf-8")
        except Exception as exc:
            logging.exception("API failed")
            log_event("ERROR", "api_error", str(exc), {"path": self.path}, source="api")
            return self._send_bytes(500, b'{"server":{"allow":0,"err":"server error"}}', "application/json; charset=utf-8")


def create_server() -> ThreadingHTTPServer:
    return ThreadingHTTPServer((HOST, PORT), MicroFlytonHandler)
