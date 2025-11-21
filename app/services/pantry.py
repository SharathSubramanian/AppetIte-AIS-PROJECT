# app/services/pantry.py
# app/services/pantry.py

from typing import List

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
def delete_pantry_item(db: Session, user_id: int, item_id: int) -> None:
    """
    Delete a single pantry item that belongs to this user.
    """
    item = (
        db.query(models.PantryItem)
        .filter(
            models.PantryItem.id == item_id,
            models.PantryItem.user_id == user_id,
        )
        .first()
    )
    if not item:
        return  # nothing to delete, silently ignore

    db.delete(item)
    db.commit()


def consume_ingredients(
    db: Session,
    user_id: int,
    ingredients: List[str],
) -> None:
    """
    Very simple 'consume' logic:

    For each ingredient name, find pantry items with a matching name
    (case-insensitive) for this user and delete them.

    You could make this more sophisticated later (e.g., decrement quantity).
    """
    if not ingredients:
        return

    norm_ings = [ing.strip().lower() for ing in ingredients if ing.strip()]
    if not norm_ings:
        return

    q = (
        db.query(models.PantryItem)
        .filter(models.PantryItem.user_id == user_id)
    )

    items = q.all()
    to_delete = []

    for item in items:
        if not item.name:
            continue
        if item.name.strip().lower() in norm_ings:
            to_delete.append(item)

    if not to_delete:
        return

    for item in to_delete:
        db.delete(item)

    db.commit()