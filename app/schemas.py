# app/schemas.py
from __future__ import annotations

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
    unit: Optional[str] = None
    expiry_date: Optional[date] = None


class PantryItemCreate(PantryItemBase):
    pass


class PantryItemRead(PantryItemBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Recipes ----------

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


# ---------- Shopping ----------

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


# ---------- Feedback ----------

class FeedbackCreate(BaseModel):
    # IMPORTANT: frontend sends `page`
    # Allowed values: "recommend" or "quickgen"
    page: str
    rating: int  # 1–5
    comment: Optional[str] = None


class FeedbackRead(FeedbackCreate):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)