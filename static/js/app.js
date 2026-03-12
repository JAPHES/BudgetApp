document.addEventListener("DOMContentLoaded", () => {
    const parseData = (id) => {
        const el = document.getElementById(id);
        return el ? JSON.parse(el.textContent) : null;
    };

    // Doughnut chart (50/30/20)
    const allocationData = parseData("allocation-data");
    if (allocationData) {
        const ctx = document.getElementById("allocationChart");
        if (ctx) {
            new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: ["Savings", "Needs", "Wants"],
                    datasets: [
                        {
                            data: [allocationData.savings, allocationData.needs, allocationData.wants],
                            backgroundColor: ["#198754", "#0d6efd", "#ff9f1c"],
                            hoverOffset: 6,
                        },
                    ],
                },
                options: {
                    plugins: {
                        legend: { position: "bottom" },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => `${ctx.label}: $${ctx.raw}`,
                            },
                        },
                    },
                },
            });
        }
    }

    // Stacked bar for custom categories (needs/wants)
    const categoriesData = parseData("categories-data");
    if (allocationData && categoriesData && categoriesData.length) {
        const needsAmount = allocationData.needs;
        const wantsAmount = allocationData.wants;

        const labels = categoriesData.map((c) => c.name);
        const needsValues = categoriesData.map((c) =>
            c.kind === "needs" ? parseFloat(((needsAmount * c.percentage) / 100).toFixed(2)) : 0
        );
        const wantsValues = categoriesData.map((c) =>
            c.kind === "wants" ? parseFloat(((wantsAmount * c.percentage) / 100).toFixed(2)) : 0
        );

        const stackedCtx = document.getElementById("stackedBreakdown");
        if (stackedCtx) {
            new Chart(stackedCtx, {
                type: "bar",
                data: {
                    labels,
                    datasets: [
                        { label: "Needs", data: needsValues, backgroundColor: "#0d6efd", stack: "breakdown" },
                        { label: "Wants", data: wantsValues, backgroundColor: "#ff9f1c", stack: "breakdown" },
                    ],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: "bottom" },
                        tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: $${ctx.raw}` } },
                    },
                    scales: {
                        x: { stacked: true },
                        y: { stacked: true, beginAtZero: true },
                    },
                },
            });
        }
    }

    // Monthly trends chart
    const trendsData = parseData("trends-data");
    if (trendsData && trendsData.length) {
        const labels = trendsData.map((r) => r.month);
        const salary = trendsData.map((r) => r.salary);
        const expenses = trendsData.map((r) => r.expenses);
        const savings = trendsData.map((r) => r.savings);
        const trendsCtx = document.getElementById("trendsChart");
        if (trendsCtx) {
            new Chart(trendsCtx, {
                type: "line",
                data: {
                    labels,
                    datasets: [
                        { label: "Salary", data: salary, borderColor: "#0d6efd", fill: false, tension: 0.3 },
                        { label: "Expenses", data: expenses, borderColor: "#ff9f1c", fill: false, tension: 0.3 },
                        { label: "Savings", data: savings, borderColor: "#198754", fill: false, tension: 0.3 },
                    ],
                },
                options: {
                    plugins: { legend: { position: "bottom" } },
                    scales: { y: { beginAtZero: true } },
                },
            });
        }
    }
});
