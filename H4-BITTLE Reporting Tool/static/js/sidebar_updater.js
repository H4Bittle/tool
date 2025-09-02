document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebarAppList");
    if (!sidebar) return;

    fetch("/applications")
        .then(response => response.json())
        .then(apps => {
            sidebar.innerHTML = "";
            if (apps.length === 0) {
                sidebar.innerHTML = '<li class="list-group-item text-muted">No applications found</li>';
                return;
            }

            apps.forEach(app => {
                const li = document.createElement("li");
                li.className = "list-group-item list-group-item-action d-flex justify-content-between align-items-center";
                li.textContent = app.name;
                li.onclick = function () {
                    window.location.href = `/applications/${app.id}/vulnerabilities`;
                };
                sidebar.appendChild(li);
            });
        })
        .catch(err => {
            sidebar.innerHTML = '<li class="list-group-item text-danger">Error loading applications</li>';
        });
});
