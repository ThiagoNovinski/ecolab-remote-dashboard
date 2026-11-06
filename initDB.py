import os
from datetime import datetime
from app import app
from models import db, Usuario, Maquina
from werkzeug.security import generate_password_hash

def init_db():
    """Reseta totalmente o banco de dados (drop + create) e insere os dados padrão."""
    with app.app_context():
        print("[1/3] Limpando e recriando tabelas...")
        db.drop_all()
        db.create_all()

        print("[2/3] Criando usuário admin...")
        admin_email = os.getenv("ADMIN_DEFAULT_EMAIL", "admin@furg.br")
        admin_password = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin123")

        admin = Usuario(
            nome="Administrador Ecolab",
            email=admin_email,
            matricula="00000000",
            senha_hash=generate_password_hash(admin_password),
            is_active=True,
            is_admin=True
        )
        db.session.add(admin)

        print("[3/3] Criando máquinas de teste...")
        maquinas_placeholder = [
            {
                "identificacao": "ECOLAB-01",
                "rustdesk_id": "111222333",
                "senha_atual": "123456",
                "ultimo_heartbeat": datetime.utcnow()
            },
            {
                "identificacao": "ECOLAB-02",
                "rustdesk_id": "444555666",
                "senha_atual": "abcdef",
                "ultimo_heartbeat": datetime.utcnow()
            },
        ]

        for item in maquinas_placeholder:
            nova_maquina = Maquina(
                identificacao=item["identificacao"],
                rustdesk_id=item["rustdesk_id"],
                senha_atual=item["senha_atual"],
                status="disponivel",
                ativo=True,
                ultimo_heartbeat=item["ultimo_heartbeat"]
            )
            db.session.add(nova_maquina)

        db.session.commit()
        print("\n[ÉXITO] Banco de dados resetado e inicializado do zero!")

if __name__ == "__main__":
    init_db()