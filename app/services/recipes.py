from __future__ import annotations

from typing import List, Optional
import random

from .. import schemas
from ..ml.inference import generate_recipe as ml_generate_recipe



# ------------------------------------------------------------------------------
# Title templates
# ------------------------------------------------------------------------------
_BASE_TITLES = [
    "Cozy {main} Bowl",
    "Quick {main} Skillet",
    "Weeknight {main} Stir-Fry",
    "Simple {main} Medley",
    "One-Pan {main} Delight",
]

_CATEGORY_LABELS = {
    "healthy": "Healthy",
    "cheat meal": "Cheat Meal",
    "easy to cook": "Easy to Cook",
    "comfort food": "Comfort Food",
    "high protein": "High Protein",
}


def _build_title(ingredients: List[str]) -> str:
    if not ingredients:
        return "Pantry Surprise"

    main = ", ".join(ingredients[:2]).title()
    pattern = random.choice(_BASE_TITLES)
    return pattern.format(main=main)
# app/services/recipes.py

from sqlalchemy.orm import Session
from .. import models, schemas
from typing import List

def cook_recipe(db: Session, user_id: int, ingredients: List[str]):
    """
    Removes ingredients from pantry if names match.
    """
    for ing in ingredients:
        item = (
            db.query(models.PantryItem)
            .filter(models.PantryItem.user_id == user_id,
                    models.PantryItem.name.ilike(f"%{ing}%"))
            .first()
        )
        if item:
            db.delete(item)

    db.commit()
    return True

# ------------------------------------------------------------------------------
# QUICK GENERATE
# ------------------------------------------------------------------------------
def quick_generate_recipe(ingredients: List[str]) -> schemas.Recipe:
    """
    Generate a recipe using ML if available.
    Always return a FULL recipe dict so frontend can display it cleanly.
    """

    try:
        result = ml_generate_recipe(ingredients, category=None, mode="quick")

        # result MUST be a dictionary. If not, fallback.
        if isinstance(result, dict):
            try:
                return schemas.Recipe(**result)
            except Exception:
                pass  # fallback below
    except Exception as e:
        print("⚠️ ML quick generator failed, falling back:", e)

    # ---------------------------
    # Fallback recipe
    # ---------------------------
    title = _build_title(ingredients)
    instructions = (
        f"1. Combine {', '.join(ingredients)} in a pan.\n"
        "2. Add seasoning and cook on medium heat.\n"
        "3. Stir occasionally until everything blends well.\n"
        "4. Serve warm!"
    )

    return schemas.Recipe(
        title=title,
        ingredients=ingredients,
        instructions=instructions,
        category="Quick & Easy",
    )


# ------------------------------------------------------------------------------
# INVENTORY RECOMMENDATIONS
# ------------------------------------------------------------------------------
def recommend_recipes_from_inventory(
    ingredients: List[str],
    category: Optional[str] = None,
    max_recipes: int = 5,
) -> List[schemas.Recipe]:

    ingredients = [ing.strip() for ing in ingredients if ing.strip()]

    if not ingredients:
        return []

    # Normalize category
    final_category = None
    if category:
        ck = category.lower().strip()
        final_category = _CATEGORY_LABELS.get(ck, category.title())

    seen_titles = set()
    recipes: List[schemas.Recipe] = []

    # Use ML for FIRST recipe only (best UX)
    try:
        ml_result = ml_generate_recipe(
            ingredients=ingredients,
            category=category,
            mode="inventory"
        )
        if isinstance(ml_result, dict):
            recipe = schemas.Recipe(**ml_result)
            recipes.append(recipe)
            seen_titles.add(recipe.title)
    except:
        pass

    # Fill the rest with fallback (but NO duplication)
    while len(recipes) < max_recipes:
        title = _build_title(ingredients)

        if title in seen_titles:
            continue

        seen_titles.add(title)

        instructions = (
            f"Use your pantry items ({', '.join(ingredients)}) to create this dish.\n"
            "1. Prep ingredients.\n"
            "2. Sauté aromatics.\n"
            "3. Add remaining ingredients and cook.\n"
            "4. Enjoy your meal!"
        )

        recipes.append(
            schemas.Recipe(
                title=title,
                ingredients=ingredients,
                instructions=instructions,
                category=final_category,
            )
        )

    return recipes