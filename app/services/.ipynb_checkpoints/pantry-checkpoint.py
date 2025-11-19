from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from .. import models, schemas


def create_pantry_item(
    db: Session, user_id: int, item_in: schemas.PantryItemCreate
) -> models.PantryItem:
    db_item = models.PantryItem(
        user_id=user_id,
        name=item_in.name,
        category=item_in.category,
        quantity=item_in.quantity,
        unit=item_in.unit,
        expiry_date=item_in.expiry_date,
        created_at=datetime.utcnow(),
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def list_pantry_items(
    db: Session, user_id: int, category: Optional[str] = None
) -> List[models.PantryItem]:
    query = db.query(models.PantryItem).filter(models.PantryItem.user_id == user_id)
    if category:
        query = query.filter(models.PantryItem.category == category)
    return query.order_by(models.PantryItem.created_at.desc()).all()