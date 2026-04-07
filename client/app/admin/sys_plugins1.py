import json
from pathlib import Path
from tools.sql import *
from tools.db_plugins import *


_lib = Path(__file__).resolve().parent.parent.parent / "lib"


def sys_plugins1(data):
    ses = data["ses"]

    # handle add action
    if data.get("action") == "add":
        pcode = data.get("plugin_code","").strip()
        if pcode:
            plugin_add(pcode)

    # load catalog
    catalog = []
    try:
        raw = (_lib / "flyton_plugins.json").read_text(encoding="utf-8")
        catalog = json.loads(raw).get("p", [])
    except Exception:
        pass

    back_url = f"/cgi-bin/p?ses={ses}&rpage=sys_plugins"

    cards = ""
    for p in catalog:
        pname  = p.get("name","")
        pstate = p.get("state","")
        inst   = plugin_chk(pname)

        state_badge = f'<span class="mf-badge-public">Public</span>' if pstate == "public" \
                      else f'<span class="mf-badge-private">Private</span>'

        if inst:
            action_btn = '<button class="btn btn-sm btn-secondary w-100 mt-3" disabled>Installed</button>'
        else:
            add_url = f"/cgi-bin/p?ses={ses}&rpage=sys_plugins1&action=add&plugin_code={pname}"
            action_btn = f'<a href="{add_url}" class="btn btn-sm btn-success w-100 mt-3">&#43; Install</a>'

        cards += f"""
        <div class="col-sm-6 col-lg-4">
            <div class="mf-plugin-card">
                <div class="mf-plugin-icon">&#129070;</div>
                <div class="mf-plugin-name">{pname}</div>
                <div class="mt-2">{state_badge}</div>
                {action_btn}
            </div>
        </div>
        """

    if not catalog:
        cards = '<div class="text-muted px-2">No plugins found in catalog.</div>'

    h = f"""
    <div class="col-12 px-4 pt-4">
        <div class="d-flex align-items-center gap-3 mb-4">
            <a href="{back_url}" class="btn btn-outline-secondary btn-sm">&#8592; Back</a>
            <div class="mf-page-title mb-0">&#129070; Plugin Catalog</div>
        </div>
        <div class="row g-4">
            {cards}
        </div>
    </div>
    """
    return h
