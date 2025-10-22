from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models.air_quality import AirQualityData
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    return render_template('dashboard.html')

@dashboard_bp.route('/api/air-quality-data')
@login_required
def air_quality_data():
    # Dados de exemplo - em produção, buscar do banco
    data = [
        {
            'location': 'Manaus',
            'latitude': -3.1190,
            'longitude': -60.0217,
            'aqi': 45,
            'pm25': 12.5,
            'status': 'Boa'
        },
        {
            'location': 'Belém',
            'latitude': -1.4558,
            'longitude': -48.4902,
            'aqi': 68,
            'pm25': 20.1,
            'status': 'Moderada'
        },
        {
            'location': 'Porto Velho',
            'latitude': -8.7612,
            'longitude': -63.9005,
            'aqi': 120,
            'pm25': 45.3,
            'status': 'Insalubre'
        }
    ]
    return jsonify(data)