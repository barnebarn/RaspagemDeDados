import json
import networkx as nx
import matplotlib.pyplot as plt

# ======== Dados =========
usuario = input("Qual usuario deseja visualizar: ")

with open(f'{usuario}_instagram_data.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

seguindo = [u["username"] for u in dados["following"]]
seguidores = [u["username"] for u in dados["followers"]]
todos = set(seguindo + seguidores)

# ======== Cria grafo =========
G = nx.DiGraph()

# Adiciona o nó central (você)
G.add_node(usuario)

for pessoa in todos:
    if pessoa in seguindo and pessoa in seguidores:
        G.add_edge(usuario, pessoa)   # você → pessoa
        G.add_edge(pessoa, usuario)   # pessoa → você
    elif pessoa in seguindo:
        G.add_edge(usuario, pessoa)   # você → pessoa
    elif pessoa in seguidores:
        G.add_edge(pessoa, usuario)   # pessoa → você

# ======== Visual =========
plt.figure(figsize=(9, 7))
pos = nx.spring_layout(G, seed=42)

# Define cores
cores = []
for node in G.nodes():
    if node == usuario:
        cores.append("gold")
    elif node in seguindo and node in seguidores:
        cores.append("limegreen")   # mutual
    elif node in seguindo:
        cores.append("skyblue")     # você segue
    else:
        cores.append("lightcoral")  # te segue

# Desenha
nx.draw(
    G, pos,
    with_labels=True,
    node_color=cores,
    node_size=2000,
    font_size=10,
    arrows=True,
    arrowsize=15,
    font_weight="bold"
)

plt.title("🌐 Relações de Seguidores e Seguidos", fontsize=14)
plt.show()
