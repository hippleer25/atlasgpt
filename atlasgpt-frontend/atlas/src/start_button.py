from src.buttons import button_location
from src.buttons import button_sector
from src.buttons import button_both

start_button_clicked = None

def init(user_input, user_token, history):
    global start_button_clicked
    print(user_input)
    if user_input == "Eu já tenho uma localização" or user_input == "I already have a location":
        print("INDO PRA LOCALIZAÇÃO")
        start_button_clicked = location(user_input, user_token, history)
        print('achou setor')
    elif user_input == "Eu já tenho um setor econômico" or user_input == "I already have a economic sector":
        print("INDO PRO SETOR")
        start_button_clicked = sector(user_input, user_token, history)
    elif user_input == "Eu tenho um setor e uma localização" or user_input == "I already have a sector and a location":
        print("INDO PRA AMBOS")
        start_button_clicked = both(user_input, user_token, history)
    return start_button_clicked

def location(user_input, user_token, history):
    button_instruction = button_location.firstinstruction()
    print("--------------------------------------------LOCALIZAÇÃO--------------------------------------------")
    history.insert(0, {"role": "system", "content": button_instruction})
    return 1

def sector(user_input, user_token, history):
    button_instruction = button_sector.firstinstruction()
    print("-----------------------------------------------SETOR-----------------------------------------------")
    print(button_instruction)
    history.insert(0, {"role": "system", "content": button_instruction})
    return 2

def both(user_input, user_token, history):
    button_instruction = button_both.firstinstruction()
    print("-----------------------------------------------AMBOS-----------------------------------------------")
    print(button_instruction)
    history.insert(0, {"role": "system", "content": button_instruction})
    return 3
