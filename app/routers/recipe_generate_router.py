from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.recipe_generator import generate_recipe
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.services.history_service import save_history
from app.models import User
from app.deps import get_current_user

router = APIRouter(prefix="/recipes", tags=["Recipes"])

class GenerateRequest(BaseModel):
    ingredients: str

@router.post("/generate")
def generate(req: GenerateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    recipe = generate_recipe(req.ingredients)

    save_history(db, user.id, req.ingredients, recipe)

    return {"recipe": recipe}