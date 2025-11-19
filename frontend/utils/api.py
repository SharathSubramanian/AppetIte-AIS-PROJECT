import requests

BASE_URL = "http://localhost:8000"

def signup(username, email, password):
    payload = {"username": username, "email": email, "password": password}
    r = requests.post(f"{BASE_URL}/signup", json=payload)
    return r.json(), r.status_code

def login(username, password):
    data = {"username": username, "password": password}
    r = requests.post(f"{BASE_URL}/login", data=data)
    return r.json(), r.status_code

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def add_pantry_item(token, item):
    r = requests.post(f"{BASE_URL}/pantry/", json=item, headers=auth_headers(token))
    return r.json(), r.status_code

def get_pantry(token):
    r = requests.get(f"{BASE_URL}/pantry/", headers=auth_headers(token))
    return r.json(), r.status_code

def get_recommendations(token, category):
    payload = {"category": category}
    r = requests.post(f"{BASE_URL}/recommendations", json=payload, headers=auth_headers(token))
    return r.json(), r.status_code

def quick_generate(token, ingredients):
    payload = {"ingredients": ingredients}
    r = requests.post(f"{BASE_URL}/quick-generate", json=payload, headers=auth_headers(token))
    return r.json(), r.status_code

def create_shopping_list(token, recipe_name, recipe_ingredients):
    payload = {"recipe_name": recipe_name, "recipe_ingredients": recipe_ingredients}
    r = requests.post(f"{BASE_URL}/shopping-list", json=payload, headers=auth_headers(token))
    return r.json(), r.status_code