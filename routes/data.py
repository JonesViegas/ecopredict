from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime
from models.air_quality import Dataset, AirQualityData
from app import db
from utils.data_collector import DataCollector
from utils.data_processor import DataProcessor

data_bp = Blueprint('data', __name__)
data_collector = DataCollector()
data_processor = DataProcessor()

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Garante que a pasta de upload existe"""
    upload_folder = 'static/uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"✅ Pasta {upload_folder} criada")
    return upload_folder

def detect_file_type(df):
    """
    Detecta automaticamente o tipo de arquivo baseado nas colunas
    Retorna: 'inmet', 'openaq', ou 'unknown'
    """
    columns = set(df.columns)
    
    # Padrão INMET
    inmet_columns = {'datetime', 'date', 'time', 'temperature', 'humidity', 'pressure', 'station'}
    if inmet_columns.issubset(columns):
        return 'inmet'
    
    # Padrão OpenAQ
    openaq_columns = {'datetime', 'location', 'parameter', 'value', 'unit', 'latitude', 'longitude'}
    if openaq_columns.issubset(columns):
        return 'openaq'
    
    # Padrão manual (colunas básicas)
    basic_columns = {'location', 'latitude', 'longitude', 'pm25'}
    if basic_columns.issubset(columns):
        return 'manual'
    
    return 'unknown'

def process_inmet_data(df, dataset_name):
    """Processa dados do INMET"""
    records_saved = 0
    
    for _, row in df.iterrows():
        try:
            # Determinar localização baseada na estação
            station_locations = {
                'A001': {'name': 'Manaus', 'lat': -3.1190, 'lng': -60.0217},
                'A734': {'name': 'Belém', 'lat': -1.4558, 'lng': -48.4902},
                'A930': {'name': 'Porto Velho', 'lat': -8.7612, 'lng': -63.9005},
                'A520': {'name': 'Rio Branco', 'lat': -9.9754, 'lng': -67.8249}
            }
            
            station = row.get('station', 'A001')
            location_info = station_locations.get(station, station_locations['A001'])
            
            aq_data = AirQualityData(
                location=f"{location_info['name']} - Estação {station}",
                latitude=location_info['lat'],
                longitude=location_info['lng'],
                temperature=float(row.get('temperature', 0)) if pd.notnull(row.get('temperature')) else None,
                humidity=float(row.get('humidity', 0)) if pd.notnull(row.get('humidity')) else None,
                pressure=float(row.get('pressure', 0)) if pd.notnull(row.get('pressure')) else None,
                source='inmet'
            )
            
            # Calcular AQI baseado apenas em dados meteorológicos (aproximação)
            aq_data.aqi = data_collector.calculate_aqi(
                None, None, None, None, None,  # Sem dados de poluentes
                aq_data.temperature, 
                aq_data.humidity, 
                aq_data.pressure
            )
            
            db.session.add(aq_data)
            records_saved += 1
            
        except (ValueError, TypeError) as e:
            print(f"⚠️  Erro ao processar linha INMET: {e}")
            continue
    
    return records_saved

def process_openaq_data(df, dataset_name):
    """Processa dados do OpenAQ"""
    records_saved = 0
    
    # Agrupar por localização e parâmetro para evitar duplicatas
    grouped = df.groupby(['location', 'parameter'])
    
    for (location, parameter), group in grouped:
        try:
            # Pegar o registro mais recente de cada grupo
            latest_record = group.iloc[0]
            
            aq_data = AirQualityData(
                location=location,
                latitude=float(latest_record.get('latitude', 0)),
                longitude=float(latest_record.get('longitude', 0)),
                source='openaq'
            )
            
            # Mapear parâmetros do OpenAQ para nossas colunas
            parameter_value = float(latest_record.get('value', 0)) if pd.notnull(latest_record.get('value')) else None
            
            if parameter == 'pm25':
                aq_data.pm25 = parameter_value
            elif parameter == 'pm10':
                aq_data.pm10 = parameter_value
            elif parameter == 'no2':
                aq_data.no2 = parameter_value
            elif parameter == 'o3':
                aq_data.o3 = parameter_value
            elif parameter == 'so2':
                aq_data.so2 = parameter_value
            elif parameter == 'co':
                aq_data.co2 = parameter_value * 1000  # Converter de ppm para ppb se necessário
            
            # Calcular AQI
            aq_data.aqi = data_collector.calculate_aqi(
                aq_data.pm25, aq_data.pm10, aq_data.no2, aq_data.o3, aq_data.co2
            )
            
            db.session.add(aq_data)
            records_saved += 1
            
        except (ValueError, TypeError) as e:
            print(f"⚠️  Erro ao processar linha OpenAQ: {e}")
            continue
    
    return records_saved

def process_manual_data(df, dataset_name):
    """Processa dados no formato manual"""
    records_saved = 0
    
    for _, row in df.iterrows():
        try:
            aq_data = AirQualityData(
                location=row['location'],
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                pm25=float(row.get('pm25', 0)) if pd.notnull(row.get('pm25')) else None,
                pm10=float(row.get('pm10', 0)) if pd.notnull(row.get('pm10')) else None,
                co2=float(row.get('co2', 0)) if pd.notnull(row.get('co2')) else None,
                no2=float(row.get('no2', 0)) if pd.notnull(row.get('no2')) else None,
                o3=float(row.get('o3', 0)) if pd.notnull(row.get('o3')) else None,
                so2=float(row.get('so2', 0)) if pd.notnull(row.get('so2')) else None,
                temperature=float(row.get('temperature', 0)) if pd.notnull(row.get('temperature')) else None,
                humidity=float(row.get('humidity', 0)) if pd.notnull(row.get('humidity')) else None,
                pressure=float(row.get('pressure', 0)) if pd.notnull(row.get('pressure')) else None,
                source='manual'
            )
            
            # Calcular AQI
            aq_data.aqi = data_collector.calculate_aqi(
                aq_data.pm25, aq_data.pm10, aq_data.no2, aq_data.o3, aq_data.co2,
                aq_data.temperature, aq_data.humidity, aq_data.pressure
            )
            
            db.session.add(aq_data)
            records_saved += 1
            
        except (ValueError, TypeError) as e:
            print(f"⚠️  Erro ao processar linha manual: {e}")
            continue
    
    return records_saved

@data_bp.route('/data/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Garantir que a pasta de upload existe
            upload_folder = ensure_upload_folder()
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_folder, filename)
            
            try:
                file.save(filepath)
                
                # Processar arquivo
                try:
                    if filename.endswith('.csv'):
                        df = pd.read_csv(filepath)
                    else:
                        df = pd.read_excel(filepath)
                    
                    # Detectar tipo de arquivo automaticamente
                    file_type = detect_file_type(df)
                    print(f"📁 Tipo de arquivo detectado: {file_type}")
                    
                    if file_type == 'unknown':
                        flash('Formato de arquivo não reconhecido. Use INMET, OpenAQ ou formato manual.', 'danger')
                        os.remove(filepath)
                        return redirect(request.url)
                    
                    # Salvar dataset
                    dataset = Dataset(
                        name=request.form.get('dataset_name', f"{file_type}_{filename}"),
                        description=request.form.get('description', f"Arquivo {file_type} importado automaticamente"),
                        filename=filename,
                        user_id=current_user.id
                    )
                    db.session.add(dataset)
                    db.session.commit()
                    
                    # Processar de acordo com o tipo
                    records_saved = 0
                    if file_type == 'inmet':
                        records_saved = process_inmet_data(df, dataset.name)
                    elif file_type == 'openaq':
                        records_saved = process_openaq_data(df, dataset.name)
                    elif file_type == 'manual':
                        records_saved = process_manual_data(df, dataset.name)
                    
                    db.session.commit()
                    flash(f'✅ Dataset {file_type.upper()} carregado com sucesso! {records_saved} registros salvos.', 'success')
                    
                except Exception as e:
                    flash(f'Erro ao processar arquivo: {str(e)}', 'danger')
                    # Remover arquivo em caso de erro
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return redirect(request.url)
                
            except Exception as e:
                flash(f'Erro ao salvar arquivo: {str(e)}', 'danger')
                return redirect(request.url)
            
            return redirect(url_for('data.upload'))
    
    # Carregar datasets do usuário
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    return render_template('data_upload.html', datasets=datasets)

@data_bp.route('/data/sources')
@login_required
def sources():
    return render_template('data_sources.html')

@data_bp.route('/api/fetch-openaq-data')
@login_required
def fetch_openaq_data():
    try:
        location = request.args.get('location', 'Manaus')
        data = data_collector.get_openaq_data(location=location, limit=100)
        
        if data:
            # Processar e salvar dados
            for measurement in data.get('results', []):
                aq_data = AirQualityData(
                    location=measurement.get('location', ''),
                    latitude=measurement.get('coordinates', {}).get('latitude', 0),
                    longitude=measurement.get('coordinates', {}).get('longitude', 0),
                    pm25=measurement.get('value') if measurement.get('parameter') == 'pm25' else None,
                    pm10=measurement.get('value') if measurement.get('parameter') == 'pm10' else None,
                    no2=measurement.get('value') if measurement.get('parameter') == 'no2' else None,
                    o3=measurement.get('value') if measurement.get('parameter') == 'o3' else None,
                    so2=measurement.get('value') if measurement.get('parameter') == 'so2' else None,
                    source='openaq'
                )
                db.session.add(aq_data)
            
            db.session.commit()
            return jsonify({'success': True, 'message': f'Dados de {location} carregados com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao buscar dados do OpenAQ'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@data_bp.route('/api/fetch-inmet-data')
@login_required
def fetch_inmet_data():
    try:
        station_code = request.args.get('station', 'A001')
        data = data_collector.get_inmet_data(station_code)
        
        if data:
            # Processar dados do INMET
            aq_data = AirQualityData(
                location=data.get('DC_NOME', 'Estação INMET'),
                latitude=data.get('VL_LATITUDE', 0),
                longitude=data.get('VL_LONGITUDE', 0),
                temperature=data.get('TEM_INS', 0),
                humidity=data.get('UMD_INS', 0),
                pressure=data.get('PRE_INS', 0),
                source='inmet'
            )
            db.session.add(aq_data)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Dados do INMET carregados com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao buscar dados do INMET'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
# ... código existente ...

@data_bp.route('/data/datasets')
@login_required
def datasets_list():
    """Lista todos os datasets do usuário"""
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    return render_template('datasets_list.html', datasets=datasets)

@data_bp.route('/api/dataset/<int:dataset_id>')
@login_required
def get_dataset_data(dataset_id):
    """Retorna dados de um dataset específico"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Verificar se o usuário tem permissão
    if dataset.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Buscar dados de qualidade do ar relacionados
    air_data = AirQualityData.query.filter_by(source='manual').all()
    
    data = [item.to_dict() for item in air_data]
    return jsonify({
        'dataset': {
            'id': dataset.id,
            'name': dataset.name,
            'description': dataset.description,
            'created_at': dataset.created_at.isoformat()
        },
        'records': data,
        'total_records': len(data)
    })

@data_bp.route('/data/dataset/<int:dataset_id>')
@login_required
def view_dataset(dataset_id):
    """Página para visualizar dataset específico"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Verificar permissão
    if dataset.user_id != current_user.id and not current_user.is_admin:
        flash('Acesso negado', 'danger')
        return redirect(url_for('data.datasets_list'))
    
    return render_template('view_dataset.html', dataset=dataset)