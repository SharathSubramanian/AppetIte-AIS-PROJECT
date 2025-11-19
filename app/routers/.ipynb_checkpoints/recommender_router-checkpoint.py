from fastapi import APIRouter, Depends
from app.services.recommender_service import recommend_recipes
from app.deps import get_current_user
from app.db.database import get_db
from sqlalchemy.orm import Session

from app.models import User, PantryItem

router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.get("/recommend")
def recommend(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pantry_items = db.query(PantryItem).filter(PantryItem.user_id == user.id).all()
    pantry_list = [item.ingredient for item in pantry_items]

    results = recommend_recipes(pantry_list)
    return {"recommendations": results}