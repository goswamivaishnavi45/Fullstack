# ===== app/main.py =====
# Step 1 · app + /health  ·  Step 2 · lifespan creates tables
# Step 3 · include_router  ·  Step 4 · custom exception handler
# Step 6 · auth + users routers, 409 handler
# What: entry point. Run with: uvicorn app.main:app --reload
# Concepts: FastAPI vs Uvicorn, lifespan, routers, exception handlers.
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import models  # noqa: F401  (loads the model classes so their tables are known)
from app.core.config import get_settings
from app.core.exceptions import ConflictError, NotFoundError
from app.db.session import Base, engine
from app.routers import auth, initiatives, users

settings = get_settings()


# Lifespan: code before `yield` runs once at startup.
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # create tables if they don't exist
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(auth.router)         # /auth/signup, /auth/login, /auth/me
app.include_router(users.router)        # /users (admin only)
app.include_router(initiatives.router)  # /initiatives ...


# Custom exception handlers: our domain errors -> HTTP responses, in one place.
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": f"{exc.resource} {exc.id} not found"})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": exc.message})


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
