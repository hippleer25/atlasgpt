import json
import csv
import time

def get_profile(user_token):
    print("PERSONAS_get_profile")
    print(f"./chat_history/user_{user_token}.json")
    with open(f"./chat_history/user_{user_token}.json", "r") as file:
        data = json.load(file)

    user_data = {}
    location_data = data.get('location', [])
    if len(location_data) > 0:
        location_info = location_data[0]
        user_data["region"] = location_info.get('region')
        user_data["state"] = location_info.get('state')
        user_data["city"] = location_info.get('city')
        user_data["neighborhood"] = location_info.get('neighborhood')
        user_data["location_info"] = location_data[-1]
        user_data["rent"] = location_info.get('rent')
        user_data["public_politics"] = location_info.get('public_politics')
    else:
        user_data["region"], user_data["state"], user_data["city"], user_data["neighborhood"], user_data["rent"], user_data["public_politics"] = None, None, None, None, None, None

    profile_data = data.get('profile', [])
    if len(profile_data) > 0:
        profile_info = profile_data[0]
        user_data["name"] = profile_info.get('name')
        user_data["email"] = profile_info.get('email')
        user_data["gender"] = profile_info.get('gender')
        user_data["birth_year"] = profile_info.get('birth_year')
        user_data["education"] = profile_info.get('education')
        user_data["professional_experience"] = profile_info.get('professional_experience')
        user_data["business_experience"] = profile_info.get('business_experience')
        user_data["risk_tolerance"] = profile_info.get('risk_tolerance')
        user_data["self_confidence"] = profile_info.get('self_confidence')
    else:
        user_data["name"], user_data["email"], user_data["gender"], user_data["birth_year"], user_data["education"], user_data["professional_experience"], user_data["business_experience"], user_data["risk_tolerance"], user_data["self_confidence"] = None, None, None, None, None, None, None, None, None

    return (user_data)



def search(user_token):
    print("PERSONAS_search")
    weighting = get_weighting()
    print("travou?")
    user_data = get_profile(user_token)

    print("Location Info:")
    print(f"Region: {user_data['region']}")
    print(f"State: {user_data['state']}")
    print(f"City: {user_data['city']}")
    print(f"Neighborhood: {user_data['neighborhood']}")
    print(f"Rent: {user_data['rent']}")
    print(f"Public Politics: {user_data['public_politics']}")

    print("\nProfile Info:")
    print(f"Name: {user_data['name']}")
    print(f"Email: {user_data['email']}")
    print(f"Gender: {user_data['gender']}")
    print(f"Born Date: {user_data['birth_year']}")
    print(f"Education: {user_data['education']}")
    print(f"Professional Experience: {user_data['professional_experience']}")
    print(f"Business Experience: {user_data['business_experience']}")
    print(f"Risk Tolerance: {user_data['risk_tolerance']}")
    print(f"Self-confidence: {user_data['self_confidence']}")


    print(user_data)
    time.sleep(15)

   # novas informações
    user_data["name"] = "Seu Nome"  # Substitua pelo nome que você deseja verificar

    user_data["gender"] = "Masculinio"
    user_data["birth_year"] = "1988"
    user_data["born_brazil"] = "Sim"
    user_data["living_state"] = "RJ"
    user_data["living_city"] = "Rio de Janeiro"
    user_data["education"] = "Contabilidade"
    user_data["years_experience"] = "12"
    user_data["economic_sector"] = "Financeiro"
    user_data["professional_experience"] = "Contador"
    user_data["objectives"] = "Abrir uma empresa de gerenciamento de projetos"
    user_data["business_experience"] = "Não"
    user_data["investment_capacity"] = "Média"
    user_data["risk_tolerance"] = "Média"
    user_data["self_confidence"] = "Alta"
    user_data["competitors"] = "Empresas existentes"
    user_data["geographic_level"] = "Local"
    user_data["public_politics"] = "Apoio a pequenos negócios"
    user_data["business_type"] = "Empresa de serviços"
    user_data["estimated_costs"] = "180000"
    user_data["business_size"] = "Pequeno"

    with open("atlas/files/personas.csv", mode="r", newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        print("Cabeçalhos:", headers)

        best_convergence = 0
        best_name = ""
        for row in reader:
            print("printando....")
            convergence=0
            try:
                if row["Sexo"] == user_data["gender"]:
                    print(row["Sexo"])  # Sexo
                    convergence+=int(weighting["gender"])
                try:

                    if row["Ano de Nascimento"] == user_data["birth_year"]:
                        convergence+=int(weighting["birth_year"])
                    else:
                        print("IDADE")
                        birth_year_ratio = min(int(row["Ano de Nascimento"]), int(user_data["birth_year"])) / max(int(row["Ano de Nascimento"]), int(user_data["birth_year"]))
                        print(round((birth_year_ratio**4**3)*4,2))
                        convergence+=round((birth_year_ratio**4**3)*4,2)
                        print("AQUI 2")
                except ValueError:
                    pass
                print("AQUI 3")
                print(row["Nacionalidade"])
                print("AQUI 3.12")
                if row["Nacionalidade"] == user_data["born_brazil"]:
                    print(row["Nacionalidade"])  # Nacionalidade
                    print("AQUI 1")
                    convergence+=int(weighting["born_brazil"])
                    print("OI??")
                print("AQUI 4")
                if row["Estado Natal"] == user_data["living_state"]:
                    print(row["Estado Natal"])  # Estado em que mora
                    convergence+=int(weighting["living_state"])
                if row["Cidade Natal"] == user_data["living_city"]:
                    print(row["Cidade Natal"])  # Cidade em que mora
                    convergence+=int(weighting["living_city"])
                if row["Formação"] == user_data["education"]:
                    print(row["Formação"])  # Formação técnica ou acadêmica
                    convergence+=int(weighting["education"])
                try:

                    if row["Anos de Experiência"] == user_data["years_experience"]:
                        convergence+=int(weighting["years_experience"])
                    else:
                        print("ANOS DE EXPERIÊNCIA")
                        years_experience_ratio = min(int(row["Anos de Experiência"]), int(user_data["years_experience"])) / max(int(row["Anos de Experiência"]), int(user_data["years_experience"]))
                        print(years_experience_ratio)
                        print(years_experience_ratio*4)
                        convergence+=round(years_experience_ratio*4, 2)

                except ValueError:
                    pass

                if row["Setor Econômico"] == user_data["economic_sector"]:
                    print(row["Setor Econômico"])  # Setor Econômico
                    convergence+=int(weighting["economic_sector"])
                if row["Experiência Profissional"] == user_data["professional_experience"]:
                    print(row["Experiência Profissional"])  # Experiência profissional
                    convergence+=int(weighting["professional_experience"])
                if row["Objetivos"] == user_data["objectives"]:
                    print(row["Objetivos"])  # Objetivos
                    convergence+=int(weighting["objectives"])
                if row["Experiência em abertura de negócios"] == user_data["business_experience"]:
                    print(row["Experiência em abertura de negócios"])  # Experiência em abertura de negócios
                    convergence+=int(weighting["business_experience"])
                if row["Capacidade de investimento"] == user_data["investment_capacity"]:
                    print(row["Capacidade de investimento"])  # Capacidade de investimento
                    convergence+=int(weighting["investment_capacity"])
                if row["Tolerância ao risco"] == user_data["risk_tolerance"]:
                    print(row["Tolerância ao risco"])  # Tolerância ao risco
                    convergence+=int(weighting["risk_tolerance"])
                if row["Autoconfiança"] == user_data["self_confidence"]:
                    print(row["Autoconfiança"])  # Autoconfiança
                    convergence+=int(weighting["self_confidence"])
                if row["Concorrentes"] == user_data["competitors"]:
                    print(row["Concorrentes"])  # Concorrentes
                    convergence+=int(weighting["competitors"])
                if row["Nível geográfico"] == user_data["geographic_level"]:
                    print(row["Nível geográfico"])  # Nível geográfico
                    convergence+=int(weighting["geographic_level"])
                if row["Políticas públicas"] == user_data["public_politics"]:
                    print(row["Políticas públicas"])  # Políticas públicas
                    convergence+=int(weighting["public_politics"])
                if row["Tipo de negócio"] == user_data["business_type"]:
                    print(row["Tipo de negócio"])  # Tipo de negócio
                    convergence+=int(weighting["business_type"])
                try:

                    if row["Custos estimados"] == user_data["estimated_costs"]:
                        convergence+=int(weighting["estimated_costs"])
                    else:
                        print("CUSTOS ESTIMADOS")
                        estimated_costs_ratio = min(int(row["Custos estimados"]), int(user_data["estimated_costs"])) / max(int(row["Custos estimados"]), int(user_data["estimated_costs"]))
                        print(estimated_costs_ratio)
                        print(estimated_costs_ratio*4)
                        convergence+=round(estimated_costs_ratio*4, 2)

                except ValueError:
                    pass
                print("AQUI 2")
                if row["Tamanho do negócio"] == user_data["business_size"]:
                    print(row["Tamanho do negócio"])  # Tamanho do negócio
                    convergence+=int(weighting["business_size"])
                print(f"Convergência de {row['Identificação']} é de {convergence}")
                if round(convergence,2)>best_convergence:
                    best_convergence=round(convergence,2)
                    best_name=row["Identificação"]

            except IndexError as e:
                pass
                print(f"Erro ao acessar índice: {e}")
        print("terminando")
        print(f"Melhor pessoa foi {best_name}, com uma convergência de {best_convergence}")

def get_weighting():
    weighting = {}

    with open("./atlas/src/variables_weighting.conf") as weighting_file:
        for line in weighting_file:
            line = line.strip()
            print(line)

            if "=" in line:
                weighting[line.split('=')[0]] = int(line.split('=')[1])

            print(weighting[line.split('=')[0]])

    return weighting
