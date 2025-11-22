# app/services/pantry.py

from typing import List, Optional
from sqlalchemy.orm import Session

from .. import models, schemas


# -------------------------
# CREATE PANTRY ITEM
# -------------------------
def create_pantry_item(db: Session, user_id: int, item_in: schemas.PantryItemCreate):
    item = models.PantryItem(
        user_id=user_id,
        name=item_in.name.strip(),
        quantity=item_in.quantity,
        category=item_in.category,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# -------------------------
# LIST PANTRY ITEMS  ✅ Missing function
# -------------------------
def list_pantry_items(
    db: Session,
    user_id: int,
    category: Optional[str] = None,
) -> List[models.PantryItem]:

    query = db.query(models.PantryItem).filter(models.PantryItem.user_id == user_id)

    if category:
        query = query.filter(models.PantryItem.category == category)

    return query.order_by(models.PantryItem.id.desc()).all()


# -------------------------
# DELETE PANTRY ITEM
# -------------------------
def delete_pantry_item(db: Session, user_id: int, item_id: int):
    item = (
        db.query(models.PantryItem)
        .filter(models.PantryItem.id == item_id, models.PantryItem.user_id == user_id)
        .first()
    )

    if not item:
        return False

    db.delete(item)
    db.commit()
    return True


# -------------------------
# CONSUME INGREDIENTS (COOK)
# -------------------------
def consume_ingredients(
    db: Session,
    user_id: int,
    ingredients: List[str]
) -> List[models.PantryItem]:

    removed_items = []

    ingredients = [i.lower().strip() for i in ingredients]

    pantry_items = list_pantry_items(db, user_id)

    for used in ingredients:
        for item in pantry_items:
            if item.name.lower() == used:
                removed_items.append(item)
                db.delete(item)
                break

    db.commit()

    return removed_items