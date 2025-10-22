// Dashboard functionality
function initializeDashboard() {
    loadTrendChart();
    loadPollutantChart();
    updateMetrics();
}

function loadTrendChart() {
    const ctx = document.getElementById('trendChart').getContext('2d');
    const trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
            datasets: [{
                label: 'AQI',
                data: [65, 59, 80, 81, 56, 55, 68],
                borderColor: '#198754',
                backgroundColor: 'rgba(25, 135, 84, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

function loadPollutantChart() {
    const ctx = document.getElementById('pollutantChart').getContext('2d');
    const pollutantChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['PM2.5', 'PM10', 'NO₂', 'O₃', 'CO₂'],
            datasets: [{
                data: [30, 25, 20, 15, 10],
                backgroundColor: [
                    '#ff6b6b',
                    '#4ecdc4',
                    '#45b7d1',
                    '#96ceb4',
                    '#feca57'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function updateMetrics() {
    // Atualizar métricas em tempo real
    fetch('/api/air-quality-data')
        .then(response => response.json())
        .then(data => {
            console.log('Dados atualizados:', data);
            // Atualizar interface com dados recebidos
        })
        .catch(error => {
            console.error('Erro ao atualizar métricas:', error);
        });
}

function applyFilters() {
    const region = document.getElementById('region-filter').value;
    const parameter = document.getElementById('parameter-filter').value;
    
    // Aplicar filtros e atualizar visualizações
    console.log('Aplicando filtros:', { region, parameter });
    
    // Simular atualização
    alert(`Filtros aplicados:\nRegião: ${region}\nParâmetro: ${parameter}`);
}