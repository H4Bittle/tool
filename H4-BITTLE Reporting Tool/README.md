🛡️ H4 B.I.T.T.L.E – Hackers for Bug Identification, Triage, Tracking, Logging & Export
A full-featured penetration testing reporting tool designed for structured, secure, and rich reporting of web application vulnerabilities with Word/Excel export support — built for local use by pentest teams.

🚀 Features
🔐 Secure Login (1 environment, 1 role) with bcrypt-hashed credentials in JSON

🧠 Add & Manage Applications (with version, scope URLs, start/end dates, test credentials)

🐞 Add & Edit Detailed Vulnerabilities

🗕 Separate Application & Vulnerability Flows

👤 Pentester Info (Name, Role, Email)

⚠️ 12-step Reproduction with Screenshot Uploads

📊 Dashboard with CVSS analytics (per app + monthly trends)

💃 Export Word/Excel Reports (exact template formatting)

📁 JSON-based storage (no DB, easy backups)

🔄 Dynamic Add/Remove Vulnerability & Steps in both Add and Edit pages

🖼️ Embedded screenshots in exported reports (if paths valid)

📁 Directory Structure
csharp
Copy
Edit
H4-BITTLE/
├── backend/
│   ├── app.py                # Flask app, routes, API endpoints
│   ├── auth.py               # Login/session handling
│   ├── forms.py              # Flask-WTF forms (CSRF, validation)
│   ├── models.py             # JSON read/write helpers
│   ├── tasks.py              # (Optional) backups/scheduled ops
│   ├── utils.py              # Word/Excel export, logging
│   ├── data/
│   │   ├── users.json               # Login credentials (bcrypt hash)
│   │   ├── audit_logs.json          # Activity logs
│   │   ├── applications/            # Per-app JSON metadata
│   │   ├── vulnerabilities/         # Per-app vuln JSON
│   │   └── templates/vuln_templates.json
│   └── templates/
│       ├── report_template.docx     # Word report format
│       └── excel_template.xlsx      # Excel export format
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── applications.html
│   ├── add_application.html
│   ├── edit_application.html
│   ├── add_vulnerability.html
│   ├── edit_vulnerabilities.html
│   ├── profile.html
│   └── 404.html
├── static/
│   ├── css/
│   │   ├── styles.css
│   │   └── theme.css
│   ├── js/
│   │   ├── page_logic_handler.js
│   │   ├── analytics_viewer.js
│   │   ├── sidebar_updater.js
│   │   ├── export_buttons.js
│   │   └── validation.js
│   └── screenshots/                  # Uploaded proof images
├── exports/
│   ├── word_reports/
│   ├── excel_exports/
│   └── json_backups/
├── requirements.txt
├── run.py
├── run.bat                           # Windows run script
└── run.sh                            # Linux/macOS run script
⚙️ Installation
Windows
bat
Copy
Edit
run.bat
Linux/macOS
bash
Copy
Edit
chmod +x run.sh
./run.sh
These scripts:

Create/activate virtual environment

Upgrade pip

Install dependencies if missing

Start the Flask app

🔑 Credentials
Stored in:

bash
Copy
Edit
backend/data/users.json
No hardcoded defaults. Admin must set username/password before first run.
Passwords are bcrypt-hashed.

📝 Reporting Format
Cover Page: Application name in Verdana 28

Summary Table: Vulnerability ID, Title, CVSS, Risk (Verdana 10)

Dates Table: Start/End date

URLs Table: App/API name, version, tested URL

Detailed Findings: Full structured table + 12-step PoC + Screenshots

Exported via: report_template.docx & excel_template.xlsx

🧪 Testing Workflow
Login

Add application metadata (no vulnerabilities yet)

Add vulnerabilities via Add Vulnerability page

Edit vulnerabilities dynamically (add/remove entries or steps)

View summary in dashboard & applications page

Export Word/Excel report per application

✅ Status Options
In-Progress

Completed

On-Hold

In-Pipeline

Cancelled

🛡 Severity Levels
Info

Low

Medium

High

Critical

📌 Notes
No database — uses flat JSON files

Intended for local/internal use (localhost)

Do not expose online without security hardening

