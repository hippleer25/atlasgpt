import json
import csv
from src import extract_variables
import unicodedata

print("LENDO SETOR")

def mpilocationsector(user_token, history, history_file_path):
   print("Calculando MPI para ambos")
   # print("ESTAMOS EM MPILOCATION")
   matching_rows = []
   # history_file_path = f"chat_history/user_{user_token}.json"
   try:
       # print("TENTANDO SALVAR")
       with open(history_file_path, 'r', encoding='utf-8') as json_file:
           user_data = json.load(json_file)
           print("Arquivo encontrado e dados carregados.")
   except FileNotFoundError:
       user_data = {"chat_history": [], "business": []}
       print("Arquivo não encontrado. Criando novo arquivo.")

   print(user_data)
   print('------------------------------------------------------------------------------------------')
   print("setor economico")
   print("Último", user_data["business"][-1])

   # Inicializar variáveis
   user_data["economic_sector"] = None
   user_data["region"] = None
   user_data["state"] = None
   user_data["city"] = None
   user_data["neighborhood"] = None

   # Percorrer a lista apenas uma vez
   for item in user_data["business"]:
       if "economic_sector" in item:
           user_data["economic_sector"] = item["economic_sector"]
       if "region" in item:
           user_data["region"] = item["region"]
       if "state" in item:
           user_data["state"] = item["state"]
       if "city" in item:
           user_data["city"] = item["city"]
       if "neighborhood" in item:
           user_data["neighborhood"] = item["neighborhood"]

   print("Último setor econômico:", user_data["economic_sector"])
   print("Região:", user_data["region"])
   print("Estado:", user_data["state"])
   print("Cidade:", user_data["city"])
   print("Bairro:", user_data["neighborhood"])

   with open(f"atlas/database/mpi_Rio_Grande_do_Sul.csv", "r",  newline='', encoding='utf-8') as file:
        mpi_city = csv.DictReader(file)
        mpi_both = None

        print(mpi_city)
        for row in mpi_city:
            print(row["CNAE_section"], user_data["economic_sector"])
            if row["CNAE_section"] == user_data["economic_sector"]:
                mpi_both = row["CNAE_section"]
                print("Achou CNAE", mpi_both)
                break

            return mpi_both





def firstinstruction():
    instruction = (
            '''
            Write in the language choosed by the user, portuguese or english.
            You are very important and decisive in helping us find our user's business sector and its location.
            But now we will first find the user interest sector.
            Remember that they are starting or expanding their business and already have an economic sector or type of business in mind.
            You still don't know what sector is.
            Your main function here is to identify this sector of interest.
            Send a message to initiate the conversation.
            Ask for their economic sector or type of business that have in mind
            Do not write all the sectors in your response.
            Keep in mind that the sectors covered by AtlasGPT are:
            - Agriculture, livestock, forestry production, fishing, and aquaculture
            - Water supply, sewage, waste management, and decontamination activities
            - Accommodation and food services
            - Arts, culture, sports, and recreation
            - Administrative activities and supplementary services
            - Financial activities, insurance, and related services
            - Professional, scientific, and technical activities
            - Commerce; repair of motor vehicles and motorcycles
            - Construction
            - Education
            - Manufacturing industries
            - Information and communication
            - Other service activities
            - Human health and social services
            - Domestic services
            - Transportation, storage, and postal services
            - Extractive industries
            - Real estate activities
            - Electricity and gas
            - Public administration, defense, and social security

            Explain a bit the sector discussed for user.

            After explain the choosed the economic sector, ask for confirmation of their choice using words like confirmation or confirm.
            '''
        )
    return instruction

def sector(user_input, user_token, history, payload, modelurl):
    instruction = (
        '''
        Translate all this:

        You are a backend tool and are no longer conversing with the user.
        You must identify the economic sector of interest in the conversation and write:
        "economic_sector=[insert the economic sector here]".
        Do not respond with anything other than economic_sector.

        Interpret the conversation.
        The sector was probably explicitly mentioned by the "assistant".
        The user may not explicitly state the sector, so deduce the sector based on the user's interest.
        Your role is to find the sector of interest.
        It must be one of these:
        - Agricultura, pecuária, produção florestal, pesca e aquicultura
        - Água, esgoto, atividades de gestão de resíduos e descontaminação
        - Alojamento e alimentação
        - Artes, cultura, esporte e recreação
        - Atividades administrativas e serviços complementares
        - Atividades financeiras, de seguros e serviços relacionados
        - Atividades profissionais, científicas e técnicas
        - Comércio; reparação de veículos automotores e motocicletas
        - Construção
        - Educação
        - Indústrias de transformação
        - Informação e comunicação
        - Outras atividades de serviços
        - Saúde humana e serviços sociais
        - Serviços domésticos
        - Transporte, armazenagem e correio
        - Indústrias extrativas
        - Atividades imobiliárias
        - Eletricidade e gás
        - Administração pública, defesa e seguridade social

        Analyze the messages and discover the sector chosen by the user.
        If you don't have the information, write "None".

        Example:
        economic_sector="Indústrias extrativas"
        '''
        )

    print(instruction)
    user_data = {}
    full_response = extract_variables.api_generate(user_input, user_token, history, payload, modelurl, instruction)
    # print(full_response, "OIOI")
    # user_data["economic_sector"] = str(full_response).split("economic_sector=")[1].replace('"','')
    user_data["economic_sector"] = unicodedata.normalize('NFKD', str(full_response).split("economic_sector=")[1].replace('"','')).encode('ascii', 'ignore').decode('utf-8')
    print(user_data["economic_sector"])

    data = {
        'economic_sector': user_data["economic_sector"],
    }

    print(data)
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

    print("chamar próxima instrução")
    button_instruction = secondinstruction()
    print(button_instruction)
    existing_data["chat_history"].append({"role": "system", "content": button_instruction})

    with open(history_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

    print(f"Data saved to {history_file_path}")

    location(user_input, user_token, history, payload, modelurl)

def secondinstruction():
    instruction = (
            '''
            If the user writes english, so answer english. Se o usuário escrever em português, então repsonda em português.
            Você é muito importate e decisivo para encontrarmos a localização do nosso usuário.
            Lembre-se que ele está iniciando ou expandindo seu negócio, e já tem uma localização em mente.
            Você já tem a informação sobre o setor de interesse.
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

    mpi_both = mpilocationsector(user_token, history, history_file_path)

    print("O MPI para o local e o setor indicados e", mpi_both)
