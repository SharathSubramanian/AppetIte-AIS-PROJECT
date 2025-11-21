from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models, schemas


def create_pantry_item(
    db: Session,
    user_id: int,
    item_in: schemas.PantryItemCreate,
) -> models.PantryItem:
    item = models.PantryItem(
        user_id=user_id,
        name=item_in.name.strip(),
        category=item_in.category,
        quantity=item_in.quantity,
        unit=item_in.unit,
        expiry_date=item_in.expiry_date,
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
    q = db.query(models.PantryItem).filter(models.PantryItem.user_id == user_id)
    if category:
        q = q.filter(models.PantryItem.category == category)
    return q.order_by(models.PantryItem.created_at.desc()).all()


def consume_ingredients(
    db: Session,
    user_id: int,
    ingredients: List[str],
) -> List[models.PantryItem]:
    """
    Very simple "cook" logic:
    - Normalize ingredient names to lowercase
    - Remove pantry items where `name` is in the ingredient list.
    """
    normalized = {ing.strip().lower() for ing in ingredients if ing.strip()}
    if not normalized:
        return []

    items = (
        db.query(models.PantryItem)
        .filter(models.PantryItem.user_id == user_id)
        .all()
    )

    removed: List[models.PantryItem] = []
    for item in items:
        if item.name.lower() in normalized:
            removed.append(item)
            db.delete(item)

    db.commit()
    return removed