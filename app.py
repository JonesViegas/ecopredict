from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Inicializações PRIMEIRO
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    
    # Importar e registrar blueprints DENTRO da função para evitar circular imports
    with app.app_context():
        from routes.auth import auth_bp
        from routes.dashboard import dashboard_bp
        from routes.data import data_bp
        from routes.analysis import analysis_bp
        from routes.admin import admin_bp
        from routes.main import main_bp  # Novo blueprint principal
        
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(data_bp)
        app.register_blueprint(analysis_bp)
        app.register_blueprint(admin_bp)
    
    return app