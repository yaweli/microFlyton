import json, random, string, urllib.request
from pathlib import Path
from tools.sql import *
from tools.db_plugins import *

_LIB = Path(__file__).resolve().parent.parent.parent.parent / "client" / "lib"


def _load_catalog():
    try:
        raw = (_LIB / "flyton_plugins.json").read_text(encoding="utf-8")
        return {p["code"]: p for p in json.loads(raw).get("p", [])}
    except Exception:
        return {}


def _rand_char():
    return random.choice(string.ascii_letters)


def _encode_password(pw, skip):
    result = ""
    for ch in pw:
        result += ch
        for _ in range(skip - 1):
            result += _rand_char()
    extra = random.randint(9, 15)
    for _ in range(extra):
        result += _rand_char()
    return result


def _build_plp(pw, pcode):
    skip          = random.randint(1, 9)
    total_digits  = random.randint(6, 11)
    middle_count  = total_digits - 3
    middle        = "".join(str(random.randint(0, 9)) for _ in range(middle_count))
    num           = f"{len(pw):02d}{middle}{skip}"
    encoded_pw    = _encode_password(pw, skip)
    return f"{num}/{pcode}/{encoded_pw}"


def _call_verify(plp):
    url = f"https://x.yaw.red/cgi-bin/micro_f_plugin?PlP={plp}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MicroFlyton/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"err": str(e)}


def api_plugin_install(data):
    i      = data["post"]["input"]
    pcode  = i.get("plugin_code", "").strip()
    redeem = i.get("redeem", "").strip()

    catalog = _load_catalog()
    entry   = catalog.get(pcode)
    if not entry:
        print('"allow":0,"err":"unknown plugin"')
        return

    state = entry.get("state", "public")

    if state == "public":
        pw = "eli"
    else:
        if len(redeem) <= 2:
            print('"allow":0,"err":"invalid redeem code"')
            return
        pw = redeem[2:]

    plp  = _build_plp(pw, pcode)
    resp = _call_verify(plp)

    if "err" in resp:
        msg = str(resp["err"]).replace('"', "'")
        print(f'"allow":0,"err":"{msg}"')
        return

    if resp.get("pas1") != "OK":
        print('"allow":0,"err":"verification failed"')
        return

    plugin_url = resp.get("url", "")

    result = plugin_add(pcode)
    if not result.get("status") and result.get("err") == "already installed":
        print('"allow":0,"err":"plugin already installed"')
        return

    if plugin_url:
        w = find_in_sql({'table': 'plugins', 'fld': 'plugin_code', 'val': pcode, 'what': 'id'})
        if w:
            add_to_data("plugins", w[0], "url", plugin_url)

    print(f'"allow":1,"plugin_code":"{pcode}"')
