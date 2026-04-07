from tools.sql import *


def dashboard(data):
    ses = data["ses"]

    w = kic_sql("SELECT COUNT(id) FROM users WHERE is_active=1")
    total_users = w[0][0] if w else 0

    w = kic_sql("SELECT COUNT(id) FROM ses WHERE is_active=1")
    total_ses = w[0][0] if w else 0

    h = f"""
    <div class="col-12 px-4 pt-4">
        <div class="mf-page-title">&#128202; Dashboard</div>
        <div class="row g-4">

            <div class="col-sm-6 col-xl-4">
                <div class="mf-stat-card blue">
                    <div class="mf-stat-icon">&#128100;</div>
                    <div class="mf-stat-info">
                        <div class="mf-stat-label">Total Users</div>
                        <div class="mf-stat-value">{total_users}</div>
                    </div>
                </div>
            </div>

            <div class="col-sm-6 col-xl-4">
                <div class="mf-stat-card green">
                    <div class="mf-stat-icon">&#128274;</div>
                    <div class="mf-stat-info">
                        <div class="mf-stat-label">Active Sessions</div>
                        <div class="mf-stat-value">{total_ses}</div>
                    </div>
                </div>
            </div>

        </div>
    </div>
    """
    return h
