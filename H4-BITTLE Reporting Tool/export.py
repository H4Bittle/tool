from backend.utils import generate_word_report
import os

app_id = "200869fb-d1ac-4660-837e-15b61848c61a"

# Check file existence before calling the function
print("\n[DEBUG] File existence check:")
template_path = "backend/templates/report_template.docx"
app_file = f"backend/data/applications/app_{app_id}.json"
vuln_file = f"backend/data/vulnerabilities/{app_id}.json"

print(f"Template file exists: {os.path.exists(template_path)} → {template_path}")
print(f"App JSON exists: {os.path.exists(app_file)} → {app_file}")
print(f"Vuln JSON exists: {os.path.exists(vuln_file)} → {vuln_file}")

print("\n[DEBUG] Running generate_word_report...\n")
try:
    path = generate_word_report(app_id)
    print("Report path:", path)
except Exception as e:
    import traceback
    print("[ERROR] Failed to generate report:")
    traceback.print_exc()
