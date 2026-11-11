# ===== tests/test_initiatives.py =====
# Step 8 · One API test
# What: create an initiative, then check it shows up in the list.
# Concepts: pytest, assert, TestClient, dependency_overrides (test DB + fake logged-in user).
# Run from backend/:  pytest -v
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base, get_db
from app.deps import get_current_user
from app.main import app
from app.models import User

# A separate database just for tests, so tracker.db is never touched.
test_engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=test_engine)


def override_get_db():  # same shape as the real get_db, but uses test.db
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


def override_current_user():  # skip JWT: pretend user 1 is logged in
    return User(id=1, email="test@x.com", role="user")


def test_create_then_list_initiative():
    # Arrange: fresh empty tables + swap the real dependencies for fakes
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user
    client = TestClient(app)

    # Act + Assert: create one
    r = client.post("/initiatives", json={"name": "AI pilot", "budget": 500})
    assert r.status_code == 201
    assert r.json()["owner_id"] == 1  # owner = the logged-in (fake) user

    # Act + Assert: it appears in the list
    r = client.get("/initiatives")
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["name"] == "AI pilot"

    app.dependency_overrides.clear()  # undo the fakes so other tests start clean
