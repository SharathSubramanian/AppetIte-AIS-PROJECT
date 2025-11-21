# frontend/utils/api.py

from __future__ import annotations

import requests
from typing import Any, Dict, List, Optional

BASE_URL = "http://127.0.0.1:8000"


def _request(
    method: str,
    path: str,
    token: Optional[str] = None,
    json: Any = None,
) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"
    headers: Dict[str, str] = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        r = requests.request(method, url, headers=headers, json=json)
    except Exception as e:
        return {
            "code": 0,
            "data": None,
            "message": f"Request failed: {e}",
        }

    try:
        data = r.json()
    except Exception:
        data = None

    if r.status_code >= 400:
        # Extract detail if FastAPI error
        msg = "Request failed"
        if isinstance(data, dict) and "detail" in data:
            msg = str(data["detail"])
        else:
            msg = f"HTTP {r.status_code}"
        return {
            "code": r.status_code,
            "data": data,
            "message": msg,
        }

    return {
        "code": r.status_code,
        "data": data,
        "message": "ok",
    }


# ------------------------ Auth ------------------------


def signup(username: str, email: str, password: str) -> Dict[str, Any]:
    payload = {
        "username": username,
        "email": email,
        "password": password,
    }
    return _request("POST", "/signup", json=payload)


def login(username: str, password: str) -> dict:
    url = f"{BASE_URL}/login"
    data = {
        "username": username,
        "password": password,
    }
    resp = requests.post(url, data=data)

    if resp.status_code != 200:
        return {"status": "error", "message": resp.text}

    j = resp.json()

    if "access_token" not in j:
        return {"status": "error", "message": "Invalid login response"}

    return {
        "status": "ok",
        "token": j["access_token"]
    }


# ---------------------- Pantry ------------------------


def get_pantry(token: str) -> Dict[str, Any]:
    return _request("GET", "/pantry/", token=token)


def add_pantry(
    token: str,
    name: str,
    category: str,
    quantity: float,
    unit: str,
    expiry_date: Optional[str] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "name": name,
        "category": category,
        "quantity": quantity,
        "unit": unit,
    }
    if expiry_date:
        payload["expiry_date"] = expiry_date

    return _request("POST", "/pantry/", token=token, json=payload)


def delete_pantry_item(token: str, item_id: int) -> Dict[str, Any]:
    return _request("DELETE", f"/pantry/{item_id}", token=token)


# -------------------- Recommendations -----------------


def get_recommendations(
    token: str,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "category": category,
    }
    return _request("POST", "/recommendations", token=token, json=payload)


def cook_recipe(token: str, recipe_title: str, ingredients: List[str]) -> Dict[str, Any]:
    payload = {
        "recipe_title": recipe_title,
        "ingredients": ingredients,
    }
    return _request("POST", "/cook", token=token, json=payload)


# --------------------- Quick Generate -----------------


def quick_generate(token: str, ingredients: List[str]) -> Dict[str, Any]:
    payload = {
        "ingredients": ingredients,
    }
    return _request("POST", "/quick-generate", token=token, json=payload)


# --------------------- Shopping list ------------------


def create_shopping_list(
    token: str,
    recipe_name: str,
    ingredients: List[str],
) -> Dict[str, Any]:
    payload = {
        "recipe_name": recipe_name,
        "recipe_ingredients": ingredients,
    }
    return _request("POST", "/shopping-list", token=token, json=payload)