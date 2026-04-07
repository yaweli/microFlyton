from tools.sql import *


def header(data):
    ses  = data["ses"]
    page = data["s"]["page"]

    dash_active  = ""
    users_active = ""
    if page == "dashboard": dash_active  = "active"
    if page == "users":     users_active = "active"

    print(f"""
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-3">
        <a class="navbar-brand fw-bold" href="/cgi-bin/p?ses={ses}&rpage=dashboard">
            &#9670; MicroFlyton
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navmenu">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id=navmenu>
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                <li class="nav-item">
                    <a class="nav-link {dash_active}" href="/cgi-bin/p?ses={ses}&rpage=dashboard">Dashboard</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {users_active}" href="/cgi-bin/p?ses={ses}&rpage=users">Users</a>
                </li>
            </ul>
            <a class="btn btn-outline-light btn-sm" href="/pages/index.html">Logout</a>
        </div>
    </nav>
    """)
