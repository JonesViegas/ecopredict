// Mapa interativo da qualidade do ar
let map;
const markers = [];

// Função para obter a cor baseada no AQI (Índice de Qualidade do Ar)
function getAQIColor(aqi) {
    if (aqi <= 50) return '#00e400';      // Boa - Verde
    if (aqi <= 100) return '#ffff00';     // Moderada - Amarelo
    if (aqi <= 150) return '#ff7e00';     // Insalubre (Grupos Sensíveis) - Laranja
    if (aqi <= 200) return '#ff0000';     // Insalubre - Vermelho
    if (aqi <= 300) return '#8f3f97';     // Muito Insalubre - Roxo
    return '#7e0023';                     // Perigosa - Marrom
}

function loadMap() {
    const mapContainer = document.getElementById('map');
    if (!mapContainer || map) { // Evita reinicializar o mapa
        return;
    }

    // 1. Inicializa o mapa Leaflet, centrado na região amazônica.
    map = L.map('map').setView([-5.0, -60.0], 4);

    // 2. Adiciona a camada de mapa (tiles) do OpenStreetMap.
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // 3. Busca os dados das estações na nossa API.
    fetch('/api/air-quality-data')
        .then(response => response.json())
        .then(stations => {
            // Limpa marcadores antigos se a função for chamada novamente
            markers.forEach(marker => marker.remove());

            // 4. Adiciona um marcador para cada estação no mapa.
            stations.forEach(station => {
                if (station.latitude && station.longitude) {
                    const circleMarker = L.circleMarker([station.latitude, station.longitude], {
                        radius: 8,
                        fillColor: getAQIColor(station.aqi),
                        color: '#000',
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(map);

                    // 5. Define o conteúdo que aparecerá no hover.
                    const popupContent = `
                        <b>${station.location}</b><br>
                        Qualidade do Ar: <b>${station.status}</b><br>
                        AQI: ${station.aqi || 'N/A'}<br>
                        PM2.5: ${station.pm25 ? station.pm25.toFixed(2) + ' µg/m³' : 'N/A'}
                    `;

                    // 6. Adiciona o evento de "mouseover" (passar o mouse).
                    circleMarker.on('mouseover', function (e) {
                        this.bindPopup(popupContent).openPopup();
                    });

                    // Opcional: Fecha o popup ao retirar o mouse.
                    circleMarker.on('mouseout', function (e) {
                        this.closePopup();
                    });

                    markers.push(circleMarker);
                }
            });
        })
        .catch(error => console.error('Erro ao carregar dados do mapa:', error));
}