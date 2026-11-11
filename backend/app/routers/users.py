# ===== app/routers/users.py =====
# Step 6 · Admin-only route
# Concepts: require_role factory on the whole router -> non-admins get 403.
from fastapi import APIRouter, Depends

from app.deps import DB, require_role
from app.schemas.user import UserOut
from app.services import users as service

# dependencies=[...] on the router: EVERY route below requires role "admin".
router = APIRouter(prefix="/users", tags=["users (admin)"], dependencies=[Depends(require_role("admin"))])


@router.get("", response_model=list[UserOut])
def list_users(db: DB):
    return service.list_users(db)
