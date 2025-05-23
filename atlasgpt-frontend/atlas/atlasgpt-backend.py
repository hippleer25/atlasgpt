from flask import Flask, request, Response, session, jsonify
from flask_cors import CORS
import os
import requests
import json
import unicodedata
from src.buttons import button_location
from src import start_button
from src import extract_variables
from src import confirmation

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})


app.secret_key = os.urandom(16)

complete_data = data_content = ""


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
                business = data.get('business', [])
                profile = data.get('profile', [])
        else:
            history = []
            business = []
            profile = []
            start_button.init(user_input, user_token, history)
    except Exception as e:
        print(f"Error reading history file: {e}")
        return "Error reading history", 500

    history.append({"role": "user", "content": save_user_input})


    try:
        with open(history_file_path, "w", encoding="utf-8") as file:
            json.dump({'chat_history': history, 'business': business, 'profile': profile}, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error writing history file: {e}")
        return "Error saving history", 500

    modelurl = "http://127.0.0.1:11434/api/chat"
    payload = {
        "model": "atlasgpt",
        "messages": history
    }

    try:
        response = requests.post(modelurl, json=payload, stream=True)
        response.raise_for_status()
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

                try:
                    with open(history_file_path, "r", encoding="utf-8") as file:
                        existing_data = json.load(file)
                    existing_data['chat_history'] = history
                    with open(history_file_path, "w", encoding="utf-8") as file:
                        json.dump(existing_data, file, ensure_ascii=False, indent=4)

                except Exception as e:
                    print(f"Error saving history: {e}")
                    yield "Error saving history"


                confirmation.process_confirmation(user_input, user_token, history, complete_data, payload, modelurl)
            except Exception as e:
                print(f"Error processing response: {e}")
                # yield "Error processing response"

        return Response(generate(), content_type='text/plain;charset=utf-8')

    except requests.RequestException as e:
        print(f"Request exception: {e}")
        return f"Error: {str(e)}", 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
