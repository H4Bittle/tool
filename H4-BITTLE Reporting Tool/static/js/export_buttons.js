document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("applicationList");
    if (!container) return;

    fetch("/applications")
        .then(res => res.json())
        .then(apps => {
            container.innerHTML = "";
            apps.forEach(app => {
                const li = document.createElement("li");
                li.className = "list-group-item d-flex justify-content-between align-items-center";
                li.innerHTML = `
                    <span><strong>${app.name}</strong> (v${app.version})</span>
                    <div>
                        <button class="btn btn-sm btn-outline-success me-2" onclick="exportWord('${app.id}')">Word</button>
                        <button class="btn btn-sm btn-outline-primary" onclick="exportExcel('${app.id}')">Excel</button>
                    </div>
                `;
                container.appendChild(li);
            });
        });
});

function exportWord(appId) {
    fetch(`/export/word/${appId}`)
        .then(res => res.json())
        .then(data => {
            alert("Word report generated.");
            window.open(data.path, '_blank');
        })
        .catch(err => alert("Failed to generate Word report."));
}

function exportExcel(appId) {
    fetch(`/export/excel/${appId}`)
        .then(res => res.json())
        .then(data => {
            alert("Excel report generated.");
            window.open(data.path, '_blank');
        })
        .catch(err => alert("Failed to generate Excel report."));
}
