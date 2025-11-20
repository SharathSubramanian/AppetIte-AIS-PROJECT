# app/services/pantry.py

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models, schemas


def create_pantry_item(
    db: Session,
    user_id: int,
    item_in: schemas.PantryItemCreate,
) -> models.PantryItem:
    """
    Create a pantry item for a specific user.
    """
    item = models.PantryItem(
        user_id=user_id,                     # ✅ IMPORTANT: tie to the current user
        name=item_in.name,
        category=item_in.category,
        quantity=item_in.quantity,
        unit=item_in.unit,
        expiry_date=item_in.expiry_date,     # this is Optional[date]
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_pantry_items(
    db: Session,
    user_id: int,
    category: Optional[str] = None,
) -> List[models.PantryItem]:
    """
    List pantry items for the given user, optionally filtered by category.
    """
    query = db.query(models.PantryItem).filter(models.PantryItem.user_id == user_id)

    if category:
        query = query.filter(models.PantryItem.category == category)

    # Keep a deterministic order
    return query.order_by(models.PantryItem.created_at.asc()).all()