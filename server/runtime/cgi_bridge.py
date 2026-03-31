from __future__ import annotations

import importlib.util
from functools import lru_cache
from pathlib import Path

from config import SERVER_ROOT

CGI_ROOT = SERVER_ROOT / "cgi-bin"


def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load CGI entry: {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=2)
def _page_module():
    return _load_module("microflyton_cgi_page", CGI_ROOT / "p.py")


@lru_cache(maxsize=2)
def _api_module():
    return _load_module("microflyton_cgi_api", CGI_ROOT / "api.py")


@lru_cache(maxsize=2)
def _p4web_module():
    return _load_module("microflyton_cgi_p4web", CGI_ROOT / "p4web.py")


def render_page_request(query_string: str) -> bytes:
    module = _page_module()
    func = getattr(module, "render_page_request", None)
    if func is None:
        raise RuntimeError("server/cgi-bin/p.py is missing render_page_request(query_string)")
    return func(query_string)


def render_api_request(query_string: str, body: bytes) -> bytes:
    module = _api_module()
    func = getattr(module, "render_api_request", None)
    if func is None:
        raise RuntimeError("server/cgi-bin/api.py is missing render_api_request(query_string, body)")
    return func(query_string, body)


def render_p4web_request(query_string: str) -> bytes:
    module = _p4web_module()
    func = getattr(module, "render_page_request", None) or getattr(module, "run", None)
    if func is None:
        raise RuntimeError("server/cgi-bin/p4web.py is missing render_page_request(query_string) or run(query_string)")
    return func(query_string)
