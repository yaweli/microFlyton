from __future__ import annotations

from apis.cgi import handle_api_request


def render_api_request(query_string: str, body: bytes) -> bytes:
    return handle_api_request(query_string, body)
