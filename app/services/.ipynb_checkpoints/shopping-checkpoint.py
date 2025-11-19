from typing import List
from sqlalchemy.orm import Session

from .. import models


def compute_shopping_list_items(
    recipe_ingredients: List[str],
    pantry_items: List[models.PantryItem],
) -> List[str]:
    """
    Very simple logic: missing ingredients = recipe - pantry names.
    Later you can use quantities too.
    """
    pantry_names = {item.name.lower() for item in pantry_items}
    missing = [ing for ing in recipe_ingredients if ing.lower() not in pantry_names]
    return missing