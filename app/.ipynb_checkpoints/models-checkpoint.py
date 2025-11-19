from typing import List
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base

class PantryItem(Base):
    __tablename__ = "pantry"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ingredient = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True  # pydantic v2


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RecipeGenerateRequest(BaseModel):
    ingredients: str


class RecipeResponse(BaseModel):
    title: str
    instructions: List[str]
    categories: List[str] = []


class RecommendationResponse(BaseModel):
    recipes: List[RecipeResponse]