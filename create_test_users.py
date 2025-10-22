import sys
import os

# Adicionar o diretório atual ao path do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.user import User

def create_test_users():
    app = create_app()
    
    with app.app_context():
        # Criar tabelas se não existirem
        print("📦 Criando tabelas do banco de dados...")
        db.create_all()
        
        # Criar admin user
        admin = User.query.filter_by(email='admin@ecopredict.com').first()
        if not admin:
            admin = User(username='admin', email='admin@ecopredict.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            print('✅ Admin user created: admin@ecopredict.com / admin123')
        else:
            print('ℹ️  Admin user already exists')
        
        # Criar user normal
        user = User.query.filter_by(email='user@ecopredict.com').first()
        if not user:
            user = User(username='user', email='user@ecopredict.com')
            user.set_password('user123')
            db.session.add(user)
            print('✅ Normal user created: user@ecopredict.com / user123')
        else:
            print('ℹ️  Normal user already exists')
        
        # Criar usuário pesquisador
        researcher = User.query.filter_by(email='pesquisador@ecopredict.com').first()
        if not researcher:
            researcher = User(username='pesquisador', email='pesquisador@ecopredict.com')
            researcher.set_password('pesquisa123')
            db.session.add(researcher)
            print('✅ Researcher user created: pesquisador@ecopredict.com / pesquisa123')
        else:
            print('ℹ️  Researcher user already exists')
        
        try:
            db.session.commit()
            print('🎉 Test users created successfully!')
            print('\n📝 Credenciais para teste:')
            print('   Admin: admin@ecopredict.com / admin123')
            print('   Usuário: user@ecopredict.com / user123')
            print('   Pesquisador: pesquisador@ecopredict.com / pesquisa123')
        except Exception as e:
            print(f'❌ Error creating users: {e}')
            db.session.rollback()

if __name__ == '__main__':
    create_test_users()