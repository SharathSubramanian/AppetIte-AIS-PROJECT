from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- User ----------

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Pantry ----------

class PantryItemBase(BaseModel):
    name: str
    category: Optional[str] = None
    quantity: float
    unit: str
    expiry_date: Optional[date] = None


class PantryItemCreate(PantryItemBase):
    pass


class PantryItemRead(PantryItemBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Recipes / Recommendations ----------

class Recipe(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    category: Optional[str] = None


class RecommendationRequest(BaseModel):
    category: Optional[str] = None  # 'healthy', 'cheat_meal', 'easy_to_cook', etc.


class QuickGenerateRequest(BaseModel):
    ingredients: List[str]


class QuickGenerateResponse(BaseModel):
    recipe: Recipe


# ---------- Shopping list ----------

class ShoppingListCreate(BaseModel):
    recipe_name: str
    recipe_ingredients: List[str]


class ShoppingListRead(BaseModel):
    id: int
    recipe_name: str
    items: List[str]
    created_at: datetime
    is_completed: bool

    model_config = ConfigDict(from_attributes=False)


# ---------- Cook ----------

class CookRequest(BaseModel):
    recipe_title: str
    ingredients: List[str]


class CookResponse(BaseModel):
    message: str
    removed_items: List[PantryItemRead]