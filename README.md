# Secure Remote Access Hub

Dashboard web e hub centralizado para o gerenciamento de acesso remoto
seguro a computadores. Desenvolvido no laboratório Ecolab (FURG), o
sistema permite monitorar o status de máquinas em rede e solicitar
credenciais de acesso temporárias, aplicando a rotação automática de
chaves ao fim de cada sessão.

## Funcionalidades

-   **Monitoramento em tempo real:** visualização do status das máquinas
    conectadas (online/offline e métricas básicas de uso).
-   **Geração de credenciais sob demanda:** solicitação de acesso remoto
    temporário diretamente pela interface web.
-   **Rotação automática de chaves:** invalidação e troca da senha do
    software de controle imediatamente após a desconexão do usuário,
    prevenindo acessos não autorizados subsequentes.
-   **Controle centralizado (hub):** servidor principal responsável por
    alocar e distribuir o controle para os nós da rede.

## Tecnologias utilizadas

-   **Back-end:** Python e Flask.
-   **Banco de dados:** PostgreSQL.
-   **Front-end:** HTML5 e CSS3 (Vanilla).
-   **Software de acesso remoto:** RustDesk.

## Estrutura inicial do projeto

``` text
/
├── app/                 # Núcleo da aplicação Flask: rotas, modelos e regras de negócio
├── templates/           # Templates HTML do dashboard
├── static/              # Arquivos estáticos, incluindo CSS
├── client_scripts/      # Scripts executados nas máquinas clientes
├── run.py               # Ponto de entrada da aplicação
├── requirements.txt     # Dependências Python
├── .env                 # Variáveis de ambiente (não versionar)
└── README.md
```

Os diretórios e arquivos acima representam a estrutura inicial planejada
e podem ser ajustados durante o desenvolvimento.

## Arquitetura e Fluxo de Comunicação

Para evitar bloqueios de firewall na rede da universidade, o sistema utiliza uma arquitetura de *Polling / Heartbeat*, onde a máquina cliente sempre inicia a comunicação com o servidor central.

```mermaid
sequenceDiagram
    actor User as Usuário (Front-end)
    participant API as API (Flask / Hub)
    participant DB as Banco de Dados (PostgreSQL)
    participant PC as Script Cliente (PC 1 - RustDesk)

    %% Fluxo de Inicialização / Cadastro de Senha (PC -> Hub)
    Note over PC, DB: Conexão iniciada pelo cliente (Outbound) evita bloqueios
    PC->>PC: 1. Gera senha inicial do RustDesk
    PC->>API: 2. Envia ID e Senha ativa (POST /status)
    API->>DB: 3. Salva credenciais e marca como 'Disponível'

    %% Fluxo de Solicitação de Acesso (Instantâneo)
    User->>API: 4. Solicita acesso remoto
    API->>DB: 5. Consulta máquina 'Disponível'
    DB-->>API: 6. Retorna dados e senha armazenada do PC 1
    API->>DB: 7. Registra sessão e altera status para 'Ocupado'
    API-->>User: 8. Exibe credencial instantaneamente na interface web

    %% Fluxo de Encerramento (Polling / Heartbeat)
    User->>API: 9. Aciona botão "Encerrar Conexão"
    API->>DB: 10. Altera status da máquina para 'Aguardando Rotação'
    
    Note over PC, API: O PC faz consultas periódicas de poucos segundos (Heartbeat)
    PC->>API: 11. Heartbeat: "Qual o meu status?" (GET /status)
    API-->>PC: 12. Responde: "Sessão encerrada, rotacionar chave"
    
    PC->>PC: 13. Altera senha local do RustDesk
    PC->>API: 14. Envia nova senha gerada (POST /status)
    API->>DB: 15. Atualiza DB com nova senha e marca como 'Disponível' ```

## Modelagem do Banco de Dados
erDiagram
    USUARIOS ||--o{ SESSOES : realiza
    MAQUINAS ||--o{ SESSOES : recebe

    USUARIOS {
        int id PK
        string nome
        string email_matricula UK "Único (Para login)"
        string senha_hash "Senha criptografada"
    }

    MAQUINAS {
        int id PK
        string identificacao "Ex: PC-Bancada-01"
        string rustdesk_id UK "ID fixo do RustDesk"
        string senha_atual "Chave temporária ativa"
        string status "disponivel, ocupado, aguardando_rotacao, offline"
        timestamp ultimo_heartbeat "Para checar se o PC está ligado"
    }

    SESSOES {
        int id PK
        int usuario_id FK
        int maquina_id FK
        string senha_utilizada "Log de auditoria de segurança"
        timestamp inicio_sessao
        timestamp fim_sessao "Pode ser nulo até o encerramento"
    }

## Como executar em ambiente de desenvolvimento

### 1. Clonar o repositório

``` bash
git clone https://github.com/ThiagoNovinski/ecolab-remote-dashboard
cd secure-remote-access-hub
```


### 2. Configurar o banco de dados

Certifique-se de que o PostgreSQL esteja instalado e em execução. Crie
um banco de dados dedicado ao projeto e tenha em mãos as credenciais de
conexão.

### 3. Criar e ativar o ambiente virtual Python

``` bash
python -m venv venv
```

Linux/macOS:

``` bash
source venv/bin/activate
```

Windows (Prompt de Comando):

``` bat
venv\Scripts\activate.bat
```

Windows (PowerShell):

``` powershell
.\venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

Com o ambiente virtual ativado, execute:

``` bash
pip install -r requirements.txt
```

### 5. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto. **Não versione esse arquivo
nem compartilhe segredos reais.**

Exemplo de configuração:

``` ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=substitua_por_uma_chave_secreta
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
```

Ajuste os valores de conexão conforme a configuração local do
PostgreSQL. Para ambientes de produção, use uma chave secreta forte e
configure as variáveis de ambiente de acordo com o método de implantação
escolhido.

### 6. Executar a aplicação

Com o ambiente virtual ativado e as variáveis configuradas:

``` bash
flask run
```

O painel deverá estar disponível no endereço:

<http://127.0.0.1:5000>

## Segurança e considerações de desenvolvimento

-   As credenciais temporárias devem ter escopo e duração limitados.
-   A troca de senha deve ocorrer de forma autenticada e segura, com
    tratamento de falhas e registro de auditoria.
-   Os scripts clientes devem autenticar as mensagens recebidas do hub e
    rejeitar comandos não autorizados.
-   Segredos, senhas e credenciais de acesso não devem ser gravados em
    logs nem armazenados em texto puro.
-   O acesso ao dashboard deve exigir autenticação e autorização
    adequadas.
-   A integração com o software de acesso remoto ainda precisa ser
    definida e validada quanto à viabilidade técnica.

## Status do projeto

Projeto em fase inicial de definição e desenvolvimento. A escolha do
software de acesso remoto e a integração com seus mecanismos de CLI ou
API permanecem pendentes de pesquisa técnica.
