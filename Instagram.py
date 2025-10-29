import requests
import json
import time


# Query hashes que o IG usa (podem mudar, mas esses funcionam pra web)
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
username = input("Insira o usuario que deseja pegar os dados olha só:")
followers = get_followers(username, limit_pages=5)  # 5 páginas de cada
following = get_following(username, limit_pages=5)

print("Followers (amostra):", [f["username"] for f in followers[:30]])
print("Following (amostra):", [f["username"] for f in following[:30]])
print("Totais (apontados pelo script):", len(followers), len(following))

data = {
    "username": username,
    "followers": followers,
    "following": following
}

# Salvar num arquivo JSON bonitinho
with open(f"{username}_instagram_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"✅ Dados salvos em {username}_instagram_data.json")