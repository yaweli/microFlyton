from __future__ import annotations

import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from flyton_core import guess_type
from runtime.cgi_bridge import render_api_request, render_p4web_request, render_page_request
from runtime.pathmap import CGI_API_PATHS, CGI_P4WEB_PATHS, CGI_PAGE_PATHS, resolve_static_path

SERVER_ROOT = Path(__file__).resolve().parent.parent
CLIENT_ROOT = SERVER_ROOT.parent / "client"
APP_NAME    = os.getenv("APP_NAME", "MicroFlyton")
HOST        = os.getenv("HOST", "127.0.0.1")
PORT        = int(os.getenv("PORT", "8080"))


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

    def handle_error(self, request, client_address):
        import traceback
        print(f"\n[CRASH] request from {client_address}", flush=True)
        traceback.print_exc()
        print(flush=True)

    def do_GET(self):
        parsed = urlparse(self.path)
        print(f"[GET] {parsed.path}", flush=True)
        if parsed.path == "/":
            html = (
                f'<!doctype html><html><body><h1>{APP_NAME}</h1>'
                f'<p><a href="/pages/index.html">Open MicroFlyton</a></p></body></html>'
            ).encode("utf-8")
            return self._send_bytes(200, html, "text/html; charset=utf-8")
        if parsed.path == "/health":
            body = json.dumps({"ok": True, "app": APP_NAME}).encode("utf-8")
            return self._send_bytes(200, body, "application/json; charset=utf-8")
        if parsed.path in CGI_PAGE_PATHS:
            print(f"[GET] -> render_page_request", flush=True)
            data = render_page_request(parsed.query)
            return self._send_bytes(200, data, "text/html; charset=utf-8")
        if parsed.path in CGI_P4WEB_PATHS:
            print(f"[GET] -> render_p4web_request", flush=True)
            data = render_p4web_request(parsed.query)
            return self._send_bytes(200, data, "text/html; charset=utf-8")
        if parsed.path in CGI_API_PATHS:
            print(f"[GET] -> render_api_request", flush=True)
            data = render_api_request(parsed.query, b"")
            print(f"[GET] -> done", flush=True)
            return self._send_bytes(200, data, "application/json; charset=utf-8")
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

    def do_STOP(self):
        client_ip = self.client_address[0]
        if client_ip not in ("127.0.0.1", "::1", "localhost"):
            self._send_bytes(403, b"Forbidden", "text/plain; charset=utf-8")
            return
        self._send_bytes(200, b'{"ok":true,"msg":"stopping"}', "application/json; charset=utf-8")
        print(f"[STOP] Shutdown requested by {client_ip}", flush=True)
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def do_POST(self):
        parsed = urlparse(self.path)
        print(f"[POST] {parsed.path}", flush=True)
        if parsed.path not in CGI_API_PATHS:
            return self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")
        length = int(self.headers.get("Content-Length", "0") or "0")
        body   = self.rfile.read(length)
        print(f"[POST] -> render_api_request", flush=True)
        data   = render_api_request(parsed.query, body)
        print(f"[POST] -> done", flush=True)
        return self._send_bytes(200, data, "application/json; charset=utf-8")


def create_server() -> ThreadingHTTPServer:
    return ThreadingHTTPServer((HOST, PORT), MicroFlytonHandler)
