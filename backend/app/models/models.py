# ===== app/models/models.py =====
# Step 2 · SQLAlchemy models (the database tables) - see docs/database_diagram.png
# What: users, initiatives, milestones. Class = table, object = row, attribute = column.
# Concepts: Mapped, mapped_column, primary key, ForeignKey, relationship, cascade, index.
from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)  # no duplicate emails
    hashed_password: Mapped[str]                                  # never the real password
    role: Mapped[str] = mapped_column(default="user")             # "user" or "admin"

    # Not a column: user.initiatives gives the list of this user's initiatives.
    initiatives: Mapped[list["Initiative"]] = relationship(back_populates="owner")


class Initiative(Base):
    __tablename__ = "initiatives"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None]                     # "| None" = optional (NULL allowed)
    status: Mapped[str] = mapped_column(default="planned")  # planned / active / done
    budget: Mapped[float] = mapped_column(default=0)

    # Foreign key: on the "many" side. index=True makes "initiatives of user X" fast.
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    owner: Mapped["User"] = relationship(back_populates="initiatives")
    # cascade: deleting an initiative also deletes its milestones.
    milestones: Mapped[list["Milestone"]] = relationship(
        back_populates="initiative", cascade="all, delete-orphan"
    )


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    due_date: Mapped[date | None]
    done: Mapped[bool] = mapped_column(default=False)

    initiative_id: Mapped[int] = mapped_column(ForeignKey("initiatives.id"), index=True)
    initiative: Mapped["Initiative"] = relationship(back_populates="milestones")
