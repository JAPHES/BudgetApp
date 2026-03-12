document.addEventListener("DOMContentLoaded", () => {
    const dataScript = document.getElementById("allocation-data");
    if (!dataScript) return;

    const data = JSON.parse(dataScript.textContent);
    const ctx = document.getElementById("allocationChart");
    if (!ctx) return;

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Savings", "Needs", "Wants"],
            datasets: [
                {
                    data: [data.savings, data.needs, data.wants],
                    backgroundColor: ["#198754", "#0d6efd", "#ffc107"],
                    hoverOffset: 4,
                },
            ],
        },
        options: {
            plugins: {
                legend: { position: "bottom" },
            },
        },
    });
});
