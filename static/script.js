function createBarChart(canvasId, labels, values, label, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                borderRadius: 8,
                backgroundColor: color,
                borderWidth: 1,
                borderColor: color,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function createDoughnutChart(canvasId, labels, values, label) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const palette = ['#2563eb', '#0ea5e9', '#14b8a6', '#84cc16', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                backgroundColor: labels.map((_, i) => palette[i % palette.length]),
                borderWidth: 1,
                borderColor: '#ffffff'
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12 }
                }
            }
        }
    });
}

(function initDashboard() {
    const data = window.dashboardData || {};

    createBarChart(
        'wardChart',
        data.ward?.labels || [],
        data.ward?.values || [],
        'Records',
        'rgba(37, 99, 235, 0.75)'
    );

    createBarChart(
        'mohollaChart',
        data.moholla?.labels || [],
        data.moholla?.values || [],
        'Records',
        'rgba(2, 132, 199, 0.72)'
    );

    createDoughnutChart(
        'rateChart',
        data.rate?.labels || [],
        data.rate?.values || [],
        'Rate Distribution'
    );

    const filterForm = document.getElementById('filterForm');
    const exportBtn = document.getElementById('exportBtn');

    if (filterForm && exportBtn) {
        const updateExportLink = () => {
            const params = new URLSearchParams(new FormData(filterForm));
            exportBtn.href = `/export?${params.toString()}`;
        };

        filterForm.addEventListener('change', updateExportLink);
        filterForm.addEventListener('input', updateExportLink);
        updateExportLink();
    }
})();
