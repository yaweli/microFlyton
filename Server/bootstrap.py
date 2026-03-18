from config import ENV_SOURCE, MACHINE_ID
from db import init_db, log_event

if __name__ == "__main__":
    init_db()
    log_event("INFO", "bootstrap", "Bootstrap completed", {"env_source": ENV_SOURCE, "machine_id": MACHINE_ID}, source="bootstrap")
    print("Bootstrap completed.")
