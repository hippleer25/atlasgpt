from flask import Flask, request, Response, session, jsonify
from flask_cors import CORS
import os
import requests
import json
import unicodedata
from src import button_location
from src import personas

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})
# button_clicked = 0

app.secret_key = os.urandom(16)  # Securely generate a secret key

@app.route('/api/token', methods=['GET', 'POST'])
def generate_token():
    if 'user_token' not in session:
        session['user_token'] = os.urandom(16).hex()
    return jsonify({'user_token': session['user_token']}), 200

@app.route('/api', methods=['GET'])
def search():
    user_input = request.args.get('q')
    user_token = request.args.get('t')

    if not user_input or not user_token:
        return "Missing query parameters", 400

    save_user_input = unicodedata.normalize('NFC', user_input)

    print(f"User Input: {user_input}")
    print(f"User Token: {user_token}")

    if not os.path.exists("chat_history"):
        os.makedirs("chat_history")

    history_file_path = f"chat_history/user_{user_token}.json"

    try:
        if os.path.exists(history_file_path):
            with open(history_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                history = data.get('chat_history', [])
                location = data.get('location', [])
                profile = data.get('profile', [])
        else:
            history = []
            location = []
            profile = []
    except Exception as e:
        print(f"Error reading history file: {e}")
        return "Error reading history", 500

    history.append({"role": "user", "content": save_user_input})


    if user_input.startswith("AtlasGPT,"):
        if user_input == "AtlasGPT, já tenho uma ideia de onde ficaria meu nogócio!":
            # button_clicked = 1
            # print(button_clicked)
            button_instruction = button_location.firstinstruction()
            print(button_instruction)
            history.insert(0, {"role": "system", "content": button_instruction})

    try:
        with open(history_file_path, "w", encoding="utf-8") as file:
            json.dump({'chat_history': history, 'location': location, 'profile': profile}, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error writing history file: {e}")
        return "Error saving history", 500

    llamaurl = "http://127.0.0.1:11434/api/chat"
    payload = {
        "model": "atlasgpt",
        "messages": history
    }

    try:
        response = requests.post(llamaurl, json=payload, stream=True)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        print(f"Response Status Code: {response.status_code}")

        def generate():
            complete_data = ""
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    data = chunk.decode('utf-8')

                    try:
                        json_data = json.loads(data)
                        if 'message' in json_data and 'content' in json_data['message']:
                            data_content = json_data['message']['content']
                            complete_data += data_content
                            yield data_content
                    except json.JSONDecodeError as e:
                        print(f"JSON Decode Error: {e}")
                        continue

                history.append({"role": "assistant", "content": complete_data})
                if "Você" in complete_data and "confirma" in complete_data:
                    print("BUTTON LOCATION")
                    try:
                        if "Você" in complete_data and "confirma" in complete_data and "localização" in complete_data and "?" in complete_data:
                            print("CONFIRMANDO LOCALIZAÇÃO")
                            button_location.locationconfirm(complete_data, user_token)
                            print(button_location.secondinstruction())
                            history.append({"role": "system", "content": button_location.secondinstruction()})

                        elif "Você confirma o valor do aluguel de" in complete_data and "políticas" in complete_data and "?" in complete_data:
                            print("CONFIRMANDO ALUGUEL")
                            button_location.priceconfirm(complete_data, user_token)
                            print("VOLTAMOS")
                            personas.search(user_token)

                    except Exception as error:
                        pass
                else:
                    # print("SEM BOTÃO", button_clicked)
                    pass

                try:
                    with open(history_file_path, "r", encoding="utf-8") as file:
                        existing_data = json.load(file)
                    existing_data['chat_history'] = history
                    with open(history_file_path, "w", encoding="utf-8") as file:
                        json.dump(existing_data, file, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(f"Error saving history: {e}")
                    yield "Error saving history"

            except Exception as e:
                print(f"Error processing response: {e}")
                yield "Error processing response"

        return Response(generate(), content_type='text/plain;charset=utf-8')

    except requests.RequestException as e:
        print(f"Request exception: {e}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
