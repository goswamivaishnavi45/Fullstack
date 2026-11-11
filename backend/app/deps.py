# ===== app/deps.py =====
# Step 5 · Reusable dependencies (DB, Page)
# Step 6 · Auth dependencies (get_current_user, require_role, get_owned_initiative)
# Concepts: Depends, Annotated, sub-dependencies, 401 vs 403, dependency factory.
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import Initiative, User
from app.services import initiatives as initiative_service

# Instead of writing `db: Session = Depends(get_db)` in every route, write `db: DB`.
DB = Annotated[Session, Depends(get_db)]


# FastAPI reads skip and limit from the query string: /initiatives?skip=0&limit=10
# ge = "greater or equal", le = "less or equal". Bad values -> 422.
def pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),  # max 100 so nobody asks for a million rows
) -> dict:
    return {"skip": skip, "limit": limit}


# Any route can now write `page: Page` to get {"skip": ..., "limit": ...}.
Page = Annotated[dict, Depends(pagination)]


# ---------- Step 6: authentication (401 = who are you?) ----------

# Reads the "Authorization: Bearer <token>" header (401 if missing).
# tokenUrl tells /docs where to log in (adds the green "Authorize" button).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DB) -> User:
    unauthorized = HTTPException(
        status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = decode_access_token(token)  # checks signature + expiry
    except jwt.InvalidTokenError:
        raise unauthorized
    user = db.get(User, int(payload["sub"]))  # sub = user id we put in at login
    if user is None:
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# ---------- Step 6: authorization (403 = you are logged in, but not allowed) ----------

# Dependency FACTORY: require_role("admin") returns a new dependency function.
def require_role(*roles: str):
    def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user

    return checker


# Ownership check: load the initiative (404 if missing), then
# allow only its owner or an admin (403 otherwise).
def get_owned_initiative(initiative_id: int, user: CurrentUser, db: DB) -> Initiative:
    initiative = initiative_service.get_initiative(db, initiative_id)
    if user.role != "admin" and initiative.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You can only change your own initiatives")
    return initiative


OwnedInitiative = Annotated[Initiative, Depends(get_owned_initiative)]
