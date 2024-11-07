import json

def firstinstruction():
    instruction = (
            '''
            Você é muito importate e decisivo para encontrarmos a localização do nosso usuário.
            Lembre-se que ele está iniciando ou expandindo seu negócio, e já tem uma localização em mente.
            Sua função principal aqui é encontrar esta localização.
            A localização é em território brasileiro.
            Pergunte onde ficará o negócio que o usuário pretende abrir.
            Comece perguntando do maior para o menor, onde o seu negócio ficará localizado.
            1 - Qual a região (IBGE) de abertura/expansão do negócio?
            2 - Qual o estado?
            3 - Qual o município?
            4 - Qual o bairro?
            Faça as perguntas nessa ordem. Altere as palavras da pergunta, mas mantenha seu sentido estrito.
            Somente quando não houverem mais perguntas a serem feitas, confirme a localização escrevendo por extenso.
            A frase de confirmação deve ser em uma nova linha.

            Siga estritamente os modelos
            Quando souber tudo:
            "Você confirma a localização: região [insira aqui a região], o estado [insira aqui o estado], a cidade de [inira aqui a cidade] e o bairro [insira aqui o bairro]?"
            Exemplo:
            "Você confirma a localização: região Sul, o estado Rio Grande do Sul, a cidade de Porto Alegre e o bairro Santana?"

            Quando não souber o bairro:
            "Você confirma a localização: região [insira aqui a região], o estado [insira aqui o estado] e a cidade de [inira aqui a cidade]?"
            Exemplo:
            "Você confirma a localização: região Sul, o estado Rio Grande do Sul e a cidade de Porto Alegre?"

            Quando não souber nem o bairro nem a cidade:
            "Você confirma a localização: região [insira aqui a região] e o estado [insira aqui o estado]?"
            Exemplo:
            "Você confirma a localização: região Sul e o estado Rio Grande do Sul?"


            Quando só souber a região:
            "Você confirma a localização: região [insira aqui a região]?"
            Exemplo:
            "Você confirma a localização: região Sul?"

            Caso o usuário fale em inglês, troque "Você confirma a localização" por "Do you confirm the location"
            Exemplo:
            "Do you confirm the location: region Sul, state of Rio Grande do Sul, city of Porto Alegre and the neighborhood Santana?"

            '''
        )
    return instruction

def locationconfirm(complete_data, user_token):
    print("VERIFICANDO")


    if "\n" not in complete_data.split("Você confirma a localização: ")[1].split("?")[0]:
        verification_phrase = complete_data.split("Você confirma a localização: ")[1].split("?")[0]
    print(verification_phrase)

    if "bairro" in verification_phrase:
        print("BAIRRO")
        neighborhood = verification_phrase.split("bairro ")[1]
        city = verification_phrase.split(" e o bairro")[0].split("cidade de ")[1]
        state = verification_phrase.split(", a cidade de")[0].split("estado ")[1]
        region = verification_phrase.split(", o estado")[0].split("região ")[1]
        print(region)

    elif "cidade" in verification_phrase:
        print("CIDADE")
        neighborhood = None
        city = verification_phrase.split("cidade de ")[1]
        state = verification_phrase.split(" e a cidade de")[0].split("estado ")[1]
        region = verification_phrase.split(", o estado")[0].split("região ")[1]

    elif "estado" in verification_phrase:
        print("ESTADO")
        neighborhood = None
        city = None
        state = verification_phrase.split("estado ")[1]
        region = verification_phrase.split(" e o estado")[0].split("região ")[1]
    elif "region" in verification_phrase:
        print("REGIÃO")
        neighborhood = None
        city = None
        state = None
        region = verification_phrase.split("região ")[1]

    print(f"Região: {region}")
    print(f"Estado: {state}")
    print(f"Cidade: {city}")
    print(f"Bairro: {neighborhood}")

    data = {
        'region': region,
        'state': state,
        'city': city,
        'neighborhood': neighborhood
    }

    history_file_path = f"chat_history/user_{user_token}.json"

    try:
        print("TENTANDO SALVAR")
        with open(history_file_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
            print("Arquivo encontrado e dados carregados.")
    except FileNotFoundError:
        existing_data = {"chat_history": [], "location": []}
        print("Arquivo não encontrado. Criando novo arquivo.")

    existing_data['location'].append(data)

    with open(history_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

    print(f"Data saved to {history_file_path}")



def secondinstruction():
    print("SEGUNDAS INSTRUÇÕES")
    instruction = (
            '''
            Localização confirmada!!
            Não precisa mais confirmar a localização.
            Agora que já sabemos a localização do negócio, precisamos fazer novas perguntas.
            "Qual deve ser o custo mensal do aluguel em reais (R$)?"
            "Há políticas púbicas que favoreçam ou desfavoreçam seu empreendimento?"
            Faça as perguntas com palavras diferentes, mas com o mesmo significado.
            As perguntas devem ser feitas em mensagens separadas.
            Faça essas perguntas em sequência.

            Quando o usuário afirmar que há políticas públicas, pergunte "Quais são estas políticas e/ou quais são as finalidades destas?"
            Lembre-se de mudar as palaras utilizadas na pergunta.

            Quando as duas questões forem respondidas, peça uma confirmação do valor do aluguel e das políticas púbilcas.
            Faça essa confirmação apenas se as duas perguntas estiverem respondidas.
            Antes de confirmar, você precisa ter perguntado sobre as políticas públicas.
            Não utilize negrito para formatar a pergunta.
            Não utilize capslock para formatar as informações.

            Assim:
            "Você confirma o valor do aluguel de R$[insira aqui o valor do aluguel] mensais, e que [há/não há] políticas públicas para a região?"

            Caso a conversa seja em inglês:
            "Do you confirm the rent amount of R$[insert here the rent price] per month, and whether [there is/there isn't] public policies for the area?"
            '''
        )
    return instruction

def priceconfirm(complete_data, user_token):
    print("VERIFICANDO")

    print(complete_data)
    print(complete_data.split("Você confirma o valor do aluguel de ")[1].split("?")[0])
    if "políticas" in complete_data.split("Você confirma o valor do aluguel de ")[1].split("?")[0]:
        verification_phrase = complete_data.split("Você confirma o valor do aluguel de ")[1].split("?")[0]
        print("DENTRO DO IF")
    print(verification_phrase)

    rent = verification_phrase.split('R$')[1].split(' mensais')[0].split(' ')[0].replace(' ','')
    public_politics = verification_phrase.split('e que ')[1].split(' políticas públicas')[0]
    print("polí")
    if "n" in public_politics or "N" in public_politics:
        public_politics = False
    else:
        public_politics = True
    print("ticas")
    print(f"Aluguel: {rent}")
    print(f"Políticas públicas: {public_politics}")

    data = {
        'rent': rent,
        'public_politics': public_politics
    }

    history_file_path = f"chat_history/user_{user_token}.json"

    try:
        print("TENTANDO SALVAR")
        with open(history_file_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
            print("Arquivo encontrado e dados carregados.")
    except FileNotFoundError:
        existing_data = {"chat_history": [], "location": [], "pofile": []}
        print("Arquivo não encontrado. Criando novo arquivo.")

    existing_data['location'].append(data)

    with open(history_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

    print(f"Data saved to {history_file_path}")

# SALVANDO AS INFORMAÇÕES DO CADASTRO
    data = {
        'name': 'Antônio',
        'email': 'antonio@gmail.com',
        'gender': 'male',
        'born_date': '19780714',
        'education': 'Economia',
        'professional_experience': 'Contador',
        'business_experience': 'none',
        'risk_tolerance': 'medium',
        'self_confidence': 'high'

    }

    history_file_path = f"chat_history/user_{user_token}.json"

    try:
        print("TENTANDO SALVAR")
        with open(history_file_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
            print("Arquivo encontrado e dados carregados.")
    except FileNotFoundError:
        existing_data = {"chat_history": [], "location": [], "pofile": []}
        print("Arquivo não encontrado. Criando novo arquivo.")

    existing_data['profile'].append(data)

    with open(history_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

    print(f"Data saved to {history_file_path}")

# CONTINUAR DAQUI: NÃO SE ESTÁ SALVANDO O VALOR DAS VARIAǗEIS NEM O CAHT HISTORY
