document.addEventListener("DOMContentLoaded", function () {
    // Populate application dropdown
    fetch("/applications")
        .then(response => response.json())
        .then(apps => {
            const dropdown = document.getElementById("vuln_app_id");
            if (dropdown) {
                apps.forEach(app => {
                    const option = document.createElement("option");
                    option.value = app.id;
                    option.textContent = `${app.name} (v${app.version})`;
                    dropdown.appendChild(option);
                });
            }
        });

    // Handle application form submission
    const appForm = document.getElementById("appForm");
    if (appForm) {
        appForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const payload = {
                id: document.getElementById("app_id").value,
                name: document.getElementById("app_name").value,
                version: document.getElementById("app_version").value,
                url: document.getElementById("app_url").value,
                start_date: document.getElementById("app_start_date").value,
                end_date: document.getElementById("app_end_date").value
            };

            fetch("/add_application", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert("Application added successfully");
                        appForm.reset();
                    }
                });
        });
    }

    // Handle vulnerability form submission
    const vulnForm = document.getElementById("vulnForm");
    if (vulnForm) {
        vulnForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const steps = [];
            for (let i = 1; i <= 12; i++) {
                const desc = document.getElementById(`step${i}_desc`).value;
                steps.push({ step_number: i, description: desc, screenshot: null }); // Screenshot upload handled later
            }

            const payload = {
                application_id: document.getElementById("vuln_app_id").value,
                id: document.getElementById("vuln_id").value,
                title: document.getElementById("vuln_name").value,
                summary: document.getElementById("vuln_summary").value,
                description: document.getElementById("vuln_description").value,
                business_impact: document.getElementById("vuln_business_impact").value,
                recommendation: document.getElementById("vuln_recommendation").value,
                cvss_score: parseFloat(document.getElementById("vuln_cvss_score").value),
                cvss_vector: document.getElementById("vuln_cvss_vector").value,
                severity: document.getElementById("vuln_severity").value,
                affected_url: document.getElementById("vuln_affected_url").value,
                cwe_cve_id: document.getElementById("vuln_cwe_cve").value,
                reference_url: document.getElementById("vuln_reference").value,
                steps_to_reproduce: steps
            };

            fetch("/add_vulnerability", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert("Vulnerability added successfully");
                        vulnForm.reset();
                    }
                });
        });
    }
});
