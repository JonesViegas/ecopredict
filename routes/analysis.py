from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import pandas as pd
from models.air_quality import AirQualityData, Dataset  # ✅ Adicionar Dataset aqui
from app import db
from utils.ml_models import AirQualityPredictor
import json
from datetime import datetime, timedelta

analysis_bp = Blueprint('analysis', __name__)
ml_predictor = AirQualityPredictor()

@analysis_bp.route('/analysis')
@login_required
def index():
    return render_template('analysis.html')

@analysis_bp.route('/analysis/dataset/<int:dataset_id>')
@login_required
def analyze_dataset(dataset_id):
    """Página de análise para dataset específico"""
    dataset = Dataset.query.get_or_404(dataset_id)  # ✅ Agora Dataset está definido
    
    # Verificar permissão
    if dataset.user_id != current_user.id and not current_user.is_admin:
        flash('Acesso negado', 'danger')
        return redirect(url_for('data.datasets_list'))
    
    return render_template('analyze_dataset.html', dataset=dataset)

@analysis_bp.route('/analysis/train-models', methods=['POST'])
@login_required
def train_models():
    try:
        # Buscar dados para treinamento
        aq_data = AirQualityData.query.limit(1000).all()
        
        if not aq_data:
            return jsonify({'success': False, 'message': 'Dados insuficientes para treinamento'})
        
        # Converter para DataFrame
        data_list = []
        for record in aq_data:
            data_list.append({
                'pm25': record.pm25 or 0,
                'pm10': record.pm10 or 0,
                'no2': record.no2 or 0,
                'o3': record.o3 or 0,
                'co2': record.co2 or 0,
                'temperature': record.temperature or 0,
                'humidity': record.humidity or 0,
                'pressure': record.pressure or 0,
                'aqi': record.aqi or 0
            })
        
        df = pd.DataFrame(data_list)
        
        # Usar AQI como target para previsão
        X = df[['pm25', 'pm10', 'no2', 'o3', 'co2', 'temperature', 'humidity', 'pressure']]
        y = df['aqi']
        
        # Treinar modelos
        rf_model, rf_mse, rf_r2 = ml_predictor.train_random_forest(X, y)
        lr_model, lr_mse, lr_r2 = ml_predictor.train_linear_regression(X, y)
        kmeans = ml_predictor.train_kmeans(X, n_clusters=3)
        
        return jsonify({
            'success': True,
            'message': 'Modelos treinados com sucesso!',
            'metrics': {
                'random_forest': {'mse': rf_mse, 'r2': rf_r2},
                'linear_regression': {'mse': lr_mse, 'r2': lr_r2}
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@analysis_bp.route('/api/dataset/<int:dataset_id>/train', methods=['POST'])
@login_required
def train_dataset_models(dataset_id):
    """Treina modelos com dados de um dataset específico"""
    try:
        dataset = Dataset.query.get_or_404(dataset_id)
        
        # Verificar permissão
        if dataset.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'success': False, 'message': 'Acesso negado'})
        
        # Buscar dados do dataset (todos os tipos)
        air_data = AirQualityData.query.all()
        
        if len(air_data) < 10:
            return jsonify({'success': False, 'message': 'Dados insuficientes para treinamento (mínimo 10 registros)'})
        
        # Converter para DataFrame
        data_list = []
        for record in air_data:
            data_list.append({
                'pm25': record.pm25 or 0,
                'pm10': record.pm10 or 0,
                'no2': record.no2 or 0,
                'o3': record.o3 or 0,
                'co2': record.co2 or 0,
                'temperature': record.temperature or 0,
                'humidity': record.humidity or 0,
                'pressure': record.pressure or 0,
                'aqi': record.aqi or 0
            })
        
        df = pd.DataFrame(data_list)
        
        # Preparar dados para treinamento
        from utils.ml_models import AirQualityPredictor
        ml_predictor = AirQualityPredictor()
        
        # Usar AQI como target para previsão
        X = df[['pm25', 'pm10', 'no2', 'o3', 'co2', 'temperature', 'humidity', 'pressure']]
        y = df['aqi']
        
        # Treinar modelos
        rf_model, rf_mse, rf_r2 = ml_predictor.train_random_forest(X, y)
        lr_model, lr_mse, lr_r2 = ml_predictor.train_linear_regression(X, y)
        kmeans = ml_predictor.train_kmeans(X, n_clusters=3)
        
        return jsonify({
            'success': True,
            'message': f'Modelos treinados com sucesso usando {len(air_data)} registros do dataset {dataset.name}',
            'metrics': {
                'random_forest': {'mse': rf_mse, 'r2': rf_r2},
                'linear_regression': {'mse': lr_mse, 'r2': lr_r2}
            },
            'dataset_info': {
                'name': dataset.name,
                'records_used': len(air_data),
                'features_used': list(X.columns)
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@analysis_bp.route('/analysis/predict', methods=['POST'])
@login_required
def predict():
    try:
        data = request.get_json()
        features = [
            data.get('pm25', 0),
            data.get('pm10', 0),
            data.get('no2', 0),
            data.get('o3', 0),
            data.get('co2', 0),
            data.get('temperature', 0),
            data.get('humidity', 0)
        ]
        
        model_type = data.get('model_type', 'random_forest')
        prediction = ml_predictor.predict_air_quality(features, model_type)
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'model_used': model_type
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@analysis_bp.route('/analysis/cluster-analysis')
@login_required
def cluster_analysis():
    try:
        # Buscar dados para análise de clusters
        aq_data = AirQualityData.query.filter(
            AirQualityData.pm25.isnot(None),
            AirQualityData.pm10.isnot(None)
        ).limit(500).all()
        
        if not aq_data:
            return jsonify({'success': False, 'message': 'Dados insuficientes para análise'})
        
        # Preparar dados para clustering
        data_for_clustering = []
        locations = []
        
        for record in aq_data:
            data_for_clustering.append([
                record.pm25 or 0,
                record.pm10 or 0,
                record.temperature or 0
            ])
            locations.append({
                'location': record.location,
                'lat': record.latitude,
                'lng': record.longitude,
                'aqi': record.aqi or 0
            })
        
        # Aplicar K-Means
        import numpy as np
        from sklearn.cluster import KMeans
        
        kmeans = KMeans(n_clusters=4, random_state=42)
        clusters = kmeans.fit_predict(data_for_clustering)
        
        # Agrupar resultados
        results = []
        for i, location in enumerate(locations):
            results.append({
                **location,
                'cluster': int(clusters[i]),
                'pollution_level': ['Baixo', 'Moderado', 'Alto', 'Muito Alto'][clusters[i]]
            })
        
        return jsonify({
            'success': True,
            'clusters': results,
            'cluster_centers': kmeans.cluster_centers_.tolist()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@analysis_bp.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@analysis_bp.route('/api/generate-report')
@login_required
def generate_report():
    try:
        report_type = request.args.get('type', 'weekly')
        
        # Calcular data de início baseada no tipo de relatório
        end_date = datetime.utcnow()
        if report_type == 'daily':
            start_date = end_date - timedelta(days=1)
        elif report_type == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        else:  # monthly
            start_date = end_date - timedelta(days=30)
        
        # Buscar dados do período
        aq_data = AirQualityData.query.filter(
            AirQualityData.timestamp.between(start_date, end_date)
        ).all()
        
        if not aq_data:
            return jsonify({'success': False, 'message': 'Nenhum dado encontrado para o período'})
        
        # Gerar estatísticas
        aqi_values = [d.aqi for d in aq_data if d.aqi]
        pm25_values = [d.pm25 for d in aq_data if d.pm25]
        
        report = {
            'period': report_type,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_records': len(aq_data),
            'stats': {
                'aqi': {
                    'mean': sum(aqi_values) / len(aqi_values) if aqi_values else 0,
                    'max': max(aqi_values) if aqi_values else 0,
                    'min': min(aqi_values) if aqi_values else 0
                },
                'pm25': {
                    'mean': sum(pm25_values) / len(pm25_values) if pm25_values else 0,
                    'max': max(pm25_values) if pm25_values else 0,
                    'min': min(pm25_values) if pm25_values else 0
                }
            },
            'alerts': generate_alerts(aq_data)
        }
        
        return jsonify({'success': True, 'report': report})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def generate_alerts(aq_data):
    alerts = []
    
    # Verificar níveis críticos
    high_pm25 = [d for d in aq_data if d.pm25 and d.pm25 > 35]
    high_aqi = [d for d in aq_data if d.aqi and d.aqi > 100]
    
    if high_pm25:
        alerts.append({
            'type': 'warning',
            'message': f'{len(high_pm25)} registros com PM2.5 acima do limite seguro (35 µg/m³)',
            'locations': list(set([d.location for d in high_pm25]))
        })
    
    if high_aqi:
        alerts.append({
            'type': 'danger',
            'message': f'{len(high_aqi)} registros com AQI acima de 100 (insalubre)',
            'locations': list(set([d.location for d in high_aqi]))
        })
    
    return alerts