# ===== app/schemas/user.py =====
# Step 6 · User + token schemas
# What: JSON shapes for signup, user output and the login response.
# Concepts: UserCreate has password, UserOut never does (response_model filters it).
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):  # body of POST /auth/signup
    email: EmailStr  # must look like an email, otherwise 422
    password: str = Field(min_length=8)


class UserOut(BaseModel):  # NO password / hashed_password here
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str


class Token(BaseModel):  # response of POST /auth/login
    access_token: str
    token_type: str = "bearer"
