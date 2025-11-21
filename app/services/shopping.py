from typing import List, Dict

from sqlalchemy.orm import Session

from .. import models


def compute_shopping_list_items(
    recipe_ingredients: List[str],
    pantry_items: List[models.PantryItem],
) -> List[str]:
    """
    Compare recipe ingredients with pantry item names.
    Returns a list of missing ingredients (case-insensitive exact match).
    """
    recipe_norm = {ing.strip().lower() for ing in recipe_ingredients if ing.strip()}
    pantry_norm = {item.name.strip().lower() for item in pantry_items}

    missing = sorted(list(recipe_norm - pantry_norm))
    return missing