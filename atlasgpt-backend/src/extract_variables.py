import requests
import json
from src.buttons import button_location
from src.buttons import button_sector
from src.buttons import button_both
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente (para a API key da OpenAI)
load_dotenv()

# Configuração da API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4.1-nano"  # ou outro modelo de sua escolha como "gpt-4"

def init(user_input, user_token, history, start_button_clicked, payload, modelurl):
    if start_button_clicked == 1:
        print("INSTRUÇÃO DA LOCALIZAÇÃO")
        return button_location.location(user_input, user_token, history, payload, modelurl)
    elif start_button_clicked == 2:
        print("INSTRUÇÃO DO SETOR")
        return button_sector.sector(user_input, user_token, history, payload, modelurl)
    elif start_button_clicked == 3:
        print("INSTRUÇÃO DO SETOR")
        num_inst = 0
        if num_inst == 0:
            print("PRIMEIRA PARTE DE BOTH")
            return button_both.sector(user_input, user_token, history, payload, modelurl)
            num_inst += 1
        elif num_inst == 1:
            print("SEGUNDA PARTE DE BOTH")
            return button_both.location(user_input, user_token, history, payload, modelurl)

def api_generate(user_input, user_token, history, payload, modelurl, instruction):
    history_text = [msg for msg in history if msg["role"] == "user" or msg["role"] == "assistant"]

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Preparar payload para a API da OpenAI
    openai_payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "system", "content": instruction}] + history_text
    }

    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=openai_payload)
        response.raise_for_status()

        # Processar a resposta da OpenAI
        json_response = response.json()
        full_response = json_response["choices"][0]["message"]["content"]

        print(f"Resposta Completa: {full_response}")
        return full_response

    except requests.RequestException as e:
        print(f"Erro de conexão: {e}")
        return f"ERRO DE CONEXÃO: {e}"
