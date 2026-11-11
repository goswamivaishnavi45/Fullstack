# ===== app/schemas/initiative.py =====
# Step 3 · Pydantic schemas (+ Step 5: InitiativePage)
# What: the JSON shapes going in and out of the API (NOT database tables).
# Concepts: Create / Update (all optional) / Out (from_attributes), Field, Literal, 422.
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Only these 3 values are allowed; anything else -> 422.
Status = Literal["planned", "active", "done"]


# ---------- Initiative ----------
class InitiativeCreate(BaseModel):  # body of POST
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: Status = "planned"
    budget: float = Field(default=0, ge=0)  # ge=0: no negative budget
    # no owner_id here: the owner is the logged-in user (Step 6), never sent by the client


class InitiativeUpdate(BaseModel):  # body of PATCH: every field optional
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: Status | None = None
    budget: float | None = Field(default=None, ge=0)


class InitiativeOut(BaseModel):  # what the API returns
    model_config = ConfigDict(from_attributes=True)  # can read a SQLAlchemy object

    id: int
    name: str
    description: str | None
    status: Status
    budget: float
    owner_id: int


class InitiativePage(BaseModel):  # one page of results + info for the UI
    items: list[InitiativeOut]
    total: int  # how many match in total (not just this page)
    skip: int
    limit: int


# ---------- Milestone ----------
class MilestoneCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    due_date: date | None = None  # "2026-12-31" in JSON -> date object
    done: bool = False


class MilestoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    due_date: date | None
    done: bool
    initiative_id: int
