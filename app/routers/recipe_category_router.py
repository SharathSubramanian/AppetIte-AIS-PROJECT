from fastapi import APIRouter
from pydantic import BaseModel
from app.services.category_service import categorize_recipe

router = APIRouter(prefix="/recipes", tags=["Recipes"])

class CategoryRequest(BaseModel):
    text: str

@router.post("/categorize")
def categorize(req: CategoryRequest):
    tags = categorize_recipe(req.text)
    return {"categories": tags}