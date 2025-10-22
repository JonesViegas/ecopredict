// Funções gerais do EcoPredict

// Inicialização quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('EcoPredict carregado com sucesso!');
    
    // Adicionar efeitos de hover em cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
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

// Função para mostrar loading
function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div> Carregando...';
    }
}

// Função para mostrar mensagens
function showMessage(element, message, type = 'info') {
    if (element) {
        const alertClass = type === 'error' ? 'alert-danger' : 
                          type === 'success' ? 'alert-success' : 'alert-info';
        element.innerHTML = `<div class="alert ${alertClass}">${message}</div>`;
    }
}

// Função para formatar números
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

// Função para obter cor baseada no AQI
function getAQIColor(aqi) {
    if (aqi <= 50) return '#00e400';      // Boa - Verde
    if (aqi <= 100) return '#ffff00';     // Moderada - Amarelo
    if (aqi <= 150) return '#ff7e00';     // Insalubre - Laranja
    if (aqi <= 200) return '#ff0000';     // Insalubre - Vermelho
    if (aqi <= 300) return '#8f3f97';     // Muito Insalubre - Roxo
    return '#7e0023';                     // Perigosa - Vermelho Escuro
}