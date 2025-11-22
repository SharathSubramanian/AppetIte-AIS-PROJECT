# frontend/utils/api.py

"""
Central API client for the AppetIte frontend.

All functions return a dict with the SAME shape:

{
    "code": <int HTTP status>,
    "data": <parsed JSON or None>,
    "message": <string, "ok" or error detail>
}

The Streamlit pages (app.py + pages/*) should ONLY depend on this shape.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

BASE_URL = "http://127.0.0.1:8000"


def _wrap_response(resp: requests.Response) -> Dict[str, Any]:
    """Convert a `requests.Response` into a uniform dict."""
    try:
        data = resp.json()
    except Exception:
        data = None

    # Default message
    msg: str

    if 200 <= resp.status_code < 300:
        # Success
        if isinstance(data, dict) and "detail" in data:
            msg = str(data["detail"])
        else:
            msg = "ok"
    else:
        # Error
        if isinstance(data, dict) and "detail" in data:
            msg = str(data["detail"])
        else:
            msg = resp.text or "request failed"

    return {
        "code": resp.status_code,
        "data": data,
        "message": msg,
    }


# ---------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------


def signup(username: str, email: str, password: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/signup"
    payload = {
        "username": username,
        "email": email,
        "password": password,
    }
    resp = requests.post(url, json=payload)
    return _wrap_response(resp)


def login(username: str, password: str) -> Dict[str, Any]:
    """
    FastAPI /login is using OAuth2PasswordRequestForm,
    so we must send x-www-form-urlencoded.
    """
    url = f"{BASE_URL}/login"
    data = {"username": username, "password": password}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(url, data=data, headers=headers)
    return _wrap_response(resp)


# ---------------------------------------------------------------------
# Pantry CRUD
# ---------------------------------------------------------------------


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def get_pantry(token: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/pantry/"
    resp = requests.get(url, headers=_auth_headers(token))
    return _wrap_response(resp)


def add_pantry(
    token: str,
    name: str,
    category: Optional[str],
    quantity: float,
    unit: str,
    expiry_date: Optional[str],
) -> Dict[str, Any]:
    url = f"{BASE_URL}/pantry/"
    payload = {
        "name": name,
        "category": category or "",
        "quantity": quantity,
        "unit": unit,
        "expiry_date": expiry_date,  # can be None or ISO string
    }
    resp = requests.post(url, json=payload, headers=_auth_headers(token))
    return _wrap_response(resp)


def delete_pantry_item(token: str, item_id: int) -> Dict[str, Any]:
    url = f"{BASE_URL}/pantry/{item_id}"
    resp = requests.delete(url, headers=_auth_headers(token))
    return _wrap_response(resp)


# ---------------------------------------------------------------------
# Recommendations & cooking
# ---------------------------------------------------------------------


def get_recommendations(
    token: str,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    url = f"{BASE_URL}/recommendations"
    payload: Dict[str, Any] = {"category": category}
    resp = requests.post(url, json=payload, headers=_auth_headers(token))
    return _wrap_response(resp)


def cook_recipe(
    token: str,
    recipe_title: str,
    ingredients: List[str],
) -> Dict[str, Any]:
    """
    Hit the /cook endpoint to consume ingredients from the pantry.
    """
    url = f"{BASE_URL}/cook"
    payload = {
        "recipe_title": recipe_title,
        "ingredients": ingredients,
    }
    resp = requests.post(url, json=payload, headers=_auth_headers(token))
    return _wrap_response(resp)


# ---------------------------------------------------------------------
# Quick generate (ignores pantry)
# ---------------------------------------------------------------------


def quick_generate(token: str, ingredients: List[str]) -> Dict[str, Any]:
    url = f"{BASE_URL}/quick-generate"
    payload = {"ingredients": ingredients}
    resp = requests.post(url, json=payload, headers=_auth_headers(token))
    return _wrap_response(resp)


# ---------------------------------------------------------------------
# Shopping list
# ---------------------------------------------------------------------


def create_shopping_list(
    token: str,
    recipe_name: str,
    recipe_ingredients: List[str],
) -> Dict[str, Any]:
    url = f"{BASE_URL}/shopping-list"
    payload = {
        "recipe_name": recipe_name,
        "recipe_ingredients": recipe_ingredients,
    }
    resp = requests.post(url, json=payload, headers=_auth_headers(token))
    return _wrap_response(resp)