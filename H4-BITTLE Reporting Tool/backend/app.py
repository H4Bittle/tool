from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file 
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta, datetime
import os
import json
import traceback

from backend.auth import authenticate, load_user, User
from backend.forms import LoginForm
from backend.models import (
    load_applications, save_application,
    load_vulnerabilities, save_vulnerability
)
from backend.utils import (
    generate_word_report, generate_excel_report,
    log_action
)

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=30)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

csrf = CSRFProtect(app)

# ================= USER LOADER =====================
@login_manager.user_loader
def user_loader(user_id):
    data = load_user(user_id)
    if data:
        return User(data['username'], data['password'])
    return None

# ================= HOME ============================
@app.route('/')
def home():
    return redirect(url_for('login'))

# ================= LOGIN ===========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if authenticate(username, password):
            data = load_user(username)
            user = User(data['username'], data['password'])
            login_user(user)
            session.permanent = True
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ================= DASHBOARD ========================
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ========== APPLICATION ROUTES ======================
@app.route('/applications', methods=['GET'])
@login_required
def applications_page():
    apps = load_applications()
    return render_template('applications.html', applications=apps)

@app.route('/api/applications', methods=['GET'])
@login_required
def get_applications_api():
    apps = load_applications()
    simplified = []
    for app in apps:
        simplified.append({
            "id": app.get("id"),
            "name": app.get("name"),
            "status": app.get("status", "").lower(),
            "start_date": app.get("start_date", ""),
            "end_date": app.get("end_date", "")
        })
    return jsonify(simplified)

@app.route('/api/applications_summary', methods=['GET'])
@login_required
def applications_summary_api():
    apps = load_applications()

    total = len(apps)
    completed = 0
    in_progress = 0

    # Always return Jan..Dec
    monthly = [0] * 12

    def parse_date(app):
        v = (app.get("start_date") or "").strip()
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(v, fmt)
            except Exception:
                pass
        # optional fallback: file mtime of this app's json (comment out if not desired)
        try:
            app_id = app.get("id")
            if app_id:
                p = os.path.join("backend", "data", "applications", f"{app_id}.json")
                if os.path.isfile(p):
                    return datetime.fromtimestamp(os.path.getmtime(p))
        except Exception:
            pass
        return None

    for app in apps:
        status = (app.get("status") or "").lower()
        if status in ("completed",):
            completed += 1
        elif status in ("in-progress", "in progress", "inprogress"):
            in_progress += 1

        dt = parse_date(app)
        if dt:
            monthly[dt.month - 1] += 1

    return jsonify({
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "monthly": monthly
    })


    for app in apps:
        summary["total"] += 1
        status = (app.get("status") or "").lower()
        if status == "completed":
            summary["completed"] += 1
        elif status == "in-progress":
            summary["in_progress"] += 1

        try:
            date_obj = datetime.strptime(app.get("start_date", ""), "%Y-%m-%d")
            month_name = date_obj.strftime("%b")
            if month_name in summary["monthly"]:
                summary["monthly"][month_name] += 1
        except:
            pass

    return jsonify(summary)

@app.route('/api/applications/<app_id>/status', methods=['POST'])
@login_required
def update_status_only(app_id):
    try:
        data = request.get_json()
        valid_statuses = {
            "inprogress": "in-progress",
            "in-progress": "in-progress",
            "in progress": "in-progress",
            "completed": "completed",
            "onhold": "on-hold",
            "on-hold": "on-hold",
            "on hold": "on-hold",
            "cancelled": "cancelled"
        }

        new_status_input = (data.get("status") or "").strip().lower()
        if new_status_input not in valid_statuses:
            return jsonify({"success": False, "message": "Invalid status"}), 400

        final_status = valid_statuses[new_status_input]

        applications = load_applications()
        for i, app in enumerate(applications):
            if app.get("id") == app_id:
                applications[i]["status"] = final_status
                save_application(applications[i])
                log_action(f"Updated status of {app_id} to {final_status}")
                return jsonify({"success": True})

        return jsonify({"success": False, "message": "Application not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/add_application', methods=['GET'])
@login_required
def add_application_page():
    return render_template('add_application.html')

@app.route('/add_application', methods=['POST'])
@login_required
def add_application():
    if request.content_type != 'application/json':
        return jsonify({"error": "Unsupported Content-Type"}), 415
    data = request.get_json()
    new_app = {
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description", ""),
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date"),
        "status": data.get("status", "in-progress"),
        "app_details": data.get("app_details", []),
        "pentesters": data.get("pentesters", []),
        "test_credentials": data.get("test_credentials", [])
    }
    save_application(new_app)
    log_action(f"Application added: {new_app['name']}")
    return jsonify({"success": True})

@app.route('/applications/<app_id>/edit', methods=['GET'])
@login_required
def edit_application_page(app_id):
    applications = load_applications()
    app_data = next((a for a in applications if a["id"] == app_id), None)
    if not app_data:
        return "Application not found", 404
    return render_template('edit_application.html', application=app_data)

@app.route('/api/applications/<app_id>/update', methods=['POST'])
@login_required
def update_application(app_id):
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"success": False, "message": "Empty request body"}), 400

        applications = load_applications()
        for i, app in enumerate(applications):
            if app.get("id") == app_id:
                applications[i]["name"] = data.get("name", app.get("name", ""))
                applications[i]["start_date"] = data.get("start_date", app.get("start_date", ""))
                applications[i]["end_date"] = data.get("end_date", app.get("end_date", ""))
                applications[i]["status"] = data.get("status", app.get("status", ""))
                applications[i]["app_details"] = data.get("app_details", app.get("app_details", []))
                applications[i]["pentesters"] = data.get("pentesters", app.get("pentesters", []))
                applications[i]["test_credentials"] = data.get("test_credentials", app.get("test_credentials", []))

                save_application(applications[i])
                log_action(f"Application updated: {app_id}")
                return jsonify({"success": True})

        return jsonify({"success": False, "message": "Application not found"}), 404

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

# ========== VULNERABILITY ROUTES ====================

@app.route('/add_vulnerability/<app_id>', methods=['GET'])
@login_required
def add_vulnerability_page(app_id):
    return render_template('add_vulnerability.html', app_id=app_id)

from werkzeug.utils import secure_filename
from backend.models import save_vulnerabilities, load_vulnerabilities
from backend.utils import log_action

SCREENSHOT_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'screenshots')
os.makedirs(SCREENSHOT_UPLOAD_DIR, exist_ok=True)

@app.route('/add_vulnerability', methods=['POST'])
@login_required
def add_vulnerability():
    # ========== DEBUGGING SECTION ==========
    print("\n==== /add_vulnerability submission ====")
    print("Form keys:", list(request.form.keys()))
    print("File keys:", list(request.files.keys()))
    # =======================================

    if 'vulnerabilities' not in request.form or 'application_id' not in request.form:
        print("Missing required data in request.form")
        return jsonify({"success": False, "message": "Missing required data"}), 400

    try:
        app_id = request.form['application_id']
        vuln_data = json.loads(request.form['vulnerabilities'])
    except Exception as e:
        print("Failed to parse vulnerabilities or application_id:", e)
        return jsonify({"success": False, "message": "Invalid payload", "error": str(e)}), 400

    # Load previously saved vulnerabilities for the app
    existing = load_vulnerabilities(app_id)

    for v_idx, vuln in enumerate(vuln_data):
        for s_idx, step in enumerate(vuln.get("steps", [])):
            screenshot_filename = step.get("screenshot")
            print(f"Vuln {v_idx} Step {s_idx} expects screenshot field: '{screenshot_filename}'")
            if screenshot_filename:
                if screenshot_filename in request.files:
                    file = request.files[screenshot_filename]
                    safe_name = secure_filename(screenshot_filename)
                    save_path = os.path.join(SCREENSHOT_UPLOAD_DIR, safe_name)
                    try:
                        file.save(save_path)
                        print(f"Saved screenshot: {safe_name} -> {save_path}")
                    except Exception as file_save_exc:
                        print(f"ERROR: Could not save {safe_name}: {file_save_exc}")
                        step["screenshot"] = ""  # Mark as missing if failed to save
                else:
                    print(f"WARNING: Screenshot '{screenshot_filename}' not found in uploaded files ({list(request.files.keys())})")
                    step["screenshot"] = ""  # No file found, clear to avoid JSON/file mismatch

        existing.append(vuln)

    # Save all vulnerabilities back
    save_vulnerabilities(app_id, existing)
    log_action(f"Vulnerabilities added for app {app_id}")
    print("==== /add_vulnerability done ====")
    return jsonify({"success": True})

@app.route('/applications/<app_id>/vulnerabilities', methods=['GET'])
@login_required
def get_vulnerabilities(app_id):
    vulns = load_vulnerabilities(app_id)
    return jsonify(vulns)

# ======== REPLACE ONLY THIS ROUTE IN app.py =========
@app.route('/applications/<app_id>/vulnerabilities/update', methods=['POST'])
@login_required
def update_vulnerabilities_route(app_id):
    """
    Supports your existing edit_vulnerabilities.html UI:
      - multipart/form-data with field 'vulnerabilities' (JSON string)
      - optional uploaded files (keys must match the 'screenshot' names you set)
    """
    try:
        # 1) Parse JSON payload from form field
        raw = request.form.get('vulnerabilities')
        if not raw:
            # also allow JSON body as fallback
            payload = request.get_json(silent=True)
            if payload is None:
                return jsonify({"success": False, "message": "No vulnerabilities JSON provided."}), 400
        else:
            try:
                payload = json.loads(raw)
            except Exception as e:
                return jsonify({"success": False, "message": f"Invalid JSON in 'vulnerabilities': {e}"}), 400

        if not isinstance(payload, list):
            return jsonify({"success": False, "message": "Payload must be a JSON array."}), 400

        # 2) For each step, if a file with that key exists in request.files, save it
        saved_any = False
        for v in payload:
            steps = v.get("steps", [])
            if not isinstance(steps, list):
                v["steps"] = steps = []
            for s in steps:
                name = (s.get("screenshot") or "").strip()
                if not name:
                    continue
                if name in request.files:
                    f = request.files[name]
                    if not f or not getattr(f, "filename", ""):
                        continue
                    safe = secure_filename(name)  # preserves your generated key pattern
                    out_path = os.path.join(SCREENSHOT_UPLOAD_DIR, safe)
                    os.makedirs(SCREENSHOT_UPLOAD_DIR, exist_ok=True)
                    f.save(out_path)
                    # store just the filename (your UI links to /static/screenshots/<filename>)
                    s["screenshot"] = safe
                    saved_any = True
                else:
                    # If no file uploaded under that key, leave the existing value as-is
                    # (your UI already sets it to empty if nothing provided)
                    pass

        # 3) Save entire list back to JSON
        save_vulnerabilities(app_id, payload)
        log_action(f"Vulnerabilities updated for app {app_id}. files_saved={saved_any}")
        return jsonify({"success": True, "count": len(payload)})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500
# ======== END REPLACEMENT =========

# ======== END FIX =======================================

@app.route('/vulnerabilities_summary', methods=['GET'])
@login_required
def vulnerabilities_summary_page():
    summary = {"total": 0, "info": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
    apps = load_applications()
    for app in apps:
        vulns = load_vulnerabilities(app["id"])
        for v in vulns:
            sev = (v.get("severity") or '').lower()
            summary["total"] += 1
            if sev in summary:
                summary[sev] += 1
    return render_template("vulnerabilities_summary.html", summary=summary)

@app.route('/api/vulnerabilities_summary', methods=['GET'])
@login_required
def vulnerabilities_summary_api():
    summary = {"total": 0, "info": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
    apps = load_applications()
    for app in apps:
        vulns = load_vulnerabilities(app["id"])
        for v in vulns:
            sev = (v.get("severity") or '').lower()
            summary["total"] += 1
            if sev in summary:
                summary[sev] += 1
    return jsonify(summary)

@app.route('/vulnerability_templates', methods=['GET'])
@login_required
def get_templates():
    try:
        with open("backend/data/templates/vuln_templates.json") as f:
            return jsonify(json.load(f))
    except Exception:
        return jsonify([])

@app.route("/edit_vulnerabilities/<app_id>")
@login_required
def edit_vulnerabilities(app_id):
    app_file = os.path.join("backend", "data", "applications", f"{app_id}.json")
    vuln_file = os.path.join("backend", "data", "vulnerabilities", f"{app_id}.json")

    if not os.path.exists(app_file):
        print("App file not found:", app_file)
        return render_template("404.html"), 404

    with open(app_file) as f:
        app_data = json.load(f)

    if os.path.exists(vuln_file):
        with open(vuln_file) as f:
            try:
                vulns = json.load(f)
                print(f"Loaded {len(vulns)} vulnerabilities for app {app_id}: {vulns}")
            except Exception as e:
                print(f"Error loading vulnerabilities JSON: {e}")
                vulns = []
    else:
        print("Vulnerability file not found:", vuln_file)
        vulns = []

    return render_template("edit_vulnerabilities.html", app=app_data, app_id=app_id, vulnerabilities=vulns)



# ========== EXPORT ROUTES ===========================
@app.route('/export/word/<app_id>', methods=['GET'])
@login_required
def export_word(app_id):
    try:
        path = generate_word_report(app_id)
        if path:
            return jsonify({"message": "Word report generated", "path": path})
        else:
            return jsonify({"message": "Failed to generate Word report"}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": f"Export failed: {str(e)}"}), 500

@app.route('/export/excel/<app_id>', methods=['GET'])
@login_required
def export_excel(app_id):
    try:
        path = generate_excel_report(app_id)
        if path:
            return jsonify({"message": "Excel report generated", "path": path})
        else:
            return jsonify({"message": "Failed to generate Excel report"}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": f"Export failed: {str(e)}"}), 500

@app.route('/exports/word_reports/<filename>')
@login_required
def download_word_report(filename):
    full_path = os.path.join(os.path.dirname(__file__), '..', 'exports', 'word_reports', filename)
    if not os.path.exists(full_path):
        return render_template("404.html"), 404
    return send_file(full_path, as_attachment=True)

# ========== ERROR HANDLING ==========================
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

# ========== MAIN ====================================
if __name__ == '__main__':
    app.run(debug=True)
