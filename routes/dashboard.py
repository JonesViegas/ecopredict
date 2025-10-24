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
    # Busca os 100 registros mais recentes do banco de dados
    latest_data = AirQualityData.query.order_by(AirQualityData.timestamp.desc()).limit(100).all()
    
    data = []
    locations_added = set()  # Usado para evitar locais duplicados no mapa

    for record in latest_data:
        if record.location not in locations_added:
            status = 'Boa'
            if record.aqi and record.aqi > 100:
                status = 'Insalubre'
            elif record.aqi and record.aqi > 50:
                status = 'Moderada'
            
            data.append({
                'location': record.location,
                'latitude': record.latitude,
                'longitude': record.longitude,
                'aqi': record.aqi,
                'pm25': record.pm25,
                'status': status
            })
            locations_added.add(record.location)
            
    return jsonify(data)