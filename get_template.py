import requests
import json

# --- CONFIGURAÇÕES ---
URL = 'http://localhost:3000'
USER = 'joao.balbuena0@gmai.com'
PASS = 'joao12345'
ID_DASHBOARD = 4 

# 1. Login
try:
    session_res = requests.post(f"{URL}/api/session", json={"username": USER, "password": PASS})
    session = session_res.json()['id']
    headers = {"X-Metabase-Session": session}
    print("Logado com sucesso!")
except:
    print("Erro ao fazer login. Verifique e-mail e senha.")
    exit()

def extrair():
    print(f"Extraindo tudo do Dashboard {ID_DASHBOARD}...")
    
    # Puxa o dashboard inteiro
    response = requests.get(f"{URL}/api/dashboard/{ID_DASHBOARD}", headers=headers)
    
    if response.status_code == 200:
        dash_data = response.json()
        
        # Salva o arquivo JSON com tudo dentro
        with open('projeto_template.json', 'w', encoding='utf-8') as f:
            json.dump(dash_data, f, indent=4, ensure_ascii=False)
        
        print("--------------------------------------------------")
        print("Mapeamento concluído com SUCESSO!")
        print(f"Arquivo 'projeto_template.json' gerado.")
        print(f"Abas encontradas: {len(dash_data.get('tabs', []))}")
        print("--------------------------------------------------")
    else:
        print(f"Erro ao acessar dashboard: Status {response.status_code}")
        print("Verifique se o ID 4 está correto e se o Metabase está ligado.")

if __name__ == "__main__":
    extrair()