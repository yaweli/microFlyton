// MicroFlyton - Plugin install flow
// (c) KICDEV 2025

async function plugin_install(pcode, state) {
    go_el('plugin_msg').innerText = '';

    if (state !== 'public') {
        go_el('plugin_modal_code').value = pcode;
        go_el('plugin_redeem_input').value = '';
        go_clean(go_el('plugin_redeem_input'));
        new bootstrap.Modal(go_el('pluginRedeemModal')).show();
        return;
    }

    await do_plugin_install(pcode, '');
}

function submit_redeem() {
    let pcode  = go_el('plugin_modal_code').value;
    let redeem = go_el('plugin_redeem_input').value.trim().toUpperCase();
    if (redeem.length <= 2) {
        go_red(go_el('plugin_redeem_input'));
        return;
    }
    bootstrap.Modal.getInstance(go_el('pluginRedeemModal')).hide();
    do_plugin_install(pcode, redeem);
}

async function do_plugin_install(pcode, redeem) {
    let btn = go_el('plugin_install_btn_' + pcode);
    if (btn) { btn.disabled = true; btn.innerText = 'Installing...'; }

    let res = await call_server('api_plugin_install', {plugin_code: pcode, redeem: redeem});
    let s   = res && res.server ? res.server : null;
    let msg = go_el('plugin_msg');

    if (!s || !s.allow) {
        let err = s ? (s.err || 'Install failed') : 'Server error';
        if (msg) msg.innerText = err;
        if (btn) { btn.disabled = false; btn.innerText = '+ Install'; }
        return;
    }

    if (msg) msg.innerText = '';
    location.reload();
}
