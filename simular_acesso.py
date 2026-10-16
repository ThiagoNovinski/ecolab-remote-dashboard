import requests

# Simulando o usuário ID 1 solicitando acesso à máquina ID 1
payload = {
    "usuario_id": 1,
    "maquina_id": 1
}

resposta = requests.post("http://127.0.0.1:5000/acessar", json=payload)

print(f"Status Code: {resposta.status_code}")
print(f"Resposta da API: {resposta.json()}")