# ===== app/routers/auth.py =====
# Step 6 · Signup, login, "who am I"
# Concepts: OAuth2PasswordRequestForm (form data), JWT access token, 201 / 401 / 409.
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token
from app.deps import DB, CurrentUser
from app.schemas.user import Token, UserCreate, UserOut
from app.services import users as service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut, status_code=201)
def signup(body: UserCreate, db: DB):
    return service.create_user(db, body)  # UserOut hides hashed_password


# Login takes FORM data (username + password), not JSON - that's the OAuth2 standard.
# We use the email as the "username".
@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DB):
    user = service.authenticate(db, form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Wrong email or password", headers={"WWW-Authenticate": "Bearer"}
        )
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):  # needs a valid token
    return user
