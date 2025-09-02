document.addEventListener("DOMContentLoaded", function () {
    const statsContainer = document.getElementById("dashboardStats");
    if (!statsContainer) return;

    fetch("/applications")
        .then(res => res.json())
        .then(apps => {
            const totalApps = apps.length;
            const statusCounts = {
                "completed": 0,
                "in-progress": 0,
                "on-hold": 0,
                "in-pipeline": 0,
                "cancelled": 0
            };
            apps.forEach(app => {
                const status = (app.status || '').toLowerCase();
                if (statusCounts.hasOwnProperty(status)) {
                    statusCounts[status]++;
                }
            });

            fetch("/vulnerabilities_summary")
                .then(res => res.json())
                .then(summary => {
                    const { total, info, low, medium, high, critical } = summary;

                    statsContainer.innerHTML = `
                        <div class="row g-3">
                            <div class="col-md-4">
                                <div class="card shadow-sm">
                                    <div class="card-body">
                                        <h5 class="card-title">Applications: ${totalApps}</h5>
                                        <ul class="list-unstyled mb-0">
                                            ${Object.entries(statusCounts).map(([k, v]) => `<li>${k}: ${v}</li>`).join('')}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-8">
                                <div class="card shadow-sm">
                                    <div class="card-body">
                                        <h5 class="card-title">Vulnerabilities Summary</h5>
                                        <ul class="list-unstyled mb-0">
                                            <li>Critical: ${critical}</li>
                                            <li>High: ${high}</li>
                                            <li>Medium: ${medium}</li>
                                            <li>Low: ${low}</li>
                                            <li>Info: ${info}</li>
                                            <li>Total: ${total}</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
        });
});
