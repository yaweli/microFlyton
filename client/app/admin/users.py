from tools.sql import *


def users(data):
    rows = ""
    id   = ""
    for u in sql_order({'table': 'users', 'id': id}):
        id     = u["id"]
        active = '<span class="mf-badge-active">Active</span>' if u["is_active"] else \
                 '<span class="text-muted small">Inactive</span>'
        rows += f"""
        <tr>
            <td class="text-muted small">{u["id"]}</td>
            <td>{u["username"] or ""}</td>
            <td>{u["FirstName"] or ""}</td>
            <td>{u["LastName"] or ""}</td>
            <td class="text-muted small">{str(u["created_at"])[:10] if u["created_at"] else "—"}</td>
            <td>{active}</td>
        </tr>"""

    if not rows:
        rows = '<tr><td colspan="6" class="text-center text-muted py-4">No users found.</td></tr>'

    h = f"""
    <div class="col-12 px-4 pt-4">
        <div class="mf-page-title">&#128100; Users</div>
        <div class="card border-0 shadow-sm">
            <div class="table-responsive">
    Users version : 0.099
                <table class="table table-hover mb-0">
                    <thead class="table-dark">
                        <tr>
                            <th>#</th>
                            <th>Username</th>
                            <th>First Name</th>
                            <th>Last Name</th>
                            <th>Created</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    """
    return h
