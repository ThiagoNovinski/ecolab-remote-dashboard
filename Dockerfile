FROM python:3.11-slim

WORKDIR /app

# Instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta que o Gunicorn vai utilizar
EXPOSE 5000

# Inicia o servidor WSGI
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]