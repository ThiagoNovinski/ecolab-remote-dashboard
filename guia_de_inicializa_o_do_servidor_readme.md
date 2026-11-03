# Hub Ecolab - Configuração do Servidor (Backend)

Este guia detalha os passos necessários para hospedar o núcleo central do Hub Ecolab (Servidor Web Flask + Banco de Dados PostgreSQL) utilizando Docker. A aplicação é executada em um ambiente isolado (container) com o servidor WSGI Gunicorn, garantindo estabilidade e suporte a múltiplas conexões simultâneas.

## 🛠️ 1. Pré-requisitos

Antes de iniciar, certifique-se de que a máquina que servirá como host no laboratório possui:
- **Docker Desktop** (para Windows/Mac) ou **Docker Engine** (para Linux) instalado e rodando.
- O plugin **Docker Compose** instalado (normalmente já incluso no Docker Desktop).

## ⚙️ 2. Configuração Inicial

1. Transfira a pasta inteira do projeto (`ecolab-remote-dashboard`) para a máquina que será o servidor.
2. Na raiz do projeto, certifique-se de que o arquivo `.env` existe e está configurado corretamente com as variáveis de produção. Exemplo:

```env
POSTGRES_USER=ecolab_admin
POSTGRES_PASSWORD=senha_super_segura
POSTGRES_DB=ecolab_db
DATABASE_URL=postgresql://ecolab_admin:senha_super_segura@db:5432/ecolab_db
SECRET_KEY=sua_chave_secreta_aqui
```
*(Nota: O host na `DATABASE_URL` deve ser obrigatoriamente `db`, pois esse é o nome do container do banco de dados na rede do Docker).*

## 🚀 3. Executando o Servidor

Abra um terminal (Prompt de Comando, PowerShell ou bash) na raiz do projeto e execute o comando abaixo para construir a imagem e iniciar os containers em segundo plano (modo *detached*):

```bash
docker compose up -d --build
```

O Docker fará o download das dependências e iniciará dois containers: `db` (PostgreSQL) e `web` (Gunicorn/Flask).

## 🗄️ 4. Inicializando o Banco de Dados

Como este é um ambiente novo, o banco de dados estará completamente vazio. Para criar as tabelas estruturais necessárias:

1. Acesse o shell interativo do Flask dentro do container `web`:
```bash
docker compose exec web flask shell
```

2. Dentro do shell do Python, execute:
```python
from models import db
db.create_all()
exit()
```

## 👑 5. Criando o Primeiro Administrador

Para acessar o painel de gerenciamento de instâncias, você precisará de uma conta com privilégios de administrador:

1. Acesse a aplicação no navegador em `http://localhost:5000` (ou IP da máquina na rede).
2. Registre uma nova conta de usuário normalmente (ex: `seu_email@exemplo.com`).
3. Para promover este usuário a Administrador, acesse o banco de dados diretamente via container executando no terminal:
```bash
docker compose exec db psql -U ecolab_admin -d ecolab_db -c "UPDATE usuarios SET is_admin = true WHERE email = 'seu_email@exemplo.com';"
```
*(Substitua o email e as credenciais de acordo com o seu arquivo `.env`)*.

## 📡 6. Acesso na Rede Local

Para que os alunos (e os computadores do laboratório) acessem o painel e a API, eles devem utilizar o endereço IP do servidor host na rede local.

- Descubra o IP da máquina host (usando `ipconfig` no Windows ou `ip a` no Linux).
- O acesso será feito pela porta 5000: `http://<IP_DO_SERVIDOR>:5000`.

---

## 🔧 Comandos Úteis do Docker

- **Ver logs em tempo real (útil para debug):**
  `docker compose logs -f`
- **Parar o servidor:**
  `docker compose down`
- **Reiniciar o servidor:**
  `docker compose restart`
- **Parar e apagar completamente o banco de dados (CUIDADO):**
  `docker compose down -v`