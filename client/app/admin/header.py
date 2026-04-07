from tools.sql import *


def header(data):
    ses  = data["ses"]
    page = data["s"]["page"]
    uid  = data["s"].get("my_user_id", 0)

    dash_active  = ""
    users_active = ""
    if page == "dashboard": dash_active  = "active"
    if page == "users":     users_active = "active"

    # fetch user display name
    urow = kic_sql(f"SELECT username, FirstName, LastName FROM users WHERE id={int(uid)} LIMIT 1")
    if urow and len(urow) > 0:
        username  = urow[0][0] or ""
        firstname = urow[0][1] or ""
        lastname  = urow[0][2] or ""
        display   = f"{firstname} {lastname}".strip() or username
        initials  = ((firstname[:1] + lastname[:1]) or username[:2]).upper()
    else:
        display  = "User"
        initials = "U"

    print(f"""
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-3">
        <a class="navbar-brand fw-bold" href="/cgi-bin/p?ses={ses}&rpage=dashboard">
            &#9670; MicroFlyton
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navmenu">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navmenu">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                <li class="nav-item">
                    <a class="nav-link {dash_active}" href="/cgi-bin/p?ses={ses}&rpage=dashboard">Dashboard</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {users_active}" href="/cgi-bin/p?ses={ses}&rpage=users">Users</a>
                </li>
            </ul>
            <div class="d-flex align-items-center gap-3">
                <a class="btn btn-outline-light btn-sm" href="/pages/index.html">Logout</a>
                <div class="mf-avatar" data-bs-toggle="modal" data-bs-target="#userModal" title="{display}">
                    {initials}
                </div>
            </div>
        </div>
    </nav>

    <!-- User modal -->
    <div class="modal fade" id="userModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" style="max-width:320px">
            <div class="modal-content mf-user-modal">
                <div class="modal-body text-center py-4">
                    <div class="mf-avatar mf-avatar-lg mx-auto mb-3">{initials}</div>
                    <div class="mf-modal-name">{display}</div>
                    <div class="mf-modal-role text-muted small mt-1">@{username if urow else display}</div>
                    <a href="/pages/index.html" class="btn btn-sm btn-outline-danger mt-3 w-100">Logout</a>
                </div>
            </div>
        </div>
    </div>
    """)
