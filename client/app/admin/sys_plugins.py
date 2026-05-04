import json
from pathlib      import Path
from tools.sql        import *
from tools.db_plugins import *

_lib = Path(__file__).resolve().parent.parent.parent / "lib"


def _plugin_names():
    try:
        raw     = (_lib / "flyton_plugins.json").read_text(encoding="utf-8")
        catalog = json.loads(raw).get("p", [])
        return {p["code"]: p.get("name", p["code"]) for p in catalog if "code" in p}
    except Exception:
        return {}


def sys_plugins(data):
    ses = data["ses"]

    # handle disable action
    if data.get("action") == "disable":
        pid = data.get("plugin_id","")
        if pid:
            plugin_disable(int(pid))

    rows = plugin_list()

    if not rows:
        empty = """
        <div class="mf-plugin-empty">
            <div style="font-size:2.5rem">&#129074;</div>
            <div class="mt-2 text-muted">No plugins installed yet.</div>
        </div>
        """
    else:
        empty = ""

    names = _plugin_names()
    cards = ""
    for p in rows:
        pid   = p[0]
        pcode = p[1]
        pname = names.get(pcode, pcode)
        pdate = str(p[2])[:10] if p[2] else "—"
        dis_url = f"/cgi-bin/p?ses={ses}&rpage=sys_plugins&action=disable&plugin_id={pid}"
        cards += f"""
        <div class="col-sm-6 col-lg-4">
            <div class="mf-plugin-card">
                <div class="mf-plugin-icon">&#129070;</div>
                <div class="mf-plugin-name">{pname}</div>
                <div class="mf-plugin-date text-muted small">Installed: {pdate}</div>
                <div class="mf-plugin-badge mf-badge-active mt-2">Active</div>
                <a href="{dis_url}" class="mf-plugin-btn-disable btn btn-sm btn-outline-danger mt-3 w-100"
                   onclick="return confirm('Delete {pcode}?')">Delete</a>
            </div>
        </div>
        """

    add_url = f"/cgi-bin/p?ses={ses}&rpage=sys_plugins1"

    h = f"""
    <div class="col-12 px-4 pt-4">
        <div class="d-flex align-items-center justify-content-between mb-4">
            <div class="mf-page-title mb-0">&#129070; Plugins</div>
            <a href="{add_url}" class="btn btn-primary btn-sm px-4">&#43; Add Plugin</a>
        </div>
        {empty}
        <div class="row g-4">
            {cards}
        </div>
    </div>
    """
    return h
