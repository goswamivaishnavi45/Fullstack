# ===== app/routers/initiatives.py =====
# Step 3 · CRUD routes  ·  Step 4 · made thin  ·  Step 5 · pagination + filter
# Step 6 · login required for all routes; edit/delete only by owner or admin
# Step 11 · streaming summary (StreamingResponse + generator)
# Concepts: APIRouter, path/query/body params, response_model, status codes, Depends.
import time

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.deps import DB, CurrentUser, OwnedInitiative, Page, get_current_user
from app.schemas.initiative import (
    InitiativeCreate,
    InitiativeOut,
    InitiativePage,
    InitiativeUpdate,
    MilestoneCreate,
    MilestoneOut,
    Status,
)
from app.services import initiatives as service

# dependencies=[...]: every route here needs a valid token (401 otherwise).
router = APIRouter(
    prefix="/initiatives", tags=["initiatives"], dependencies=[Depends(get_current_user)]
)


@router.post("", response_model=InitiativeOut, status_code=201)
def create_initiative(body: InitiativeCreate, db: DB, user: CurrentUser):
    return service.create_initiative(db, body, owner_id=user.id)  # owner = logged-in user


# GET /initiatives?skip=0&limit=10&status=active  (any logged-in user can read)
@router.get("", response_model=InitiativePage)
def list_initiatives(db: DB, page: Page, status: Status | None = None):
    items, total = service.list_initiatives(db, page["skip"], page["limit"], status)
    return {"items": items, "total": total, **page}


@router.get("/{initiative_id}", response_model=InitiativeOut)
def get_initiative(initiative_id: int, db: DB):
    return service.get_initiative(db, initiative_id)


# OwnedInitiative: 404 if missing, 403 if you're not the owner (or admin).
@router.patch("/{initiative_id}", response_model=InitiativeOut)
def update_initiative(initiative: OwnedInitiative, body: InitiativeUpdate, db: DB):
    return service.update_initiative(db, initiative, body)


@router.delete("/{initiative_id}", status_code=204)
def delete_initiative(initiative: OwnedInitiative, db: DB):
    service.delete_initiative(db, initiative)


@router.post("/{initiative_id}/milestones", response_model=MilestoneOut, status_code=201)
def create_milestone(initiative: OwnedInitiative, body: MilestoneCreate, db: DB):
    return service.create_milestone(db, initiative, body)


@router.get("/{initiative_id}/milestones", response_model=list[MilestoneOut])
def list_milestones(initiative_id: int, db: DB):
    return service.list_milestones(db, initiative_id)


# Step 11 · Send the summary word by word instead of all at once.
@router.get("/{initiative_id}/summary")
def stream_summary(initiative_id: int, db: DB):
    initiative = service.get_initiative(db, initiative_id)  # 404 BEFORE streaming starts
    text = service.build_summary(initiative)  # use the DB now, not inside the generator

    def word_stream():  # a generator: `yield` sends one piece, then continues
        for word in text.split(" "):
            yield word + " "
            time.sleep(0.15)  # pretend the AI is "thinking" between words

    return StreamingResponse(word_stream(), media_type="text/plain")
