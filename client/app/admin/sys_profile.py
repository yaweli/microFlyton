from tools.sql import *


def sys_profile(data):
    ses = data["ses"]
    uid = data["s"].get("my_user_id", 0)

    urow = kic_sql(f"SELECT username, FirstName, LastName, Roles, created_at FROM users WHERE id={int(uid)} LIMIT 1")
    if urow and len(urow) > 0:
        username   = urow[0][0] or ""
        firstname  = urow[0][1] or ""
        lastname   = urow[0][2] or ""
        roles_raw  = urow[0][3] or "[]"
        created_at = urow[0][4] or ""
        display    = f"{firstname} {lastname}".strip() or username
        initials   = ((firstname[:1] + lastname[:1]) or username[:2]).upper()
        import json
        try:
            roles = ", ".join(json.loads(roles_raw))
        except Exception:
            roles = str(roles_raw)
    else:
        display = username = initials = "?"
        roles = ""
        created_at = ""

    h = f"""
    <div class="col-12 px-4 pt-4">
        <div class="mf-page-title">&#128100; Profile</div>
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-5">
                <div class="mf-profile-card">
                    <div class="mf-profile-banner"></div>
                    <div class="mf-profile-body">
                        <div class="mf-avatar mf-avatar-lg mf-profile-avatar">{initials}</div>
                        <div class="mf-profile-name">{display}</div>
                        <div class="mf-profile-username text-muted">@{username}</div>

                        <div class="mf-profile-fields mt-4">
                            <div class="mf-profile-row">
                                <span class="mf-profile-label">First Name</span>
                                <span class="mf-profile-value">{firstname or "—"}</span>
                            </div>
                            <div class="mf-profile-row">
                                <span class="mf-profile-label">Last Name</span>
                                <span class="mf-profile-value">{lastname or "—"}</span>
                            </div>
                            <div class="mf-profile-row">
                                <span class="mf-profile-label">Username</span>
                                <span class="mf-profile-value">{username}</span>
                            </div>
                            <div class="mf-profile-row">
                                <span class="mf-profile-label">Roles</span>
                                <span class="mf-profile-value">{roles or "—"}</span>
                            </div>
                            <div class="mf-profile-row">
                                <span class="mf-profile-label">Member Since</span>
                                <span class="mf-profile-value">{str(created_at)[:10] if created_at else "—"}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    return h
