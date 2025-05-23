from src import start_button
from src import extract_variables

def process_confirmation(user_input, user_token, history, complete_data, payload, modelurl):
    data_content = ""
    if "onfirm" in complete_data:
        extract_variables.init(user_input, user_token, history, start_button.start_button_clicked, payload, modelurl)
        complete_data = ""
    return complete_data, data_content
