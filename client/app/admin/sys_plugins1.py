import json
from pathlib import Path
from tools.sql import *
from tools.db_plugins import *

_lib = Path(__file__).resolve().parent.parent.parent / "lib"


def sys_plugins1(data):
    ses = data["ses"]

    try:
        raw     = (_lib / "flyton_plugins.json").read_text(encoding="utf-8")
        catalog = json.loads(raw).get("p", [])
    except Exception:
        catalog = []

    back_url = f"/cgi-bin/p?ses={ses}&rpage=sys_plugins"

    cards = ""
    for p in catalog:
        pcode  = p.get("code", "")
        pname  = p.get("name", "")
        pstate = p.get("state", "public")
        inst   = plugin_chk(pcode)

        state_badge = f'<span class="mf-badge-public">Public</span>' if pstate == "public" \
                      else f'<span class="mf-badge-private">Private</span>'

        if inst:
            action_btn = '<button class="btn btn-sm btn-secondary w-100 mt-3" disabled>Installed</button>'
        elif pstate == "public":
            install_url = f"/cgi-bin/p?ses={ses}&rpage=sys_plugins2&plugin_code={pcode}"
            action_btn  = f'<a href="{install_url}" class="btn btn-sm btn-success w-100 mt-3">&#43; Install</a>'
        else:
            action_btn = f"""
                <button class="btn btn-sm btn-success w-100 mt-3"
                        onclick="document.getElementById('rf_{pcode}').style.display='block';this.style.display='none'">
                    &#43; Install
                </button>
                <div id="rf_{pcode}" style="display:none" class="mt-3">
                    <input type="text" id="rc_{pcode}" class="form-control mb-2"
                           placeholder="Enter Redeem Code"
                           oninput="this.value=this.value.toUpperCase()">
                    <a href="#" onclick="go_install('{pcode}','{ses}')"
                       class="btn btn-sm btn-success w-100">Confirm</a>
                </div>"""

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
    <script src="/lib/fly_plugins.js"></script>
    """
    return h
