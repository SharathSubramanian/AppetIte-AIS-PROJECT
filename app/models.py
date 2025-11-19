from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    pantry_items = relationship("PantryItem", back_populates="owner")
    shopping_lists = relationship("ShoppingList", back_populates="owner")


class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=True)
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="unit")

    expiry_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="pantry_items")


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    recipe_name = Column(String, nullable=False)
    # For simplicity store as JSON string (or move to separate table later)
    items_json = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    is_completed = Column(Boolean, default=False)

    owner = relationship("User", back_populates="shopping_lists")