# app/services/pantry.py

from sqlalchemy.orm import Session
from .. import models, schemas

def get_pantry(db: Session, user_id: int):
    return db.query(models.PantryItem).filter(models.PantryItem.user_id == user_id).all()

def add_item(db: Session, user_id: int, item: schemas.PantryItemCreate):
    db_item = models.PantryItem(
        user_id=user_id,
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        expiry=item.expiry
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, user_id: int, item_id: int):
    item = (
        db.query(models.PantryItem)
        .filter(models.PantryItem.id == item_id,
                models.PantryItem.user_id == user_id)
        .first()
    )

    if not item:
        return False

    db.delete(item)
    db.commit()
    return True