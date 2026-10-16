import os
from flask import Flask
from dotenv import load_dotenv
from flask import request, jsonify, render_template
from datetime import datetime
from flask import render_template_string
from models import db, Usuario, Maquina, Sessao

# Carrega as variáveis de ambiente
load_dotenv()

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configurações
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Conecta o banco de dados (que foi criado no models.py) com a aplicação Flask
db.init_app(app)

# Rotas da API
@app.route('/')
def index():
    Usuario.query.all()
    return "API conectada e rodando com modelos separados!"

@app.route('/dashboard')
def dashboard():
    # Busca todas as máquinas no banco de dados
    maquinas = Maquina.query.all()
    
    # O Flask vai procurar o arquivo "dashboard.html" na pasta "templates"
    return render_template('dashboard.html', maquinas=maquinas)

@app.route('/status', methods=['POST'])
def update_status():
    # Recebe os dados enviados pela máquina cliente em formato JSON
    dados = request.get_json()

    # Validação de segurança básica
    if not dados or 'rustdesk_id' not in dados:
        return jsonify({"erro": "Dados inválidos ou rustdesk_id ausente"}), 400

    rustdesk_id = dados.get('rustdesk_id')
    senha_atual = dados.get('senha')
    identificacao = dados.get('identificacao', f'PC-{rustdesk_id}')

    # Verifica se esta máquina já existe no banco de dados
    maquina = Maquina.query.filter_by(rustdesk_id=rustdesk_id).first()

    if maquina:
        # Atualiza a máquina existente
        maquina.senha_atual = senha_atual
        maquina.status = 'disponivel'
        maquina.ultimo_heartbeat = datetime.utcnow()
    else:
        # Cadastra a máquina automaticamente no primeiro contato (Auto-Registro)
        maquina = Maquina(
            identificacao=identificacao,
            rustdesk_id=rustdesk_id,
            senha_atual=senha_atual,
            status='disponivel',
            ultimo_heartbeat=datetime.utcnow()
        )
        db.session.add(maquina)

    # Efetiva as alterações no PostgreSQL
    db.session.commit()

    return jsonify({
        "mensagem": "Status recebido com sucesso", 
        "maquina_id": maquina.id,
        "identificacao": maquina.identificacao
    }), 200

@app.route('/acessar', methods=['POST'])
def solicitar_acesso():
    dados = request.get_json()
    usuario_id = dados.get('usuario_id')
    maquina_id = dados.get('maquina_id')

    # Validação básica
    if not usuario_id or not maquina_id:
        return jsonify({"erro": "usuario_id e maquina_id são obrigatórios"}), 400

    from models import Usuario, Maquina, Sessao, db
    
    usuario = Usuario.query.get(usuario_id)
    maquina = Maquina.query.get(maquina_id)

    if not usuario or not maquina:
        return jsonify({"erro": "Usuário ou Máquina não encontrados"}), 404

    if maquina.status != 'disponivel':
        return jsonify({"erro": "Máquina ocupada ou indisponível"}), 403

    # 1. Cria o log de auditoria na tabela sessoes
    nova_sessao = Sessao(
        usuario_id=usuario.id,
        maquina_id=maquina.id,
        senha_utilizada=maquina.senha_atual
    )
    
    # 2. Bloqueia a máquina para outros usuários
    maquina.status = 'em_uso'

    db.session.add(nova_sessao)
    db.session.commit()

    return jsonify({
        "mensagem": "Acesso concedido",
        "sessao_id": nova_sessao.id,
        "senha_liberada": maquina.senha_atual
    }), 200

@app.route('/desconectar', methods=['POST'])
def desconectar():
    dados = request.get_json()
    sessao_id = dados.get('sessao_id')

    # Validação básica
    if not sessao_id:
        return jsonify({"erro": "sessao_id é obrigatório"}), 400

    from models import Sessao, Maquina, db
    from datetime import datetime
    
    sessao = Sessao.query.get(sessao_id)

    if not sessao:
        return jsonify({"erro": "Sessão não encontrada"}), 404

    if sessao.fim_sessao:
        return jsonify({"erro": "Esta sessão já foi encerrada anteriormente"}), 400

    # 1. Registra o fim da sessão no log de auditoria
    sessao.fim_sessao = datetime.utcnow()

    # 2. Libera a máquina associada a esta sessão
    maquina = Maquina.query.get(sessao.maquina_id)
    if maquina:
        maquina.status = 'disponivel'

    db.session.commit()

    return jsonify({
        "mensagem": "Desconectado com sucesso, máquina liberada para uso",
        "sessao_id": sessao.id,
        "maquina_id": maquina.id if maquina else None
    }), 200

@app.route('/admin/acessos')
def admin_acessos():
    from models import Sessao
    
    # Busca todas as sessões cadastradas, ordenando da mais recente para a mais antiga
    sessoes = Sessao.query.order_by(Sessao.inicio_sessao.desc()).all()
    
    return render_template('admin_acessos.html', sessoes=sessoes)

if __name__ == '__main__':
    app.run(debug=True)