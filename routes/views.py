from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Maquina, Sessao

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    # Redireciona a raiz do site para o dashboard
    return redirect(url_for('views.dashboard'))

@views_bp.route('/dashboard')
@login_required
def dashboard():
    # Busca todas as máquinas no banco de dados
    maquinas = Maquina.query.all()
    
    # O Flask vai procurar o arquivo "dashboard.html" na pasta "templates"
    return render_template('dashboard.html', maquinas=maquinas)


@views_bp.route('/admin/acessos')
@login_required
def admin_acessos():
    # Verifica se o usuário autenticado possui a flag de administrador
    if not current_user.is_admin:
        flash("Acesso negado. Apenas administradores podem visualizar o histórico.")
        return redirect(url_for('view.dashboard'))

    from models import Sessao
    
    # Busca todas as sessões cadastradas, ordenando da mais recente para a mais antiga
    sessoes = Sessao.query.order_by(Sessao.inicio_sessao.desc()).all()
    
    return render_template('admin_acessos.html', sessoes=sessoes)
