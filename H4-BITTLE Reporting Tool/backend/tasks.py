# Optional background or utility tasks (e.g., scheduled backup)
import os
import json
from datetime import datetime
from models import load_applications, load_vulnerabilities

BACKUP_DIR = os.path.join(os.path.dirname(__file__), '..', 'exports', 'json_backups')
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_all_data():
    backup = {
        "timestamp": datetime.utcnow().isoformat(),
        "applications": load_applications(),
        "vulnerabilities": {}
    }

    for app in backup["applications"]:
        app_id = app["id"]
        backup["vulnerabilities"][app_id] = load_vulnerabilities(app_id)

    filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(BACKUP_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(backup, f, indent=2)

    return filepath
