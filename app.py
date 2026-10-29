import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from models import db, Usuario

# Importa os módulos desacoplados
from routes.auth import auth_bp
from routes.views import views_bp
from routes.api import api_bp

load_dotenv()
app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
# Atenção: O redirecionamento de não autenticados agora aponta para o blueprint 'auth'
login_manager.login_view = 'auth.login' 
login_manager.login_message = "Por favor, faça login para acessar esta página."

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Acopla as rotas à aplicação principal
app.register_blueprint(auth_bp)
app.register_blueprint(views_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True)