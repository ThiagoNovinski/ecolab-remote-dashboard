import os
from flask import Flask
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configura a aplicação usando as variáveis do .env
# O segundo argumento é um valor padrão caso a variável não seja encontrada
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave_padrao_de_teste')

# Rota básica para testar se o servidor está rodando
@app.route('/')
def index():
    return """
    <h1>Servidor do Secure Remote Access Hub rodando! 🚀</h1>
    <p>A aplicação Flask foi iniciada com sucesso no laboratório Ecolab.</p>
    """

if __name__ == '__main__':
    # Executa o servidor em modo de depuração (debug=True)
    # Isso faz com que o servidor reinicie automaticamente se você alterar o código
    app.run(debug=True)