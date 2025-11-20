# app/services/pantry.py
from datetime import date, timedelta
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
        name=item_in.name,
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


def get_expiring_items(
    db: Session,
    user_id: int,
    days: int = 7,
):
    today = date.today()
    cutoff = today + timedelta(days=days)

    return (
        db.query(models.PantryItem)
        .filter(
            models.PantryItem.user_id == user_id,
            models.PantryItem.expiry_date.is_not(None),
            models.PantryItem.expiry_date >= today,
            models.PantryItem.expiry_date <= cutoff,
        )
        .order_by(models.PantryItem.expiry_date.asc())
        .all()
    )