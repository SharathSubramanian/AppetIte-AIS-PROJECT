# app/services/recipes.py
from typing import List, Optional

from .. import schemas
from ..ml.inference import generate_recipe_from_ingredients


def recommend_recipes_from_inventory(
    ingredients: List[str],
    category: Optional[str] = None,
) -> List[schemas.Recipe]:
    """
    Feature 1:
    Recommend recipes based on pantry inventory, with optional category filter.

    For now, we call the same FLAN-based generator once.
    Later, you can extend this to:
    - generate multiple recipes
    - use category-tagging notebook to filter recipes
    """
    if not ingredients:
        # No pantry items – maybe return an empty list or a fallback recipe
        return []

    parsed = generate_recipe_from_ingredients(ingredients, category=category)

    recipe = schemas.Recipe(
        title=str(parsed["title"]),
        ingredients=list(parsed["ingredients"]),
        instructions=str(parsed["instructions"]),
        category=category,
    )

    return [recipe]


def quick_generate_recipe(ingredients: List[str]) -> schemas.Recipe:
    """
    Feature 2:
    Generate a quick recipe based only on user-provided ingredients.
    Does not use inventory / pantry.

    We simply call the FLAN-based generator without category.
    """
    parsed = generate_recipe_from_ingredients(ingredients, category=None)

    return schemas.Recipe(
        title=str(parsed["title"]),
        ingredients=list(parsed["ingredients"]),
        instructions=str(parsed["instructions"]),
        category=None,
    )