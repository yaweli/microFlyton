from __future__ import annotations

import contextlib
import html
import importlib.util
import io
import mimetypes
import sys
from pathlib import Path
from urllib.parse import parse_qs

from pathlib import Path as _Path

_SERVER_ROOT         = _Path(__file__).resolve().parent
_PROJECT_ROOT        = _SERVER_ROOT.parent
CLIENT_ROOT          = _PROJECT_ROOT / "client"
CLIENT_APP_ROOT      = CLIENT_ROOT / "app"
LEGACY_SERVER_APP_ROOT = _SERVER_ROOT / "app"


def safe_app_name(name: str) -> str:
    if not name:
        raise ValueError("missing app")
    if "/" in name or "\\" in name or ".." in name:
        raise ValueError("illegal app path")
    return name


def dynamic_import(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _resolve_app_path(app_name: str) -> Path:
    candidates = [
        CLIENT_APP_ROOT / f"{app_name}.py",
        LEGACY_SERVER_APP_ROOT / f"{app_name}.py",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(app_name)


def render_app(query_string: str) -> bytes:
    params = {k: v[0] for k, v in parse_qs(query_string, keep_blank_values=True).items()}
    app_name = safe_app_name(params.get("app", "start"))
    try:
        app_path = _resolve_app_path(app_name)
    except FileNotFoundError:
        body = f"""<!doctype html>
<html><body><h1>App not found</h1><pre>{html.escape(app_name)}</pre></body></html>"""
        return body.encode("utf-8")

    app_root = str(app_path.parent)
    added = False
    if app_root not in sys.path:
        sys.path.insert(0, app_root)
        added = True
    buffer = io.StringIO()
    try:
        module = dynamic_import(app_path)
        if not hasattr(module, "main"):
            raise RuntimeError(f"{app_name}.py has no main(ctx)")
        with contextlib.redirect_stdout(buffer):
            result = module.main(params)
    finally:
        if added:
            try:
                sys.path.remove(app_root)
            except ValueError:
                pass

    captured = buffer.getvalue()
    if isinstance(result, str) and result:
        return result.encode("utf-8")
    if captured:
        return captured.encode("utf-8")
    raise TypeError("app main(ctx) must return str or print HTML")


def guess_type(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def client_pages_root() -> Path:
    return CLIENT_ROOT / "pages"
