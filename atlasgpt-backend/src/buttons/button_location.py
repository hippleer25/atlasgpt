import json
import csv
from src import extract_variables
from src import personas


def firstinstruction():
    instruction = (
            '''
            If the user writes english, so answer english. Se o usuário escrever em português, então repsonda em português.
            Você é muito importate e decisivo para encontrarmos a localização do nosso usuário.
            Lembre-se que ele está iniciando ou expandindo seu negócio, e já tem uma localização em mente.
            Sua função principal aqui é encontrar esta localização.
            A localização é em território brasileiro.
            Pergunte onde ficará o negócio que o usuário pretende abrir.
            Comece perguntando do maior para o menor, onde o seu negócio ficará localizado.
            Qual a região de abertura/expansão do negócio (Sul, Sudeste, Norte, Nordeste, Centro-Oeste)?
            Qual o estado?
            Qual o município?
            Qual o bairro?
            Faça as perguntas nessa ordem.
            Realize todas essas perguntas separadamente.
            Elabore as perguntas da maneira mais natural e humana possível.
            Em uma nova mensagem, após o usuário responder a todas as perguntas, pergunte por confirmação das informações. Na sua frase, utilize a palavra "confirma".
            '''
        )
    return instruction




def location(user_input, user_token, history, payload, modelurl):
    instruction = (
        '''
        Do not respond with anything other than what is indicated.
        Write in portuguese.
        You must identify geographic information in the conversation and write: "region=[insert the region here]; state=[insert the state here]; city=[insert the city here]; neighbourhood=[insert the neighbourhood here]".

        Analyze the user"s messages ("user"). If you do not have the information, write "None".

        Example: region="Sul"; state="Rio Grande do Sul"; city="Porto Alegre"; neighbourhood="Farroupilha".
        '''
        )

    user_data = {}
    full_response = extract_variables.api_generate(user_input, user_token, history, payload, modelurl, instruction)
    user_data["region"] = full_response.split("region=")[1].split(";")[0].replace("[","").replace("]","").replace('"','')
    user_data["state"] = full_response.split("state=")[1].split(";")[0].replace("[","").replace("]","").replace('"','')
    user_data["city"] = full_response.split("city=")[1].split(";")[0].replace("[","").replace("]","").replace('"','')
    user_data["neighbourhood"] = full_response.split("neighbourhood=")[1].replace("[","").replace("]","").replace('"','').replace('\\','').replace('.','')

    data = {
        'region': user_data["region"],
        'state': user_data["state"],
        'city': user_data["city"],
        'neighborhood': user_data["neighbourhood"]
    }

    # print(data)
    history_file_path = f"chat_history/user_{user_token}.json"

    try:
        # print("TENTANDO SALVAR")
        with open(history_file_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
            print("Arquivo encontrado e dados carregados.")
    except FileNotFoundError:
        existing_data = {"chat_history": [], "business": []}
        print("Arquivo não encontrado. Criando novo arquivo.")

    existing_data['business'].append(data)

    with open(history_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

    print(f"Data saved to {history_file_path}")

    mpilocation(user_token, history, history_file_path)


def mpilocation(user_token, history, history_file_path):
    # print("ESTAMOS EM MPILOCATION")
    matching_rows = []

    user_data = personas.get_profile(user_token)
    # print(user_data["city"])

    if user_data["city"] != None:
        # print("DIFERENTE")

        # print(f"mpi_{user_data['state'].replace(' ', '_')}")

        with open(f"atlas/database/mpi_{user_data['state'].replace(' ', '_')}.csv", "r",  newline='', encoding='utf-8') as file:
            mpi_city = csv.DictReader(file)
            matching_rows = [row for row in mpi_city if row["NM_MUN"] == user_data["city"]]
            matching_rows.sort(key=lambda row: float(row["MPI"]), reverse=True)

        best_imp = ''
        for i, row in enumerate(matching_rows):
            if i == 1:
                best_imp += f"Melhor gênero de negócio: {row['CNAE_section']}"+"\n"
            if i == 2:
                best_imp += f"Segundo melhor gênero de negócio: {row['CNAE_section']}"+"\n"
            if i == 3:
                best_imp += f"Terceiro melhor gênero de negócio: {row['CNAE_section']}"+"\n"
            if i == 4:
                best_imp += f"Quarto melhor gênero de negócio: {row['CNAE_section']}"+"\n"
            if i == 5:
                best_imp += f"Quinto melhor gênero de negócio: {row['CNAE_section']}"

        instruction = (
                f'''
                Recomendação encontrada!
                Com base no cálculo de Índice Potencial de Mercado (IPM) encontramos o resultado.
                O cálculo foi feito para a cidade escolhida ({user_data["city"]}).
                Os melhores tipos de negócios são:
                {best_imp}
                Explique isso para o usuário.
                Fale de uma maneira bastante natural.
                If the chat language is in english, translate all your response to english.
                '''
            )

        # print(user_data["state"])
        # print(instruction)
        # print("SAINDO", history)
        try:
            # print("TENTANDO SALVAR")
            with open(history_file_path, 'r', encoding='utf-8') as json_file:
                existing_data = json.load(json_file)
                # print(existing_data)
                print("Arquivo encontrado e dados carregados.")
        except FileNotFoundError:
            existing_data = {"chat_history": [], "business": []}
            print("Arquivo não encontrado. Criando novo arquivo.")

        existing_data["chat_history"].append({"role": "system", "content": instruction})

        with open(history_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

        print(f"Data saved to {history_file_path}")
        # print(history)
        # print("A PRINCÍPIO, FOI")
        return instruction
