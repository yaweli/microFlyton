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
        else:
            action_btn = f"""<button id="plugin_install_btn_{pcode}"
                class="btn btn-sm btn-success w-100 mt-3"
                onclick="plugin_install('{pcode}','{pstate}')">&#43; Install</button>"""

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
        <div id="plugin_msg" class="text-danger mb-3"></div>
        <div class="row g-4">
            {cards}
        </div>
    </div>

    <!-- Redeem code modal -->
    <div class="modal fade" id="pluginRedeemModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">&#129070; Enter Redeem Code</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <input type="hidden" id="plugin_modal_code">
                    <label class="form-label fw-semibold">Redeem Code</label>
                    <input type="text" class="form-control text-uppercase" id="plugin_redeem_input"
                           placeholder="XXREDEEM..." oninput="this.value=this.value.toUpperCase()">
                    <div class="form-text text-muted mt-1">Enter the redeem code provided for this plugin.</div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button class="btn btn-success" onclick="submit_redeem()">&#43; Install</button>
                </div>
            </div>
        </div>
    </div>

    <script src="/lib/fly_plugins.js"></script>
    """
    return h
