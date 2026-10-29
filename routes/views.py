from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Maquina, Sessao
from flask import request

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    # Redireciona a raiz do site para o dashboard
    return redirect(url_for('views.dashboard'))

@views_bp.route('/dashboard')
@login_required
def dashboard():
    # Busca todas as máquinas no banco de dados
    maquinas = Maquina.query.filter_by(ativo=True).all()
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


@views_bp.route('/admin/maquinas', methods=['GET', 'POST'])
@login_required
def admin_maquinas():
    if not current_user.is_admin:
        flash("Acesso negado. Apenas administradores podem gerenciar máquinas.")
        return redirect(url_for('views.dashboard'))

    from models import db, Maquina

    if request.method == 'POST':
        identificacao = request.form.get('identificacao').strip().upper()
        rustdesk_id = request.form.get('rustdesk_id').strip().lower()

        # Verifica se o ID já existe e está ativo
        maquina_existente = Maquina.query.filter_by(rustdesk_id=rustdesk_id).first()
        
        if maquina_existente and maquina_existente.ativo:
            flash("Já existe uma máquina ativa com este RustDesk ID cadastrada.")
        elif maquina_existente and not maquina_existente.ativo:
            # Reativa a máquina caso ela tenha sido "excluída" no passado
            maquina_existente.ativo = True
            maquina_existente.identificacao = identificacao
            db.session.commit()
            flash(f"Máquina {identificacao} reativada com sucesso!")
        else:
            nova_maquina = Maquina(
                identificacao=identificacao,
                rustdesk_id=rustdesk_id,
                senha_atual="Aguardando conexão...",
                status="disponivel",
                ativo=True
            )
            db.session.add(nova_maquina)
            db.session.commit()
            flash(f"Máquina {identificacao} registrada com sucesso!")
            
        return redirect(url_for('views.admin_maquinas'))

    # Exibe apenas as máquinas ativas na tabela do painel admin
    maquinas = Maquina.query.filter_by(ativo=True).order_by(Maquina.identificacao).all()
    return render_template('admin_maquinas.html', maquinas=maquinas)


@views_bp.route('/admin/maquinas/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_maquina(id):
    if not current_user.is_admin:
        return redirect(url_for('views.dashboard'))

    from models import db, Maquina
    maquina = Maquina.query.get(id)

    if maquina:
        # Exclusão Lógica: apenas oculta a máquina, mantendo o histórico de acessos intacto
        maquina.ativo = False
        db.session.commit()
        flash("Máquina removida do painel, mas o histórico de sessões foi preservado.")

    return redirect(url_for('views.admin_maquinas'))

