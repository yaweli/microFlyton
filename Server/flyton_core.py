from __future__ import annotations
import html
import importlib.util
import mimetypes
from pathlib import Path
from urllib.parse import parse_qs

from config import CLIENT_ROOT, SERVER_ROOT


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


def render_app(query_string: str) -> bytes:
    params = {k: v[0] for k, v in parse_qs(query_string, keep_blank_values=True).items()}
    app_name = safe_app_name(params.get("app", "start"))
    app_path = SERVER_ROOT / "app" / f"{app_name}.py"
    if not app_path.exists():
        body = f"<h1>App not found</h1><p>{html.escape(app_name)}</p>"
        return body.encode("utf-8")
    module = dynamic_import(app_path)
    if not hasattr(module, "main"):
        raise RuntimeError(f"{app_name}.py has no main(ctx)")
    html_out = module.main(params)
    if not isinstance(html_out, str):
        raise TypeError("app main(ctx) must return str")
    return html_out.encode("utf-8")


def guess_type(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def client_pages_root() -> Path:
    return CLIENT_ROOT / "pages"
