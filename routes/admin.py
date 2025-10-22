from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.user import User
from models.air_quality import AirQualityData, Dataset
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def restrict_to_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403

@admin_bp.route('/admin')
@login_required
def dashboard():
    # Estatísticas para o dashboard admin
    total_users = User.query.count()
    total_datasets = Dataset.query.count()
    total_aq_data = AirQualityData.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_datasets=total_datasets,
                         total_aq_data=total_aq_data,
                         recent_users=recent_users)

@admin_bp.route('/admin/users')
@login_required
def users():
    users_list = User.query.all()
    return render_template('admin_users.html', users=users_list)

@admin_bp.route('/admin/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat(),
            'datasets_count': len(user.datasets)
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        
        if 'username' in data:
            user.username = data['username']
        
        if 'email' in data:
            user.email = data['email']
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Usuário atualizado com sucesso'})
    
    elif request.method == 'DELETE':
        # Não permitir que admin se delete
        if user.id == current_user.id:
            return jsonify({'success': False, 'message': 'Não é possível excluir sua própria conta'})
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Usuário excluído com sucesso'})

@admin_bp.route('/admin/system-stats')
@login_required
def system_stats():
    # Estatísticas do sistema
    from datetime import datetime, timedelta
    
    # Dados dos últimos 7 dias
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    # Novos usuários
    new_users = User.query.filter(User.created_at.between(start_date, end_date)).count()
    
    # Novos datasets
    new_datasets = Dataset.query.filter(Dataset.created_at.between(start_date, end_date)).count()
    
    # Dados de qualidade do ar por fonte
    sources_data = db.session.query(
        AirQualityData.source,
        db.func.count(AirQualityData.id)
    ).group_by(AirQualityData.source).all()
    
    return jsonify({
        'new_users_7d': new_users,
        'new_datasets_7d': new_datasets,
        'data_by_source': dict(sources_data),
        'total_storage_mb': calculate_storage_usage()
    })

def calculate_storage_usage():
    # Calcular uso de armazenamento (simplificado)
    import os
    total_size = 0
    
    for dirpath, dirnames, filenames in os.walk('static/uploads'):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    
    return round(total_size / (1024 * 1024), 2)  # MB