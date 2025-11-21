from datetime import timedelta
import json
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, Base
from .auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
)
from .deps import get_db_dep, get_current_user_dep
from .services import pantry as pantry_service
from .services import recipes as recipes_service
from .services import shopping as shopping_service

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AppetIte Backend",
    description="Backend API for AppetIte project",
    version="0.2.0",
)


# ---------- Auth / Users ----------

@app.post("/signup", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db_dep)):
    existing = db.query(models.User).filter(models.User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken.")

    user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_dep),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    access_token_expires = timedelta(minutes=60 * 24)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(get_current_user_dep)):
    return current_user


# ---------- Pantry ----------

@app.post("/pantry/", response_model=schemas.PantryItemRead, status_code=201)
def add_pantry_item(
    item_in: schemas.PantryItemCreate,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    item = pantry_service.create_pantry_item(db, current_user.id, item_in)
    return item


@app.get("/pantry/", response_model=List[schemas.PantryItemRead])
def list_pantry(
    category: Optional[str] = None,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    items = pantry_service.list_pantry_items(db, current_user.id, category)
    return items


# ---------- Recommendations ----------

@app.post("/recommendations", response_model=List[schemas.Recipe])
def get_recommendations(
    req: schemas.RecommendationRequest,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    pantry_items = pantry_service.list_pantry_items(db, current_user.id)
    ingredients = [item.name for item in pantry_items]

    recipes = recipes_service.recommend_recipes_from_inventory(
        ingredients=ingredients,
        category=req.category,
        max_recipes=5,
    )
    return recipes


# ---------- Quick Generate (not using pantry) ----------

@app.post("/quick-generate", response_model=schemas.QuickGenerateResponse)
def quick_generate(
    req: schemas.QuickGenerateRequest,
    current_user: models.User = Depends(get_current_user_dep),
):
    recipe = recipes_service.quick_generate_recipe(req.ingredients)
    return schemas.QuickGenerateResponse(recipe=recipe)


# ---------- Shopping List ----------

@app.post("/shopping-list", response_model=schemas.ShoppingListRead)
def create_shopping_list(
    req: schemas.ShoppingListCreate,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    pantry_items = pantry_service.list_pantry_items(db, current_user.id)
    missing = shopping_service.compute_shopping_list_items(
        recipe_ingredients=req.recipe_ingredients,
        pantry_items=pantry_items,
    )

    items_json = json.dumps(missing)
    sl = models.ShoppingList(
        user_id=current_user.id,
        recipe_name=req.recipe_name,
        items_json=items_json,
    )
    db.add(sl)
    db.commit()
    db.refresh(sl)

    return schemas.ShoppingListRead(
        id=sl.id,
        recipe_name=sl.recipe_name,
        items=missing,
        created_at=sl.created_at,
        is_completed=sl.is_completed,
    )


# ---------- Cook (consume pantry ingredients) ----------

@app.post("/cook", response_model=schemas.CookResponse)
def cook_recipe(
    req: schemas.CookRequest,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    removed = pantry_service.consume_ingredients(db, current_user.id, req.ingredients)
    removed_items = [schemas.PantryItemRead.model_validate(item) for item in removed]

    msg = f"Cooked '{req.recipe_title}'. Removed {len(removed_items)} pantry items."
    return schemas.CookResponse(message=msg, removed_items=removed_items)


# ---------- Health ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}