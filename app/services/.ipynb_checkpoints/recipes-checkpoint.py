# app/services/recipes.py

from __future__ import annotations

from typing import Dict, List, Optional

from ..ml.inference import generate_recipe


def recommend_recipes_from_inventory(
    ingredients: List[str],
    category: Optional[str] = None,
    n_recipes: int = 3,
) -> List[Dict]:
    """
    Recommend 1..n_recipes recipes from pantry inventory.

    We de-duplicate by recipe title so you don't see the same recipe 3 times.
    """
    ingredients = [x.strip() for x in ingredients if x and x.strip()]
    if not ingredients:
        return []

    recipes: List[Dict] = []
    seen_titles = set()
    attempts = 0

    # Try a few times to encourage diversity; stop early if we can't get more unique titles.
    while len(recipes) < n_recipes and attempts < n_recipes * 3:
        raw = generate_recipe(ingredients, category=category, mode="inventory")
        title_key = raw.get("title", "").strip().lower()
        if title_key and title_key not in seen_titles:
            seen_titles.add(title_key)
            recipes.append(raw)

        attempts += 1

    return recipes


def quick_generate_recipe(ingredients: List[str]) -> Dict:
    """
    Generate a single "quick" recipe that ignores pantry inventory.
    """
    ingredients = [x.strip() for x in ingredients if x and x.strip()]
    return generate_recipe(ingredients, category=None, mode="quick")