# ===== app/services/initiatives.py =====
# Step 4 · Services layer  ·  Step 5 · pagination + filter in list_initiatives
# Step 6 · owner_id comes from the logged-in user; update/delete get the already-checked object
# Step 11 · build_summary (text for the streaming endpoint)
# Concepts: thin routers, domain errors (NotFoundError), select/where/offset/limit/count.
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Initiative, Milestone
from app.schemas.initiative import InitiativeCreate, InitiativeUpdate, MilestoneCreate


def create_initiative(db: Session, data: InitiativeCreate, owner_id: int) -> Initiative:
    initiative = Initiative(**data.model_dump(), owner_id=owner_id)
    db.add(initiative)
    db.commit()
    db.refresh(initiative)
    return initiative


def list_initiatives(
    db: Session, skip: int, limit: int, status: str | None = None
) -> tuple[list[Initiative], int]:
    stmt = select(Initiative)
    if status is not None:                       # filter only if the client sent ?status=
        stmt = stmt.where(Initiative.status == status)

    # total = how many rows match the filter (for "page 1 of 5" in the UI)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    # ORDER BY id: a stable order, so pages don't shuffle. Then skip + take `limit`.
    items = db.scalars(stmt.order_by(Initiative.id).offset(skip).limit(limit)).all()
    return list(items), total


def get_initiative(db: Session, initiative_id: int) -> Initiative:
    initiative = db.get(Initiative, initiative_id)
    if initiative is None:
        raise NotFoundError("Initiative", initiative_id)  # main.py turns this into 404
    return initiative


# The router already loaded + permission-checked the initiative (OwnedInitiative),
# so these receive the object instead of the id.
def update_initiative(db: Session, initiative: Initiative, data: InitiativeUpdate) -> Initiative:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(initiative, field, value)
    db.commit()
    db.refresh(initiative)
    return initiative


def delete_initiative(db: Session, initiative: Initiative) -> None:
    db.delete(initiative)  # cascade also deletes its milestones
    db.commit()


def create_milestone(db: Session, initiative: Initiative, data: MilestoneCreate) -> Milestone:
    milestone = Milestone(**data.model_dump(), initiative_id=initiative.id)
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


def list_milestones(db: Session, initiative_id: int) -> list[Milestone]:
    return get_initiative(db, initiative_id).milestones


# Step 11 · "AI" summary text (a real app would ask an LLM here)
def build_summary(initiative: Initiative) -> str:
    done = sum(1 for m in initiative.milestones if m.done)
    total = len(initiative.milestones)
    return (
        f"{initiative.name} is currently {initiative.status} with a budget of {initiative.budget}. "
        f"{done} of {total} milestones are done. "
        f"{initiative.description or 'No description was given.'}"
    )
