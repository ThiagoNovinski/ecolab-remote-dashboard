# Secure Remote Access Hub

Dashboard web e hub centralizado para o gerenciamento de acesso remoto seguro a computadores. Desenvolvido no laboratório Ecolab (FURG), o sistema permite monitorar o status de máquinas em rede e solicitar credenciais de acesso temporárias, com o objetivo de revogar o acesso ao fim de cada sessão.

## Funcionalidades

- **Monitoramento em tempo real:** visualização do status das máquinas conectadas (online/offline e métricas básicas de uso).
- **Geração de credenciais sob demanda:** solicitação de acesso remoto temporário diretamente pela interface web.
- **Rotação de credenciais:** renovação ou invalidação da credencial de acesso após o encerramento da sessão, conforme os recursos suportados pelo software remoto.
- **Controle centralizado (hub):** servidor principal responsável por coordenar as solicitações de acesso e a comunicação com os nós da rede.

## Tecnologias utilizadas

- **Back-end:** Python e Flask.
- **Banco de dados:** PostgreSQL.
- **Front-end:** HTML5 e CSS3 (Vanilla).
- **Software de acesso remoto:** RustDesk.

## Estrutura inicial do projeto

```text
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

Os diretórios e arquivos acima representam a estrutura inicial planejada e podem ser ajustados durante o desenvolvimento.

## Arquitetura e fluxo de comunicação

Para reduzir a necessidade de conexões de entrada nas máquinas clientes, a proposta utiliza *polling/heartbeat*: cada script cliente inicia periodicamente uma conexão de saída com o servidor central. A viabilidade dessa abordagem e a integração com os recursos do RustDesk deverão ser validadas durante o desenvolvimento.

### Diagrama de sequência

```mermaid
sequenceDiagram
    autonumber
    actor User as Usuário
    participant Web as Dashboard Web
    participant API as API Flask / Hub
    participant DB as PostgreSQL
    participant PC as Script Cliente (PC 1)

    Note over PC,API: O cliente inicia a comunicação de saída por polling/heartbeat

    rect rgb(235,245,255)
        Note over PC,DB: Inicialização e registro da máquina
        PC->>API: Envia ID da máquina e estado (POST /status)
        API->>DB: Registra ou atualiza estado e último heartbeat
        DB-->>API: Confirma atualização
        API-->>PC: Confirma recebimento
    end

    rect rgb(240,255,240)
        Note over User,DB: Solicitação de acesso
        User->>Web: Solicita acesso à máquina
        Web->>API: Envia solicitação autenticada
        API->>DB: Verifica disponibilidade e permissões
        DB-->>API: Retorna estado e dados da máquina
        API->>DB: Registra sessão e reserva a máquina
        API-->>Web: Retorna autorização ou instruções de conexão
        Web-->>User: Apresenta as instruções de acesso
    end

    rect rgb(255,248,235)
        Note over User,DB: Encerramento e revogação do acesso
        User->>Web: Solicita encerramento da sessão
        Web->>API: Envia solicitação autenticada de encerramento
        API->>DB: Marca sessão como encerrando
        API->>DB: Altera status da máquina para aguardando_rotacao
        PC->>API: Consulta estado da máquina (GET /status)
        API-->>PC: Informa que o acesso deve ser revogado ou renovado
        PC->>PC: Executa a ação local suportada pelo RustDesk
        PC->>API: Informa o resultado da operação (POST /status)
        API->>DB: Atualiza estado, heartbeat e resultado da operação
        API-->>Web: Disponibiliza o estado atualizado
        Web-->>User: Exibe o resultado do encerramento
    end
```

> **Observação:** o diagrama representa o fluxo pretendido. Os endpoints, o formato das mensagens e a possibilidade de alterar credenciais do RustDesk por script ainda precisam ser implementados e testados. A expiração de uma autorização no hub, por si só, não encerra necessariamente uma sessão remota já estabelecida.

## Modelagem do banco de dados

O diagrama abaixo representa uma proposta inicial de entidades e relacionamentos. Os campos poderão ser ajustados conforme a implementação.

### Diagrama entidade-relacionamento

```mermaid
erDiagram
    USUARIOS ||--o{ SESSOES : realiza
    MAQUINAS ||--o{ SESSOES : recebe

    USUARIOS {
        int id PK
        string nome
        string email_matricula UK
        string senha_hash
    }

    MAQUINAS {
        int id PK
        string identificacao
        string rustdesk_id UK
        string status
        timestamp ultimo_heartbeat
    }

    SESSOES {
        int id PK
        int usuario_id FK
        int maquina_id FK
        timestamp inicio_sessao
        timestamp fim_sessao
        string status
    }
```

**Nota de segurança:** as senhas dos usuários devem ser armazenadas como hashes seguros. As credenciais de acesso remoto não devem ser armazenadas em texto puro nem incluídas diretamente nos registros de auditoria. Caso seja necessário gerenciar segredos, utilize um mecanismo apropriado de armazenamento e controle de acesso.

## Como executar em ambiente de desenvolvimento

### 1. Clonar o repositório

```bash
git clone https://github.com/ThiagoNovinski/ecolab-remote-dashboard.git
cd ecolab-remote-dashboard
```

### 2. Configurar o banco de dados

Certifique-se de que o PostgreSQL esteja instalado e em execução. Crie um banco de dados dedicado ao projeto e tenha em mãos as credenciais de conexão.

### 3. Criar e ativar o ambiente virtual Python

```bash
python -m venv venv
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

**Windows (Prompt de Comando):**

```bat
venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

Com o ambiente virtual ativado, execute:

```bash
pip install -r requirements.txt
```

### 5. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto. **Não versione esse arquivo nem compartilhe segredos reais.**

Exemplo de configuração:

```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=substitua_por_uma_chave_secreta
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
```

Ajuste os valores de conexão conforme a configuração local do PostgreSQL. Para ambientes de produção, utilize uma chave secreta forte e configure as variáveis de ambiente de acordo com o método de implantação escolhido.

### 6. Executar a aplicação

Com o ambiente virtual ativado e as variáveis configuradas:

```bash
flask run
```

O painel deverá estar disponível no endereço:

http://127.0.0.1:5000

## Segurança e considerações de desenvolvimento

- As credenciais temporárias devem ter escopo e duração limitados.
- A troca ou revogação de credenciais deve ocorrer por um canal autenticado, com tratamento de falhas e registro de auditoria.
- Os scripts clientes devem autenticar as mensagens recebidas do hub e rejeitar comandos não autorizados.
- Segredos, senhas e credenciais de acesso não devem ser gravados em logs nem armazenados em texto puro.
- O acesso ao dashboard deve exigir autenticação e autorização adequadas.
- A comunicação entre o hub e os clientes deve utilizar mecanismos seguros de autenticação e criptografia em trânsito.
- O mecanismo de encerramento de sessões e a integração com os recursos do RustDesk precisam ser validados tecnicamente.

## Status do projeto

Projeto em fase inicial de definição e desenvolvimento. A arquitetura de comunicação está proposta, mas os endpoints, a integração com o RustDesk e o mecanismo de revogação ou rotação de credenciais ainda precisam ser implementados e testados.