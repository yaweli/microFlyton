from __future__ import annotations

from urllib.parse import urlparse


def build_request_context(handler) -> dict:
    parsed = urlparse(handler.path)
    length = int(handler.headers.get("Content-Length", "0") or "0")
    return {
        "path": parsed.path,
        "query": parsed.query,
        "method": handler.command,
        "headers": dict(handler.headers),
        "length": length,
    }
