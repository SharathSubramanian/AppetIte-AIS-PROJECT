from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import SessionLocal
from .auth import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_db_dep():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_dep(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_dep),
):
    return get_current_user(token, db)