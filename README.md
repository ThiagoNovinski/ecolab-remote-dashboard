Secure Remote Access Hub
Dashboard web e hub centralizado para o gerenciamento de acesso remoto seguro a computadores. Desenvolvido no laboratório Ecolab (FURG), o sistema permite monitorar o status de máquinas em rede e solicitar credenciais de acesso temporárias, aplicando a rotação automática de chaves ao fim de cada sessão.

Funcionalidades
Monitoramento em Tempo Real: Visualização do status das máquinas conectadas (online/offline e métricas básicas de uso).

Geração de Credenciais sob Demanda: Botão de solicitação de acesso remoto temporário direto na interface web.

Rotação Automática de Chaves: Invalidação e troca da senha do software de controle imediatamente após a desconexão do usuário, prevenindo acessos não autorizados subsequentes.

Controle Centralizado (Hub): Servidor principal que aloca e distribui o controle para os nós da rede.

Tecnologias Utilizadas
Back-end: Python, Flask

Banco de Dados: PostgreSQL

Front-end: HTML5, CSS3 (Vanilla)

Software de Acesso Remoto: A definir (em fase de pesquisa de viabilidade técnica para integração via CLI ou API)

Estrutura Inicial do Projeto
/app: Núcleo da aplicação Flask, rotas, modelos de banco de dados e lógica de negócio.

/templates: Arquivos HTML do dashboard.

/static: Arquivos CSS para a estilização da interface.

/client_scripts: Scripts de automação que serão instalados nas máquinas clientes para receber comandos do hub e executar a troca local da chave de acesso.

Como Executar (Ambiente de Desenvolvimento)
1. Clone o repositório

Bash
git clone https://github.com/seu-usuario/secure-remote-access-hub.git
cd secure-remote-access-hub
2. Configure o Banco de Dados
Certifique-se de ter o PostgreSQL rodando localmente e crie um banco de dados dedicado para o projeto.

3. Crie e ative o ambiente virtual Python

Bash
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
4. Instale as dependências

Bash
pip install -r requirements.txt
5. Configure as Variáveis de Ambiente
Crie um arquivo .env na raiz do projeto (este arquivo não deve ser commitado) e adicione as seguintes chaves:

Snippet de código
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta_aqui
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
6. Execute a aplicação

Bash
flask run
O painel estará acessível através do navegador em [http://127.0.0.1:5000](http://127.0.0.1:5000).
