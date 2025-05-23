import requests
import json
from src.buttons import button_location
from src.buttons import button_sector
from src.buttons import button_both

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
    modelurl = "http://127.0.0.1:11434/api/generate"

    payload = {
        "model": "atlasgpt",
        "prompt": str(instruction)+str(history_text)
    }

    try:
        with requests.post(modelurl, json=payload, stream=True) as response:
            response.raise_for_status()
            full_response = ""

            for line in response.iter_lines():
                if not line:
                    continue

                try:
                    json_response = json.loads(line.decode('utf-8'))

                    if content := json_response.get('response', {}):
                        full_response += content
                        if "None" in full_response:
                            break

                    if json_response.get('done', False):
                        break

                except json.JSONDecodeError as e:
                    print(f"Erro de JSON: {e}")
                    print(f"Linha problemática: {line}")

            print(f"Resposta Completa: {full_response}")
            return full_response

    except requests.RequestException as e:
        print(f"Erro de conexão: {e}")
        return f"ERRO DE CONEXÃO: {e}"


