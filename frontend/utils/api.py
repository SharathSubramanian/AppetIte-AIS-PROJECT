# frontend/utils/api.py

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import requests

BASE_URL = "http://127.0.0.1:8000"


def _handle_request(func, *args, **kwargs) -> Tuple[Any, int]:
    try:
        r = func(*args, **kwargs)
        try:
            data = r.json()
        except Exception:
            data = r.text
        return data, r.status_code
    except Exception as e:  # pragma: no cover - defensive
        return {"detail": f"Request error: {e}"}, 0


# ------------------------------------------------------------------------------
# Auth
# ------------------------------------------------------------------------------

def signup(username: str, email: str, password: str) -> Tuple[Any, int]:
    payload = {"username": username, "email": email, "password": password}
    return _handle_request(
        requests.post,
        f"{BASE_URL}/signup",
        json=payload,
        timeout=15,
    )


def login(username: str, password: str) -> Tuple[Any, int]:
    # Backend expects OAuth2 form data
    payload = {"username": username, "password": password}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return _handle_request(
        requests.post,
        f"{BASE_URL}/login",
        data=payload,
        headers=headers,
        timeout=15,
    )


# ------------------------------------------------------------------------------
# Pantry / Expiry
# ------------------------------------------------------------------------------

def get_pantry(token: str, category: Optional[str] = None) -> Tuple[Any, int]:
    headers = {"Authorization": f"Bearer {token}"}
    params: Dict[str, Any] = {}
    if category:
        params["category"] = category
    return _handle_request(
        requests.get,
        f"{BASE_URL}/pantry",
        headers=headers,
        params=params,
        timeout=15,
    )


def add_pantry_item(
    token: str,
    name: str,
    category: str,
    quantity: float,
    unit: str,
    expiry_date: Optional[str],
) -> Tuple[Any, int]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload: Dict[str, Any] = {
        "name": name,
        "category": category,
        "quantity": quantity,
        "unit": unit,
    }
    if expiry_date:
        payload["expiry_date"] = expiry_date
    return _handle_request(
        requests.post,
        f"{BASE_URL}/pantry",
        headers=headers,
        json=payload,
        timeout=15,
    )


def get_expiring_items(token: str, days: int = 7) -> Tuple[Any, int]:
    headers = {"Authorization": f"Bearer {token}"}
    params = {"days": days}
    return _handle_request(
        requests.get,
        f"{BASE_URL}/expiry",
        headers=headers,
        params=params,
        timeout=15,
    )


# ------------------------------------------------------------------------------
# Recipes & Quick Generate
# ------------------------------------------------------------------------------

def get_recommendations(
    token: str,
    category: Optional[str] = None,
) -> Tuple[Any, int]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload: Dict[str, Any] = {"category": category}
    return _handle_request(
        requests.post,
        f"{BASE_URL}/recommendations",
        headers=headers,
        json=payload,
        timeout=30,
    )


def quick_generate(
    token: str,
    ingredients: List[str],
) -> Tuple[Any, int]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"ingredients": ingredients}
    return _handle_request(
        requests.post,
        f"{BASE_URL}/quick-generate",
        headers=headers,
        json=payload,
        timeout=30,
    )


# ------------------------------------------------------------------------------
# Shopping List & Cooking
# ------------------------------------------------------------------------------

def create_shopping_list(
    token: str,
    recipe_name: str,
    recipe_ingredients: List[str],
) -> Tuple[Any, int]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "recipe_name": recipe_name,
        "recipe_ingredients": recipe_ingredients,
    }
    return _handle_request(
        requests.post,
        f"{BASE_URL}/shopping-list",
        headers=headers,
        json=payload,
        timeout=30,
    )


def cook_recipe(
    token: str,
    recipe_name: str,
    recipe_ingredients: List[str],
) -> Tuple[Any, int]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "recipe_name": recipe_name,
        "recipe_ingredients": recipe_ingredients,
    }
    return _handle_request(
        requests.post,
        f"{BASE_URL}/cook",
        headers=headers,
        json=payload,
        timeout=30,
    )