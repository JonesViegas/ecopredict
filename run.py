from app import create_app, db
from models.user import User
from models.air_quality import AirQualityData
import os

def initialize_application():
    """Inicializa a aplicação e cria pastas necessárias"""
    # Criar pastas necessárias
    folders = ['static/uploads', 'ml/models', 'ml/data', 'static/data']
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ Pasta criada: {folder}")
    
    # Inicializar banco de dados
    try:
        with app.app_context():
            db.create_all()
            print("✅ Banco de dados inicializado com sucesso!")
            
            user_count = User.query.count()
            print(f"📊 Total de usuários no sistema: {user_count}")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")

app = create_app()

# Inicializar aplicação quando o arquivo for executado
if __name__ == '__main__':
    print("🚀 Iniciando EcoPredict...")
    initialize_application()
    print("🌐 Servidor iniciando em http://localhost:5000")
    print("📝 Use CTRL+C para parar o servidor")
    app.run(host='0.0.0.0', port=5000, debug=True)