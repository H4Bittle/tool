import os
import json
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
APPS_DIR = os.path.join(DATA_DIR, 'applications')
VULNS_DIR = os.path.join(DATA_DIR, 'vulnerabilities')

os.makedirs(APPS_DIR, exist_ok=True)
os.makedirs(VULNS_DIR, exist_ok=True)

def load_applications():
    applications = []
    for filename in os.listdir(APPS_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(APPS_DIR, filename), 'r') as f:
                applications.append(json.load(f))
    return applications

def format_ddmmyyyy(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except:
        return date_str

def save_application(app_data):
    app_id = app_data.get('id')
    if not app_id:
        app_id = f"app_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        app_data['id'] = app_id

    # ✅ Format start_date and end_date to DD-MM-YYYY
    if "start_date" in app_data:
        app_data["start_date"] = format_ddmmyyyy(app_data["start_date"])
    if "end_date" in app_data:
        app_data["end_date"] = format_ddmmyyyy(app_data["end_date"])

    filepath = os.path.join(APPS_DIR, f"{app_id}.json")
    with open(filepath, 'w') as f:
        json.dump(app_data, f, indent=2)

def load_vulnerabilities(app_id):
    filepath = os.path.join(VULNS_DIR, f"{app_id}.json")
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return json.load(f)

def save_vulnerability(app_id, vuln_data, modified_by="system"):
    filepath = os.path.join(VULNS_DIR, f"{app_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
    else:
        data = []

    vuln_data['created_at'] = datetime.utcnow().isoformat()
    vuln_data['modified_by'] = modified_by
    data.append(vuln_data)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def save_vulnerabilities(app_id, data):
    """Overwrite all vulnerabilities for a given application ID."""
    filepath = os.path.join(VULNS_DIR, f"{app_id}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
