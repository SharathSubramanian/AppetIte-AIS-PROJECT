# app/schemas.py
from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator


# ---------- User ----------

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Pantry ----------

class PantryItemBase(BaseModel):
    name: str
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    expiry_date: Optional[date] = None


class PantryItemCreate(PantryItemBase):
    pass


class PantryItemRead(PantryItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Recipes / Generation ----------



class Recipe(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    category: Optional[str] = None


class RecommendationRequest(BaseModel):
    category: Optional[str] = None


class QuickGenerateRequest(BaseModel):
    ingredients: List[str]


class QuickGenerateResponse(BaseModel):
    recipe: Recipe


# ---------- Shopping list ----------

class ShoppingListCreate(BaseModel):
    recipe_name: str
    recipe_ingredients: List[str]
# app/schemas.py

class CookRequest(BaseModel):
    ingredients: List[str]


class ShoppingListRead(BaseModel):
    id: int
    recipe_name: str
    items: List[str]
    created_at: datetime
    is_completed: bool

    class Config:
        from_attributes = True
# app/schemas.py 

from typing import List
from pydantic import BaseModel


class CookRequest(BaseModel):
    recipe_name: str
    recipe_ingredients: List[str]