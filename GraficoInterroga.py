import json
import networkx as nx
import matplotlib.pyplot as plt
import math # Para a função ceil
import matplotlib as mpl # Importa matplotlib para gerenciar fontes

# ======== Dados (Mantidos) =========
usuario = input("Qual usuario deseja visualizar: ")
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

# 💡 TENTATIVA DE USAR A FONTE "COMIC SANS MS"
# Isso define a fonte padrão para todo o texto no Matplotlib.
try:
    mpl.rcParams['font.family'] = 'Comic Sans MS'
    # Define também o padrão para a fonte sans-serif, que é frequentemente usada.
    mpl.rcParams['font.sans-serif'] = ['Comic Sans MS']
except:
    # Caso a fonte não exista, usa a padrão. Você pode adicionar um print aqui se quiser.
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

y_legend_offset = max([len(te_segue_so), len(mutuais), len(voce_segue_so)]) * y_passo / 2 + 5

plt.text(pos[usuario][0], pos[usuario][1] + 3, 'Usuario', 
         fontsize=16, ha='center', color='black', bbox=dict(facecolor='gold', alpha=0.6, edgecolor='none'))

plt.text(-30 + (x_coluna_dist * (pilhas_por_grupo-1))/2, y_legend_offset, 'Te Segue (Não sigo)', 
         fontsize=14, ha='center', color='black', bbox=dict(facecolor='lightcoral', alpha=0.6, edgecolor='none'))

plt.text(-15 + (x_coluna_dist * (pilhas_por_grupo-1))/2, y_legend_offset, 'Mútuos (Seguimos/Somos Seguidos)', 
         fontsize=14, ha='center', color='black', bbox=dict(facecolor='limegreen', alpha=0.6, edgecolor='none'))

plt.text(15 + (x_coluna_dist * (pilhas_por_grupo-1))/2, y_legend_offset, 'Você Segue (Não te Seguem)', 
         fontsize=14, ha='center', color='black', bbox=dict(facecolor='skyblue', alpha=0.6, edgecolor='none'))


plt.title("🌐 Relações de Seguidores Organizadas em Múltiplas Pilhas para Melhor Visualização", fontsize=18)
plt.axis('off') 
plt.show()