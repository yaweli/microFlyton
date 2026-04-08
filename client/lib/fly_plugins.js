// MicroFlyton - Plugin helpers
// (c) KICDEV 2025

function go_install(pcode, ses) {
    var redeem = document.getElementById('rc_' + pcode).value.trim().toUpperCase();
    if (redeem.length <= 2) {
        go_red(document.getElementById('rc_' + pcode));
        return;
    }
    location.href = '/cgi-bin/p?ses=' + ses + '&rpage=sys_plugins2&plugin_code=' + pcode + '&redeem=' + encodeURIComponent(redeem);
}
