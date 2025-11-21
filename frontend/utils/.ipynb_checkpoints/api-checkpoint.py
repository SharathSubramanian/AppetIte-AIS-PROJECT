import os
from typing import List, Optional, Dict, Any

import requests

BASE_URL = os.getenv("APPETITE_API_URL", "http://127.0.0.1:8000")


def _handle_response(resp: requests.Response) -> Dict[str, Any]:
    """
    Wrap all backend responses into a unified structure:
    {
        "code": <status_code>,
        "data": <parsed JSON or None>,
        "message": <OK or error text>
    }
    """
    status = resp.status_code
    try:
        data = resp.json()
    except Exception:
        text = resp.text.strip()
        return {
            "code": status,
            "data": None,
            "message": f"Non-JSON response ({status}): {text[:200]}",
        }

    # Try to extract a meaningful message
    msg = "OK"
    if not (200 <= status < 300):
        if isinstance(data, dict) and "detail" in data:
            msg = str(data["detail"])
        else:
            msg = str(data)

    return {"code": status, "data": data, "message": msg}


# ---------- AUTH ----------


def signup(username: str, email: str, password: str) -> Dict[str, Any]:
    payload = {"username": username, "email": email, "password": password}
    resp = requests.post(f"{BASE_URL}/signup", json=payload)
    return _handle_response(resp)


def login(username: str, password: str) -> Dict[str, Any]:
    # FastAPI OAuth2PasswordRequestForm expects form-encoded data
    payload = {"username": username, "password": password}
    resp = requests.post(
        f"{BASE_URL}/login",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return _handle_response(resp)


# ---------- HELPERS ----------


def _auth_headers(token: Optional[str]) -> Dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


# ---------- PANTRY ----------


def get_pantry(token: str, category: Optional[str] = None) -> Dict[str, Any]:
    params = {}
    if category:
        params["category"] = category
    resp = requests.get(
        f"{BASE_URL}/pantry",
        headers=_auth_headers(token),
        params=params,
    )
    return _handle_response(resp)


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

    resp = requests.post(
        f"{BASE_URL}/pantry",
        headers=_auth_headers(token),
        json=payload,
    )
    return _handle_response(resp)


def delete_pantry_item(token: str, item_id: int) -> Dict[str, Any]:
    resp = requests.delete(
        f"{BASE_URL}/pantry/{item_id}",
        headers=_auth_headers(token),
    )
    return _handle_response(resp)


# ---------- RECOMMENDATIONS & QUICK GENERATE ----------


def get_recommendations(token: str, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Calls POST /recommendations with an optional category.
    Backend returns a list of recipe objects.
    """
    payload: Dict[str, Any] = {}
    if category and category.lower() != "any":
        payload["category"] = category

    resp = requests.post(
        f"{BASE_URL}/recommendations",
        headers=_auth_headers(token),
        json=payload,
    )
    return _handle_response(resp)


def quick_generate(token: str, ingredients: List[str]) -> Dict[str, Any]:
    """
    Calls POST /quick-generate.
    Backend returns: {"recipe": {...}}
    """
    payload = {"ingredients": ingredients}
    resp = requests.post(
        f"{BASE_URL}/quick-generate",
        headers=_auth_headers(token),
        json=payload,
    )
    return _handle_response(resp)


# ---------- SHOPPING LIST ----------


def create_shopping_list(
    token: str,
    recipe_name: str,
    recipe_ingredients: List[str],
) -> Dict[str, Any]:
    """
    Calls POST /shopping-list.
    Backend compares ingredients with pantry and returns missing items.
    """
    payload = {
        "recipe_name": recipe_name,
        "recipe_ingredients": recipe_ingredients,
    }
    resp = requests.post(
        f"{BASE_URL}/shopping-list",
        headers=_auth_headers(token),
        json=payload,
    )
    return _handle_response(resp)