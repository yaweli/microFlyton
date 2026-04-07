from tools.sql import *


def sys_admin(data):
    ses      = data["ses"]
    uid      = data["s"].get("my_user_id", 0)

    ses_row  = kic_sql(f"SELECT id, user_id, is_active, created_at, update_at FROM ses WHERE id='{ses}' LIMIT 1")
    if ses_row and len(ses_row) > 0:
        ses_id     = ses_row[0][0]
        ses_uid    = ses_row[0][1]
        ses_active = "Active" if ses_row[0][2] else "Inactive"
        ses_created = str(ses_row[0][3])[:19] if ses_row[0][3] else "—"
        ses_updated = str(ses_row[0][4])[:19] if ses_row[0][4] else "—"
    else:
        ses_id = ses
        ses_uid = uid
        ses_active = "—"
        ses_created = "—"
        ses_updated = "—"

    short_id = str(ses_id)[:8] + "..." + str(ses_id)[-6:] if len(str(ses_id)) > 16 else str(ses_id)

    h = f"""
    <div class="col-12 px-4 pt-4">
        <div class="mf-page-title">&#9881;&#65039; Admin</div>
        <div class="row">
            <div class="col-md-6 col-lg-5">
                <div class="mf-info-card">
                    <div class="mf-info-card-title">&#128274; Current Session</div>
                    <div class="mf-info-card-body">
                        <div class="mf-profile-row">
                            <span class="mf-profile-label">Session ID</span>
                            <span class="mf-profile-value mf-mono" title="{ses_id}">{short_id}</span>
                        </div>
                        <div class="mf-profile-row">
                            <span class="mf-profile-label">User ID</span>
                            <span class="mf-profile-value mf-mono">{ses_uid}</span>
                        </div>
                        <div class="mf-profile-row">
                            <span class="mf-profile-label">Status</span>
                            <span class="mf-profile-value">
                                <span class="mf-badge-active">{ses_active}</span>
                            </span>
                        </div>
                        <div class="mf-profile-row">
                            <span class="mf-profile-label">Created</span>
                            <span class="mf-profile-value">{ses_created}</span>
                        </div>
                        <div class="mf-profile-row">
                            <span class="mf-profile-label">Last Active</span>
                            <span class="mf-profile-value">{ses_updated}</span>
                        </div>
                    </div>
                    <div class="px-3 pb-3">
                        <div class="mf-ses-full-id">
                            <div class="text-muted small mb-1">Full Session Token</div>
                            <code class="mf-ses-token">{ses_id}</code>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    return h
