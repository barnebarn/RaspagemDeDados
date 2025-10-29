import json

def carregar_usuarios(usuario):
    try:
        with open(f'{usuario}_instagram_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("não tem")
        return None

usuario = input("Qual usuario deseja visualizar: ")
dados = carregar_usuarios(usuario)

seguindo = [u["username"] for u in dados["following"]]
seguidores = [u["username"] for u in dados["followers"]]

# junta tudo sem duplicar
todos = set(seguindo + seguidores)

for pessoa in todos:
    print(pessoa, end=" ")

    if pessoa in seguindo and pessoa in seguidores:
        print("<->", end=" ")
    elif pessoa in seguindo and pessoa not in seguidores:
        print("<---", end=" ")
    elif pessoa in seguidores and pessoa not in seguindo:
        print("--->", end=" ")

    print(usuario)
