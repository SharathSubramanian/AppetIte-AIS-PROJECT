# frontend/utils/api.py
from __future__ import annotations

from typing import Any, Dict, List, Optional
import requests

BASE_URL = "http://127.0.0.1:8000"


def _headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _wrap(resp: requests.Response) -> Dict[str, Any]:
    try:
        data = resp.json()
    except Exception:
        data = None
    return {
        "code": resp.status_code,
        "message": resp.text if resp.status_code >= 400 else "ok",
        "data": data,
    }


# ---------- Auth ----------

def signup(username: str, email: str, password: str) -> Dict[str, Any]:
    r = requests.post(
        f"{BASE_URL}/signup",
        json={"username": username, "email": email, "password": password},
        timeout=30,
    )
    return _wrap(r)


def login(username: str, password: str) -> Dict[str, Any]:
    r = requests.post(
        f"{BASE_URL}/login",
        data={"username": username, "password": password},
        timeout=30,
    )
    return _wrap(r)


# ---------- Pantry ----------

def add_pantry(token: str, item: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.post(
        f"{BASE_URL}/pantry/",
        json=item,
        headers=_headers(token),
        timeout=30,
    )
    return _wrap(r)


def get_pantry(token: str, category: Optional[str] = None) -> Dict[str, Any]:
    params = {"category": category} if category else None
    r = requests.get(
        f"{BASE_URL}/pantry/",
        params=params,
        headers=_headers(token),
        timeout=30,
    )
    return _wrap(r)


def delete_pantry_item(token: str, item_id: int) -> Dict[str, Any]:
    r = requests.delete(
        f"{BASE_URL}/pantry/{item_id}",
        headers=_headers(token),
        timeout=30,
    )
    return _wrap(r)


# ---------- Recommend / Quick ----------

def get_recommendations(token: str, category: Optional[str] = None) -> Dict[str, Any]:
    payload = {"category": category} if category else {}
    r = requests.post(
        f"{BASE_URL}/recommendations",
        json=payload,
        headers=_headers(token),
        timeout=60,
    )
    return _wrap(r)


def quick_generate(token: str, ingredients: List[str]) -> Dict[str, Any]:
    r = requests.post(
        f"{BASE_URL}/quick-generate",
        json={"ingredients": ingredients},
        headers=_headers(token),
        timeout=60,
    )
    return _wrap(r)


def cook_recipe(token: str, recipe_title: str, ingredients: List[str]) -> Dict[str, Any]:
    r = requests.post(
        f"{BASE_URL}/cook",
        json={"recipe_title": recipe_title, "ingredients": ingredients},
        headers=_headers(token),
        timeout=30,
    )
    return _wrap(r)


# ---------- Feedback ----------

def submit_feedback(
    token: str,
    page: str,       # "recommend" | "quickgen"
    rating: int,
    comment: Optional[str] = None,
) -> Dict[str, Any]:
    r = requests.post(
        f"{BASE_URL}/feedback",
        json={"page": page, "rating": rating, "comment": comment},
        headers=_headers(token),
        timeout=30,
    )
    return _wrap(r)