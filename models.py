from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Inicializa o objeto do banco de dados, mas AINDA NÃO o conecta ao app
db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    sessoes = db.relationship('Sessao', backref='usuario', lazy=True)

class Maquina(db.Model):
    __tablename__ = 'maquinas'
    
    id = db.Column(db.Integer, primary_key=True)
    identificacao = db.Column(db.String(100), nullable=False)
    rustdesk_id = db.Column(db.String(100), unique=True, nullable=False)
    senha_atual = db.Column(db.String(100))
    status = db.Column(db.String(50), default='disponivel')
    ultimo_heartbeat = db.Column(db.DateTime)
    
    sessoes = db.relationship('Sessao', backref='maquina', lazy=True)

class Sessao(db.Model):
    __tablename__ = 'sessoes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    maquina_id = db.Column(db.Integer, db.ForeignKey('maquinas.id'))
    senha_utilizada = db.Column(db.String(100), nullable=False)
    inicio_sessao = db.Column(db.DateTime, default=datetime.utcnow)
    fim_sessao = db.Column(db.DateTime)
