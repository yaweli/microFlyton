from tools.sql import *
from tools.db_users import *
from tools.kicutil import *


def _nav_item(ses, page, tab, current_page, user_id):
    name = tab.get("name", page)

    if not is_page_allowed(page, user_id):
        return ""

    active_cls = "active" if page == current_page else ""

    return f'<li class="nav-item"><a class="nav-link {active_cls}" href="/cgi-bin/p?ses={ses}&rpage={page}">{name}</a></li>'


def header(data):
    ses          = data["ses"]
    current_page = data.get("rpage", data["s"].get("page", "dashboard"))
    uid          = data["s"].get("my_user_id", 0)

    # user display info
    urow = kic_sql(f"SELECT username, FirstName, LastName FROM users WHERE id={int(uid)} LIMIT 1")
    if urow:
        username  = urow[0][0] or ""
        firstname = urow[0][1] or ""
        lastname  = urow[0][2] or ""
        display   = f"{firstname} {lastname}".strip() or username
        initials  = ((firstname[:1] + lastname[:1]) or username[:2]).upper()
    else:
        username  = ""
        display   = "User"
        initials  = "U"

    # load pages from gen id=31
    g         = gen_data()
    pages_obj = g.get("pages", {}).get("data", {}) or {}
    pages     = sorted(pages_obj.items(), key=lambda kv: kv[1].get("order", 99))
    nav_items = "".join(_nav_item(ses, page, tab, current_page, uid) for page, tab in pages)

    # resolve cust_id: from user data -> write to session if missing
    user_data = get_data("users", uid)
    cust_id   = user_data.get("cust_id", None)
    if cust_id and not data["s"].get("cust_id"):
        add_to_data("ses", ses, "cust_id", cust_id)
        data["s"]["cust_id"] = cust_id
    cust_id = data["s"].get("cust_id", cust_id)

    # brand title: customer name if cust table + record exist, else fallback
    brand_name = "MicroFlyton"
    if cust_id:
        cust_row = find_in_sql({'table': 'cust', 'fld': 'id', 'val': int(cust_id), 'what': 'name'})
        if cust_row and type(cust_row) is tuple:
            brand_name = cust_row[0] or brand_name

    project_name = g.get("name", {}).get("val", "")
    project_html = f'<span class="text-white-50 me-2" style="font-size:13px;">{project_name}</span>' if project_name else ""

    is_privileged = is_admin(uid) or is_owner(uid)

    settings_item = f'<li><a class="dropdown-item" href="/cgi-bin/p?ses={ses}&rpage=sys_admin">&#9881;&#65039;&nbsp; Admin</a></li>' if is_privileged else ""
    plugins_item  = f'<li><a class="dropdown-item" href="/cgi-bin/p?ses={ses}&rpage=sys_plugins">&#129070;&nbsp; Plugins</a></li>' if is_privileged else ""

    print(f"""
     {kicbutton0()} 
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-3">
        <a class="navbar-brand fw-bold" href="/cgi-bin/p?ses={ses}&rpage=dashboard">
            &#9670; {brand_name}
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navmenu">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navmenu">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                {nav_items}
            </ul>
            <div class="d-flex align-items-center gap-3">
                {project_html}
                <div class="dropdown">
                    <div class="mf-avatar" data-bs-toggle="dropdown" aria-expanded="false" title="{display}">
                        {initials}
                    </div>
                    <ul class="dropdown-menu dropdown-menu-end mf-avatar-menu shadow">
                        <li class="mf-avatar-menu-header px-3 py-2">
                            <div class="mf-avatar mf-avatar-sm mx-auto mb-1">{initials}</div>
                            <div class="fw-semibold text-center small">{display}</div>
                            <div class="text-muted text-center" style="font-size:.75rem">@{username if urow else display}</div>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="/cgi-bin/p?ses={ses}&rpage=sys_profile">&#128100;&nbsp; Profile</a></li>
                        {settings_item}
                        {plugins_item}
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item text-danger" href="/pages/index.html">&#128275;&nbsp; Logout</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </nav>
    """)
