// Mapa interativo da qualidade do ar
let map;
let markers = [];

function loadMap() {
    // Inicializar mapa (usando Leaflet.js como exemplo)
    // Em produção, substituir por implementação real com biblioteca de mapas
    const mapContainer = document.getElementById('map');
    
    if (!mapContainer) {
        console.warn('Elemento do mapa não encontrado');
        return;
    }
    
    // Simular carregamento do mapa
    mapContainer.innerHTML = `
        <div class="text-center p-5 bg-light rounded">
            <i class="fas fa-map-marked-alt fa-3x text-success mb-3"></i>
            <h4>Mapa Interativo da Qualidade do Ar</h4>
            <p class="text-muted">Visualização das estações de monitoramento na Amazônia</p>
            <div class="mt-3">
                <div class="row justify-content-center">
                    <div class="col-auto">
                        <div class="card mb-3">
                            <div class="card-body py-2">
                                <span class="badge bg-success me-2">●</span>
                                <small>Boa (0-50 AQI)</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-auto">
                        <div class="card mb-3">
                            <div class="card-body py-2">
                                <span class="badge bg-warning me-2">●</span>
                                <small>Moderada (51-100 AQI)</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-auto">
                        <div class="card mb-3">
                            <div class="card-body py-2">
                                <span class="badge bg-danger me-2">●</span>
                                <small>Insalubre (101+ AQI)</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div id="map-stations" class="mt-3"></div>
        </div>
    `;
    
    // Carregar estações
    loadMapStations();
}

function loadMapStations() {
    const stationsContainer = document.getElementById('map-stations');
    
    // Dados de exemplo das estações
    const stations = [
        {
            name: 'Manaus - Centro',
            lat: -3.1190,
            lng: -60.0217,
            aqi: 45,
            pm25: 12.5,
            status: 'Boa',
            color: 'success'
        },
        {
            name: 'Belém - Centro',
            lat: -1.4558,
            lng: -48.4902,
            aqi: 68,
            pm25: 20.1,
            status: 'Moderada',
            color: 'warning'
        },
        {
            name: 'Porto Velho',
            lat: -8.7612,
            lng: -63.9005,
            aqi: 120,
            pm25: 45.3,
            status: 'Insalubre',
            color: 'danger'
        },
        {
            name: 'Rio Branco',
            lat: -9.9754,
            lng: -67.8249,
            aqi: 85,
            pm25: 28.7,
            status: 'Moderada',
            color: 'warning'
        }
    ];
    
    let stationsHtml = '<div class="row">';
    
    stations.forEach(station => {
        stationsHtml += `
            <div class="col-md-6 mb-3">
                <div class="card station-card" onclick="showStationDetails('${station.name}')">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1">${station.name}</h6>
                                <p class="mb-1">
                                    <span class="badge bg-${station.color}">AQI: ${station.aqi}</span>
                                    <small class="text-muted ms-2">PM2.5: ${station.pm25} µg/m³</small>
                                </p>
                            </div>
                            <span class="badge bg-${station.color}">${station.status}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    stationsHtml += '</div>';
    stationsContainer.innerHTML = stationsHtml;
}

function showStationDetails(stationName) {
    // Simular detalhes da estação
    const stations = {
        'Manaus - Centro': {
            aqi: 45,
            pm25: 12.5,
            pm10: 25.3,
            no2: 0.02,
            o3: 0.05,
            temperature: 28.5,
            humidity: 78,
            lastUpdate: '10 minutos atrás'
        },
        'Belém - Centro': {
            aqi: 68,
            pm25: 20.1,
            pm10: 35.2,
            no2: 0.04,
            o3: 0.07,
            temperature: 30.5,
            humidity: 82,
            lastUpdate: '15 minutos atrás'
        },
        'Porto Velho': {
            aqi: 120,
            pm25: 45.3,
            pm10: 60.8,
            no2: 0.08,
            o3: 0.10,
            temperature: 32.0,
            humidity: 70,
            lastUpdate: '5 minutos atrás'
        },
        'Rio Branco': {
            aqi: 85,
            pm25: 28.7,
            pm10: 42.1,
            no2: 0.03,
            o3: 0.06,
            temperature: 31.0,
            humidity: 75,
            lastUpdate: '20 minutos atrás'
        }
    };
    
    const station = stations[stationName];
    if (!station) return;
    
    // Criar modal com detalhes
    const modalHtml = `
        <div class="modal fade" id="stationModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${stationName}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Qualidade do Ar</h6>
                                <p><strong>AQI:</strong> ${station.aqi}</p>
                                <p><strong>PM2.5:</strong> ${station.pm25} µg/m³</p>
                                <p><strong>PM10:</strong> ${station.pm10} µg/m³</p>
                            </div>
                            <div class="col-md-6">
                                <h6>Poluentes</h6>
                                <p><strong>NO₂:</strong> ${station.no2} ppm</p>
                                <p><strong>O₃:</strong> ${station.o3} ppm</p>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <h6>Condições Meteorológicas</h6>
                                <p><strong>Temperatura:</strong> ${station.temperature}°C</p>
                                <p><strong>Umidade:</strong> ${station.humidity}%</p>
                            </div>
                            <div class="col-md-6">
                                <h6>Status</h6>
                                <p><strong>Última atualização:</strong> ${station.lastUpdate}</p>
                                <p><strong>Recomendação:</strong> ${getAQIRecommendation(station.aqi)}</p>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        <button type="button" class="btn btn-primary" onclick="generateStationReport('${stationName}')">
                            <i class="fas fa-chart-bar"></i> Gerar Relatório
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Adicionar modal ao DOM se não existir
    let modal = document.getElementById('stationModal');
    if (modal) {
        modal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const stationModal = new bootstrap.Modal(document.getElementById('stationModal'));
    stationModal.show();
}

function getAQIRecommendation(aqi) {
    if (aqi <= 50) {
        return 'Qualidade do ar boa. Condições ideais para atividades externas.';
    } else if (aqi <= 100) {
        return 'Qualidade do ar moderada. Pessoas sensíveis devem considerar reduzir atividades externas prolongadas.';
    } else if (aqi <= 150) {
        return 'Qualidade do ar insalubre para grupos sensíveis. Crianças, idosos e pessoas com problemas respiratórios devem evitar atividades externas prolongadas.';
    } else {
        return 'Qualidade do ar insalubre. Todas as pessoas devem evitar atividades externas prolongadas.';
    }
}

function generateStationReport(stationName) {
    alert(`Relatório gerado para ${stationName}! Em uma implementação real, isso baixaria um PDF com análise detalhada.`);
    
    // Fechar modal
    bootstrap.Modal.getInstance(document.getElementById('stationModal')).hide();
}

// Adicionar efeitos de hover nas estações
document.addEventListener('DOMContentLoaded', function() {
    const stationCards = document.querySelectorAll('.station-card');
    stationCards.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
});