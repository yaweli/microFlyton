from __future__ import annotations

import contextlib
import importlib
import io
import json
import traceback

from urllib.parse import *
from apis.tools.sql import *


UNSESSION_METHODS = {"api_login", "ping", "api_start_prv"}


def version() -> str:
    return "1.11"


def _resolve_method(method: str) -> tuple[str, str] | None:
    m = method.strip()
    if not m:
        return None
    candidates = []
    candidates.append((f"apis.api.{m}", m))

    for module_name, func_name in candidates:
        try:
            importlib.import_module(module_name)
            return module_name, func_name
        except ModuleNotFoundError as e:
            import os, sys
            print(f"[cgi] module not found: {module_name} -> {e}", flush=True)
            print(f"[cgi] cwd: {os.getcwd()}", flush=True)
            print(f"[cgi] sys.path: {sys.path}", flush=True)
            continue
    return None


def _normalize_payload(body: bytes) -> dict:
    try:
        payload = json.loads(body.decode("utf-8")) if body else {}
        if not isinstance(payload, dict):
            payload = {}
    except Exception:
        payload = {}

    if "info"  not in payload or not isinstance(payload.get("info"),  dict): payload["info"]  = {}
    if "input" not in payload or not isinstance(payload.get("input"), dict): payload["input"] = {}

    if "username" in payload and "u" not in payload["input"]: payload["input"]["u"] = payload.get("username")
    if "password" in payload and "p" not in payload["input"]: payload["input"]["p"] = payload.get("password")
    if "ses"      in payload and "ses" not in payload["info"]: payload["info"]["ses"] = payload.get("ses")

    payload["info"].setdefault("os",   "web")
    payload["info"].setdefault("ses",  "")
    payload["info"].setdefault("uses", "")
    return payload


def handle_api_request(query_string: str, body: bytes) -> bytes:
    params  = {k: v[0] for k, v in parse_qs(query_string, keep_blank_values=True).items()}
    method  = params.get("meth", "").strip()
    payload = _normalize_payload(body)

    base = f'"method":"{method}","server_ver":"{version()}"'

    resolved = _resolve_method(method)
    if not resolved:
        return f'{{"server":{{{base},"allow":0,"err":"missing or unknown method"}}}}'.encode("utf-8")

    if method not in UNSESSION_METHODS:
        ses = str(payload.get("info", {}).get("ses") or payload.get("ses") or params.get("ses") or "")
        row = get_session(ses) if ses else None
        if row is None:
            return f'{{"server":{{{base},"allow":0,"err":"method need login","sact":"out","xses":"{ses}"}}}}'.encode("utf-8")
        payload["session"] = row

    module_name, func_name = resolved
    module = importlib.import_module(module_name)
    func   = getattr(module, func_name, None)
    if func is None:
        return f'{{"server":{{{base},"allow":0,"err":"method implementation not found"}}}}'.encode("utf-8")

    # capture print() output - all Flyton APIs respond via print()
    print(f"[API] calling {method}", flush=True)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            func({"par": params, "post": payload})
    except BaseException as exc:
        tb = traceback.format_exc()
        print(f"\n[CRASH] api {method}: {exc}\n{tb}", flush=True)
        raise
    print(f"[API] {method} done", flush=True)

    captured = buf.getvalue().strip().lstrip(",").strip()
    if captured:
        return f'{{"server":{{{base},{captured}}}}}'.encode("utf-8")
    return f'{{"server":{{{base}}}}}'.encode("utf-8")
