from tools.sql import *


def dashboard(data):
    ses = data["ses"]

    w = kic_sql("SELECT COUNT(id) FROM users WHERE is_active=1")
    total_users = w[0][0] if w else 0

    w = kic_sql("SELECT COUNT(id) FROM ses WHERE is_active=1")
    total_ses = w[0][0] if w else 0

    h = f"""
    <div class="col-12 mt-4 px-4">
        <h4 class="mb-4 text-secondary">Dashboard</h4>
        <div class="row g-4">

            <div class="col-md-4">
                <div class="card text-white bg-primary shadow h-100">
                    <div class="card-body d-flex justify-content-between align-items-center">
                        <div>
                            <div class="text-uppercase small opacity-75">Total Users</div>
                            <div class="display-5 fw-bold">{total_users}</div>
                        </div>
                        <div class="fs-1 opacity-50">&#128100;</div>
                    </div>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card text-white bg-success shadow h-100">
                    <div class="card-body d-flex justify-content-between align-items-center">
                        <div>
                            <div class="text-uppercase small opacity-75">Active Sessions</div>
                            <div class="display-5 fw-bold">{total_ses}</div>
                        </div>
                        <div class="fs-1 opacity-50">&#128274;</div>
                    </div>
                </div>
            </div>

        </div>
    </div>
    """
    return h
