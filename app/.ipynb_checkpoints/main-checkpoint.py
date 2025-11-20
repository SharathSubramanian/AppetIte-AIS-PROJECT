from datetime import timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas
from .auth import authenticate_user, create_access_token, get_password_hash
from .deps import get_current_user_dep

# Services
from .services import pantry as pantry_service
from .services import recipes as recipes_service
from .services import shopping as shopping_service

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AppetIte Backend", version="1.0")


# -------------------- AUTH --------------------
@app.post("/signup", response_model=schemas.UserRead)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(hours=24)

    token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserRead)
def me(user: models.User = Depends(get_current_user_dep)):
    return user


# -------------------- PANTRY --------------------
@app.get("/pantry", response_model=List[schemas.PantryItemRead])
def list_pantry(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user_dep),
):
    return pantry_service.list_pantry_items(db, user.id, category)


@app.post("/pantry", response_model=schemas.PantryItemRead)
def add_pantry_item(
    item: schemas.PantryItemCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user_dep),
):
    return pantry_service.create_pantry_item(db, user.id, item)


# -------------------- RECOMMENDATIONS --------------------
@app.post("/recommendations", response_model=List[schemas.Recipe])
def recommend(
    req: schemas.RecommendationRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user_dep),
):
    pantry_items = pantry_service.list_pantry_items(db, user.id, req.category)
    ingredients = [p.name for p in pantry_items]

    return recipes_service.recommend_recipes_from_inventory(ingredients, req.category)


# -------------------- QUICK GENERATE --------------------
@app.post("/quick-generate", response_model=schemas.QuickGenerateResponse)
def quick_generate(
    req: schemas.QuickGenerateRequest,
    user: models.User = Depends(get_current_user_dep)
):
    recipe = recipes_service.quick_generate_recipe(req.ingredients)
    return schemas.QuickGenerateResponse(recipe=recipe)


# -------------------- SHOPPING LIST --------------------
@app.post("/shopping-list", response_model=schemas.ShoppingListRead)
def create_shopping_list(
    req: schemas.ShoppingListCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user_dep),
):
    pantry_items = pantry_service.list_pantry_items(db, user.id)
    missing = shopping_service.compute_shopping_list_items(req.recipe_ingredients, pantry_items)

    sl = models.ShoppingList(
        user_id=user.id,
        recipe_name=req.recipe_name,
        items_json=missing,
    )

    db.add(sl)
    db.commit()
    db.refresh(sl)

    return sl


# -------------------- COOK (DELETE INGREDIENTS USED) --------------------
@app.post("/cook", status_code=200)
def cook_recipe(
    req: schemas.CookRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user_dep),
):
    pantry_service.consume_ingredients(db, user.id, req.ingredients)
    return {"message": "Recipe cooked! Ingredients removed."}