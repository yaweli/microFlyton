from __future__ import annotations

from pathlib import Path

_PROJECT_ROOT    = Path(__file__).resolve().parent.parent.parent
CLIENT_PAGES_ROOT = _PROJECT_ROOT / "client" / "pages"
CLIENT_LIB_ROOT   = _PROJECT_ROOT / "client" / "lib"

STATIC_PREFIXES = {
    "/pages/": CLIENT_PAGES_ROOT,
    "/Client/pages/": CLIENT_PAGES_ROOT,
    "/lib/": CLIENT_LIB_ROOT,
}

CGI_PAGE_PATHS = {"/cgi-bin/p", "/pages/cgi-bin/p"}
CGI_P4WEB_PATHS = {"/cgi-bin/p4web", "/pages/cgi-bin/p4web"}
CGI_API_PATHS = {"/cgi-bin/api", "/pages/cgi-bin/api"}


def resolve_static_path(url_path: str) -> tuple[Path | None, str | None]:
    for prefix, folder in STATIC_PREFIXES.items():
        if url_path.startswith(prefix):
            rel = url_path[len(prefix):]
            return folder, rel
    return None, None
