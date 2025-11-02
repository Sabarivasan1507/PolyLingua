// static/js/chart.js

// Chart.js configuration for Progress Dashboard
const ctx = document.getElementById('progressChart').getContext('2d');

const data = {
    labels: [], // Add lesson names dynamically from template
    datasets: [{
        label: 'Quiz Score',
        data: [], // Add scores dynamically from template
        backgroundColor: 'rgba(54, 162, 235, 0.6)'
    }]
};

const config = {
    type: 'bar',
    data: data,
    options: {
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        },
        plugins: {
            legend: {
                display: true
            }
        }
    }
};

const progressChart = new Chart(ctx, config);