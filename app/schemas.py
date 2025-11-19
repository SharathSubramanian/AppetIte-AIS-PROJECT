from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, EmailStr



class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True



class PantryItemBase(BaseModel):
    name: str
    category: Optional[str] = None
    quantity: float = 1.0
    unit: str = "unit"
    expiry_date: Optional[date] = None


class PantryItemCreate(PantryItemBase):
    pass


class PantryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    expiry_date: Optional[date] = None


class PantryItemRead(PantryItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Recipes / Recommendations ----------

class RecommendationRequest(BaseModel):
    category: Optional[str] = None  


class Recipe(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    category: Optional[str] = None


class QuickGenerateRequest(BaseModel):
    ingredients: List[str]


class QuickGenerateResponse(BaseModel):
    recipe: Recipe



class ShoppingListCreate(BaseModel):
    recipe_name: str
    recipe_ingredients: List[str]


class ShoppingListRead(BaseModel):
    id: int
    recipe_name: str
    items: List[str]
    created_at: datetime
    is_completed: bool

    class Config:
        from_attributes = True