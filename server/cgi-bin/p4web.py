from __future__ import annotations

from flyton_core import render_app


def render_page_request(query_string: str) -> bytes:
    return render_app(query_string)


def run(query_string: str) -> bytes:
    return render_page_request(query_string)
