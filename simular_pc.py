import requests

# Simulando os dados que o cliente RustDesk enviaria
payload = {
    "identificacao": "Ecolab-PC-01",
    "rustdesk_id": "123456789",
    "senha": "senha_dinamica_abc123"
}

# Dispara o POST para a sua API local
resposta = requests.post("http://127.0.0.1:5000/status", json=payload)

print(f"Status Code: {resposta.status_code}")
print(f"Resposta da API: {resposta.json()}")