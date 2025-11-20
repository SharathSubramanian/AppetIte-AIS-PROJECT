from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .auth import get_current_user
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user_dep(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    # CRITICAL: use keyword args to avoid positional mixup
    return get_current_user(token=token, db=db)