# frontend/utils/api.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

BASE_URL = "http://127.0.0.1:8000"


def _headers(token: Optional[str] = None) -> Dict[str, str]:
    h = {
        "accept": "application/json",
    }
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _request(
    method: str,
    path: str,
    token: Optional[str] = None,
    json: Any = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"

    try:
        resp = requests.request(
            method,
            url,
            headers=_headers(token),
            json=json,
            params=params,
            timeout=30,
        )
    except Exception as e:
        return {
            "code": 0,
            "message": str(e),
            "data": None,
        }

    try:
        data = resp.json()
    except Exception:
        data = None

    # Extract a human-readable message
    msg: str = resp.reason
    if isinstance(data, dict):
        if "detail" in data and isinstance(data["detail"], str):
            msg = data["detail"]
        elif "message" in data and isinstance(data["message"], str):
            msg = data["message"]

    return {
        "code": resp.status_code,
        "message": msg,
        "data": data,
    }


# ---------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------


def signup(username: str, email: str, password: str) -> Dict[str, Any]:
    payload = {
        "username": username,
        "email": email,
        "password": password,
    }
    return _request("POST", "/signup", json=payload)


def login(username: str, password: str) -> Dict[str, Any]:
    # FastAPI OAuth2PasswordRequestForm expects form data, not JSON
    url = f"{BASE_URL}/login"
    try:
        resp = requests.post(
            url,
            data={"username": username, "password": password},
            headers={"accept": "application/json"},
            timeout=30,
        )
    except Exception as e:
        return {
            "code": 0,
            "message": str(e),
            "data": None,
        }

    try:
        data = resp.json()
    except Exception:
        data = None

    msg: str = resp.reason
    if isinstance(data, dict) and "detail" in data and isinstance(data["detail"], str):
        msg = data["detail"]

    return {
        "code": resp.status_code,
        "message": msg,
        "data": data,
    }


# ---------------------------------------------------------------------
# Pantry
# ---------------------------------------------------------------------


def get_pantry(token: str, category: Optional[str] = None) -> Dict[str, Any]:
    params = {}
    if category:
        params["category"] = category
    return _request("GET", "/pantry/", token=token, params=params)


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


# ---------------------------------------------------------------------
# Recommendations / Quick generate
# ---------------------------------------------------------------------


def get_recommendations(token: str, category: Optional[str] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if category:
        payload["category"] = category
    return _request("POST", "/recommendations", token=token, json=payload)


def quick_generate(token: str, ingredients: List[str]) -> Dict[str, Any]:
    """
    Call /quick-generate with a list of ingredient strings.
    Backend expects: {"ingredients": ["chicken", "butter", ...]}
    """
    payload = {"ingredients": ingredients}
    return _request("POST", "/quick-generate", token=token, json=payload)


# ---------------------------------------------------------------------
# Shopping list
# ---------------------------------------------------------------------


def create_shopping_list(
    token: str,
    recipe_name: str,
    recipe_ingredients: List[str],
) -> Dict[str, Any]:
    payload = {
        "recipe_name": recipe_name,
        "recipe_ingredients": recipe_ingredients,
    }
    return _request("POST", "/shopping-list", token=token, json=payload)


def get_shopping_lists(token: str) -> Dict[str, Any]:
    return _request("GET", "/shopping-list", token=token)