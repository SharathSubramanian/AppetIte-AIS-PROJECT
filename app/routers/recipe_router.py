from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.db.database import get_db

from app.models import RecipeGenerateRequest, RecipeResponse
from app.services.recipe_service import generate_recipe_from_ingredients
from app.services.category_service import tag_categories
from app.services.recommender_service import recommend_recipes as recommend_engine

router = APIRouter(prefix="/recipes", tags=["recipes"])


def ensure_list(ingredients):
    """If ingredients is a string → convert to list[str]."""
    if isinstance(ingredients, str):
        return [ingredients]
    return ingredients


# -----------------------------------------------------------
# 1) GENERATE RECIPE
# -----------------------------------------------------------
@router.post("/generate", response_model=RecipeResponse)
def generate_recipe(
    payload: RecipeGenerateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    # recipe_service already returns:
    #   title: str
    #   instructions: List[str]
    title, instructions_list = generate_recipe_from_ingredients(payload.ingredients)

    # Ensure correct input format for classifier
    ing_list = ensure_list(payload.ingredients)
    categories = tag_categories(ing_list)

    return RecipeResponse(
        title=title,
        instructions=instructions_list,   # Already a list
        categories=categories,
    )


# -----------------------------------------------------------
# 2) GET CATEGORIES
# -----------------------------------------------------------
@router.post("/categories", response_model=List[str])
def get_categories(
    payload: RecipeGenerateRequest,
    user=Depends(get_current_user),
):
    ing_list = ensure_list(payload.ingredients)
    categories = tag_categories(ing_list)
    return categories


# -----------------------------------------------------------
# 3) RECOMMEND
# -----------------------------------------------------------
@router.post("/recommend", response_model=List[RecipeResponse])
def recommend(
    payload: RecipeGenerateRequest,
    user=Depends(get_current_user),
):

    ing_list = ensure_list(payload.ingredients)

    recs = recommend_engine(payload.ingredients, top_k=5)

    # If NO recommendations — fallback to model generation
    if not recs:
        title, instructions = generate_recipe_from_ingredients(payload.ingredients)
        cats = tag_categories(ing_list)
        return [
            RecipeResponse(
                title=title,
                instructions=instructions,
                categories=cats,
            )
        ]

    # Build responses
    out = []
    for r in recs:
        cats = r["categories"]
        if isinstance(cats, str):
            cats = [cats]

        out.append(
            RecipeResponse(
                title=r["title"],
                instructions=[],      # recommender only returns metadata (not a recipe)
                categories=cats
            )
        )
    return out