import requests
import json
import time
import networkx as nx
import matplotlib.pyplot as plt
import math # Para a função ceil
import matplotlib as mpl # Importa matplotlib para gerenciar fontes

QUERY_HASH_FOLLOWERS = "c76146de99bb02f6415203be841dd25a"
QUERY_HASH_FOLLOWING = "d04b0a864b4b54837c0d870b0e77e076"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-IG-App-ID": "936619743392459"
}
s = requests.Session()
s.cookies.set("sessionid", "8249190055%3Aboanf0DkbQclgZ%3A0%3AAYhsqPmqNi3iW2LBUcs8EtvpSJFHy_5dSqkf8zq8_w")
s.cookies.set("csrftoken", "Ifz5dShuNXdICLgWVS6LANJotu5FhMcG")

# Usa a sessão 's' nos requests
# exemplo: requests.get(url, headers=HEADERS, cookies=s.cookies)
def get_user_id(username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    res = s.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise RuntimeError(f"Erro ao obter profile info: {res.status_code}")
    data = res.json()
    return data["data"]["user"]["id"]

def fetch_graphql_list(user_id, query_hash, first=50, max_pages=None, sleep_between=1.0):
    results = []
    after = None
    pages = 0

    while True:
        variables = {"id": str(user_id), "include_reel": True, "fetch_mutual": False, "first": first}
        if after:
            variables["after"] = after

        vars_encoded = json.dumps(variables, separators=(",", ":"))
        url = f"https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables={vars_encoded}"
        res = s.get(url, headers=HEADERS)

        if res.status_code != 200:
            raise RuntimeError(f"Erro na GraphQL: {res.status_code}")

        data = res.json()
        edges = data["data"]["user"]["edge_followed_by"]["edges"] if query_hash == QUERY_HASH_FOLLOWERS else data["data"]["user"]["edge_follow"]["edges"]
        page_info = data["data"]["user"]["edge_followed_by"]["page_info"] if query_hash == QUERY_HASH_FOLLOWERS else data["data"]["user"]["edge_follow"]["page_info"]

        for e in edges:
            node = e.get("node")
            results.append({
                "username": node.get("username"),
                "full_name": node.get("full_name"),
                "pk": node.get("id"),
                "is_private": node.get("is_private", False)
            })

        pages += 1
        if max_pages and pages >= max_pages:
            break

        if page_info.get("has_next_page"):
            after = page_info.get("end_cursor")
            time.sleep(sleep_between)
            continue
        else:
            break

    return results

def get_followers(username, limit_pages=None):
    uid = get_user_id(username)
    return fetch_graphql_list(uid, QUERY_HASH_FOLLOWERS, max_pages=limit_pages)

def get_following(username, limit_pages=None):
    uid = get_user_id(username)
    return fetch_graphql_list(uid, QUERY_HASH_FOLLOWING, max_pages=limit_pages)

# 👇 Exemplo de uso
usuario = input("Insira o usuario que deseja pegar os dados olha só:")
followers = get_followers(usuario, limit_pages=5)  # 5 páginas de cada
following = get_following(usuario, limit_pages=5)


data = {
    "username": usuario,
    "followers": followers,
    "following": following
}

# Salvar num arquivo JSON bonitinho
with open(f"{usuario}_instagram_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"✅ Dados salvos em {usuario}_instagram_data.json")

with open(f'{usuario}_instagram_data.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

seguindo = [u["username"] for u in dados["following"]]
seguidores = [u["username"] for u in dados["followers"]]
todos = set(seguindo + seguidores)

# ======== Cria grafo (Mantido) =========
G = nx.DiGraph()
G.add_node(usuario)

for pessoa in todos:
    if pessoa in seguindo and pessoa in seguidores:
        G.add_edge(usuario, pessoa)  # você → pessoa
        G.add_edge(pessoa, usuario)  # pessoa → você
    elif pessoa in seguindo:
        G.add_edge(usuario, pessoa)  # você → pessoa
    elif pessoa in seguidores:
        G.add_edge(pessoa, usuario)  # pessoa → você

# ============ LAYOUT MANUAL (Múltiplas Pilhas/Sub-colunas) ============

# 1. Classifica os nós por categoria
mutuais = [p for p in todos if p in seguindo and p in seguidores]
voce_segue_so = [p for p in todos if p in seguindo and p not in seguidores]
te_segue_so = [p for p in todos if p not in seguindo and p in seguidores]

# 2. Define as coordenadas (X e Y) para cada "pilha"

pos = {usuario: (0, 0)}  # Nó central

# --- Configurações de Espaçamento e Número de Pilhas ---
y_passo = 1.5
x_coluna_dist = 6 
pilhas_por_grupo = 3

def organizar_em_pilhas(lista_pessoas, x_inicio_grupo, y_passo, pilhas_por_grupo):
    qtd_pessoas = len(lista_pessoas)
    posicoes_grupo = {}

    if qtd_pessoas == 0:
        return posicoes_grupo

    pessoas_por_pilha = math.ceil(qtd_pessoas / pilhas_por_grupo) 
    
    for i, pessoa in enumerate(lista_pessoas):
        idx_pilha = i // pessoas_por_pilha 
        idx_na_pilha = i % pessoas_por_pilha 

        x = x_inicio_grupo + (idx_pilha * x_coluna_dist) 
        
        y_total_pilha = min(pessoas_por_pilha, qtd_pessoas - (idx_pilha * pessoas_por_pilha))
        y_start_pilha = y_total_pilha * y_passo / 2
        
        y = y_start_pilha - idx_na_pilha * y_passo
        posicoes_grupo[pessoa] = (x, y)
        
    return posicoes_grupo

# --- Aplica a função de organização para cada grupo ---
pos.update(organizar_em_pilhas(te_segue_so, -30, y_passo, pilhas_por_grupo)) 
pos.update(organizar_em_pilhas(mutuais, -15, y_passo, pilhas_por_grupo)) 
pos.update(organizar_em_pilhas(voce_segue_so, 15, y_passo, pilhas_por_grupo)) 


# ==================== Visual ====================
plt.figure(figsize=(25, 18)) 

# TENTATIVA DE USAR A FONTE "COMIC SANS MS"
try:
    mpl.rcParams['font.family'] = 'Comic Sans MS'
    mpl.rcParams['font.sans-serif'] = ['Comic Sans MS']
except:
    print("A fonte 'Comic Sans MS' não foi encontrada. Usando fonte padrão.")
    mpl.rcParams['font.family'] = 'sans-serif'


# Define cores (Mantido)
cores = []
for node in G.nodes():
    if node == usuario:
        cores.append("gold")
    elif node in seguindo and node in seguidores:
        cores.append("limegreen")
    elif node in seguindo:
        cores.append("skyblue")
    else:
        cores.append("lightcoral")

# Desenha
nx.draw(
    G,
    pos, 
    with_labels=True,
    node_color=cores,
    node_size=1000, 
    font_size=8,   
    arrows=True,
    arrowsize=10,  
    font_weight="bold",
    edge_color='gray',
    alpha=0.8 
)

# Adiciona legendas para as colunas
def get_top_y(grupo, pos):
    if not grupo: return 0
    top_node_pos = pos.get(grupo[0])
    return top_node_pos[1] if top_node_pos else 0

y_legend_offset = max([len(te_segue_so), len(mutuais), len(voce_segue_so)]) * y_passo / 5 + 5

# 💡 CORREÇÃO AQUI: Usa a variável 'usuario' para mostrar o nome real.
plt.text(pos[usuario][0], pos[usuario][1] + 3, usuario, 
         fontsize=16, ha='center', color='black', bbox=dict(facecolor='gold', alpha=0.6, edgecolor='none'))

# 1. Te Segue
plt.text(-30 + (x_coluna_dist * (pilhas_por_grupo-1))/2, y_legend_offset, 'Te Segue', 
         fontsize=14, ha='center', color='black', bbox=dict(facecolor='lightcoral', alpha=0.6, edgecolor='none'))

# 2. Mutual
plt.text(-15 + (x_coluna_dist * (pilhas_por_grupo-1))/2, y_legend_offset, 'Mutual', 
         fontsize=14, ha='center', color='black', bbox=dict(facecolor='limegreen', alpha=0.6, edgecolor='none'))

# 3. Seguindo (Você Segue)
plt.text(15 + (x_coluna_dist * (pilhas_por_grupo-1))/2, y_legend_offset, 'Seguindo', 
         fontsize=14, ha='center', color='black', bbox=dict(facecolor='skyblue', alpha=0.6, edgecolor='none'))


plt.title("🌐 Relações de Seguidores Organizadas em Múltiplas Pilhas para Melhor Visualização", fontsize=18)
plt.axis('off') 
plt.show()