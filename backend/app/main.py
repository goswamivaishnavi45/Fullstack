# ===== app/main.py =====
# Step 1 · app + /health  ·  Step 2 · lifespan creates tables
# Step 3 · include_router  ·  Step 4 · custom exception handler
# Step 6 · auth + users routers, 409 handler  ·  Step 7 · logging, middleware, CORS
# What: entry point. Run with: uvicorn app.main:app --reload
# Concepts: FastAPI vs Uvicorn, lifespan, routers, exception handlers, middleware, CORS.
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import models  # noqa: F401  (loads the model classes so their tables are known)
from app.core.config import get_settings
from app.core.exceptions import ConflictError, NotFoundError
from app.db.session import Base, engine
from app.routers import auth, initiatives, users

settings = get_settings()

# ---------- Step 7: logging ----------
# Every log line: time, level, logger name, message.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("app")


# Lifespan: code before `yield` runs once at startup.
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # create tables if they don't exist
    logger.info("App started")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(auth.router)         # /auth/signup, /auth/login, /auth/me
app.include_router(users.router)        # /users (admin only)
app.include_router(initiatives.router)  # /initiatives ...


# ---------- Step 7: middleware (runs for EVERY request) ----------
@app.middleware("http")
async def timing_and_request_id(request: Request, call_next):
    # use the client's X-Request-ID if it sent one, otherwise make a new unique id
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()

    response = await call_next(request)  # <- the route (and everything inside) runs here

    ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{ms:.1f}ms"
    logger.info("%s %s -> %s in %.1fms [id=%s]",
                request.method, request.url.path, response.status_code, ms, request_id)
    return response


# ---------- Step 7: CORS ----------
# Let the React dev server (another origin: port 5173) read our responses in the browser.
# Added last = outermost middleware, so it handles the browser's OPTIONS "preflight" first.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # exact origin; no "*" when credentials are allowed
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PATCH, DELETE ...
    allow_headers=["*"],   # Authorization, Content-Type ...
)


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
