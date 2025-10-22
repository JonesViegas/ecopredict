import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ecopredict-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ecopredict.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/uploads'
    
    # APIs externas
    OPENAQ_API_URL = 'https://api.openaq.org/v2/'
    IQAIR_API_KEY = os.environ.get('IQAIR_API_KEY', '')
    INMET_API_URL = 'https://apitempo.inmet.gov.br/'