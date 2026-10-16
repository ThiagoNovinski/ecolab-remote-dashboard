import requests

# Simulando o encerramento da sessão que criamos no passo anterior (ID 1)
payload = {
    "sessao_id": 1
}

resposta = requests.post("http://127.0.0.1:5000/desconectar", json=payload)

print(f"Status Code: {resposta.status_code}")
print(f"Resposta da API: {resposta.json()}")