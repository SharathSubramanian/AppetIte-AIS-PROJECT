# app/services/shopping.py

from typing import List
from ..models import PantryItem


def _norm(s: str) -> str:
    return s.strip().lower()


def compute_shopping_list_items(
    recipe_ingredients: List[str],
    pantry_items: List[PantryItem],
) -> List[str]:
    """
    Given a list of ingredient names for a recipe and the user's pantry items,
    return a list of ingredient names that are NOT available in the pantry.
    Partial matches are allowed (e.g., 'tomato' matches 'tomato sauce').
    """

    available_names = [_norm(p.name) for p in pantry_items]
    missing: List[str] = []

    for raw_ing in recipe_ingredients:
        ing = _norm(raw_ing)
        if not ing:
            continue

        # Check if any pantry name is close enough
        present = any(ing in p or p in ing for p in available_names)
        if not present and raw_ing not in missing:
            missing.append(raw_ing)

    return missing