import requests
import json

# --- CONFIGURAÇÕES ---
METABASE_URL = "http://localhost:3000/api"
EMAIL = "joao.balbuena0@gmai.com"
SENHA = "joao12345"
NOME_TABELA_DESTINO = "tabela_geral_consolidada"
# ALTERADO PARA O NOME CORRETO DO SEU ARQUIVO:
ARQUIVO_JSON = "projeto_template.json" 

def implantar():
    # 1. Autenticação
    try:
        session = requests.post(f"{METABASE_URL}/session", json={"username": EMAIL, "password": SENHA}).json()
        headers = {"X-Metabase-Session": session["id"], "Content-Type": "application/json"}
    except:
        print("Erro ao conectar no Metabase. Verifique se ele está ligado.")
        return

    # 2. Carregar o DNA do Painel
    print(f"📂 Lendo arquivo {ARQUIVO_JSON}...")
    with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
        template = json.load(f)

    # 3. Descobrir IDs do novo Banco/Tabela
    dbs = requests.get(f"{METABASE_URL}/database", headers=headers).json()
    dbs_list = dbs['data'] if isinstance(dbs, dict) and 'data' in dbs else dbs
    db_id = dbs_list[0]['id'] 

    meta = requests.get(f"{METABASE_URL}/database/{db_id}/metadata", headers=headers).json()
    tabela_dest = next(t for t in meta['tables'] if t['name'] == NOME_TABELA_DESTINO)
    new_table_id = tabela_dest['id']

    # 4. Criar o Dashboard (Container)
    print(f"🎨 Criando Dashboard: {template.get('name')}...")
    novo_dash = requests.post(f"{METABASE_URL}/dashboard", headers=headers, json={
        "name": template.get('name', 'Painel Importado'),
        "description": template.get('description'),
        "parameters": template.get('parameters', [])
    }).json()
    dash_id = novo_dash['id']

    # 5. Criar as 7 Abas
    mapa_abas = {}
    if template.get('tabs'):
        print(f"📑 Criando {len(template['tabs'])} abas...")
        requests.post(f"{METABASE_URL}/dashboard/{dash_id}/tabs", headers=headers, 
                      json={"tabs": [{"name": t['name']} for t in template['tabs']]})
        
        info = requests.get(f"{METABASE_URL}/dashboard/{dash_id}", headers=headers).json()
        mapa_abas = {old['id']: new['id'] for old, new in zip(template['tabs'], info['tabs'])}

    # 6. Recriar os Cards (Perguntas) e mapear IDs
    print("📦 Recriando cards e ajustando SQL/MBQL...")
    mapa_cards = {}
    dashcards_original = template.get('dashcards') or template.get('ordered_cards', [])
    
    for dc in dashcards_original:
        card_orig = dc.get('card')
        if card_orig and 'dataset_query' in card_orig:
            # Ajusta para o novo banco/tabela
            query = card_orig['dataset_query']
            query['database'] = db_id
            if query.get('type') == 'query' and 'query' in query and 'source-table' in query['query']:
                query['query']['source-table'] = new_table_id

            new_card = requests.post(f"{METABASE_URL}/card", headers=headers, json={
                "name": card_orig['name'],
                "dataset_query": query,
                "display": card_orig['display'],
                "visualization_settings": card_orig['visualization_settings']
            }).json()
            
            if 'id' in new_card:
                mapa_cards[card_orig['id']] = new_card['id']

    # 7. Montagem do Layout (O "Colar Screenshot")
    print("🪄 Montando layout e vinculando filtros...")
    for dc in dashcards_original:
        payload_item = {
            "size_x": dc['size_x'], "size_y": dc['size_y'], "row": dc['row'], "col": dc['col'],
            "visualization_settings": dc['visualization_settings'],
            "parameter_mappings": dc.get('parameter_mappings', []),
            "dashboard_tab_id": mapa_abas.get(dc.get('dashboard_tab_id'))
        }
        
        # Se for gráfico, associa o novo ID do card
        if dc.get('card_id') and dc['card_id'] in mapa_cards:
            payload_item["card_id"] = mapa_cards[dc['card_id']]
        elif dc.get('card') and dc['card'].get('id') in mapa_cards:
             payload_item["card_id"] = mapa_cards[dc['card']['id']]

        requests.post(f"{METABASE_URL}/dashboard/{dash_id}/cards", headers=headers, json=payload_item)

    print(f"\n🚀 SUCESSO! Painel implantado integralmente.")
    print(f"🔗 Link: {METABASE_URL.replace('/api', '')}/dashboard/{dash_id}")

if __name__ == "__main__":
    implantar()