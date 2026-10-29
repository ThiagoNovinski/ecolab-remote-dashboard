from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario, db
from flask_login import login_required

# Criação do Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')
        
        from models import Usuario, db
        
        # Verifica se o e-mail ou a matrícula já existem
        if Usuario.query.filter_by(email=email).first():
            flash("E-mail já cadastrado!")
            return redirect(url_for('auth.registro'))
            
        if Usuario.query.filter_by(matricula=matricula).first():
            flash("Matrícula já cadastrada!")
            return redirect(url_for('auth.registro'))
            
        senha_criptografada = generate_password_hash(senha)
        
        # O primeiro usuário criado pode ser admin manualmente depois no pgAdmin
        novo_usuario = Usuario(
            nome=nome, 
            email=email, 
            matricula=matricula, 
            senha_hash=senha_criptografada,
            is_active=True,
            is_admin=False
        )
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash("Conta criada com sucesso! Faça seu login.")
        return redirect(url_for('views.login'))
        
    return render_template('registro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        from models import Usuario
        usuario = Usuario.query.filter_by(email=email).first()
        
        # Verifica credenciais e se a conta está ativa
        if usuario and check_password_hash(usuario.senha_hash, senha):
            if not usuario.is_active:
                flash("Sua conta está desativada. Procure o administrador.")
                return redirect(url_for('views.login'))
                
            login_user(usuario)
            return redirect(url_for('views.dashboard'))
        else:
            flash("E-mail ou senha inválidos.")
            
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        # Verifica se a senha atual digitada está correta
        if not check_password_hash(current_user.senha_hash, senha_atual):
            flash("A senha atual está incorreta. Tente novamente.")
            return redirect(url_for('auth.alterar_senha'))
            
        # Verifica se a nova senha e a confirmação batem
        if nova_senha != confirmar_senha:
            flash("As novas senhas não coincidem.")
            return redirect(url_for('auth.alterar_senha'))
            
        # Gera o hash da nova senha e atualiza no banco
        from models import db
        current_user.senha_hash = generate_password_hash(nova_senha)
        db.session.commit()
        
        flash("Senha alterada com sucesso!")
        return redirect(url_for('views.dashboard'))
        
    return render_template('alterar_senha.html')
