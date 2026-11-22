import os

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://helpdesk:helpdesk@localhost:5432/helpdesk_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-at-least-32-bytes")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.models import User
from app.core.database import Base, SessionLocal, engine
from app.core.limiter import limiter
from app.main import app
from app.tickets import router as tickets_router

assert engine.url.database.endswith("test")

limiter.enabled = False


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture(autouse=True)
def enqueued(monkeypatch):
    calls = []
    monkeypatch.setattr(
        tickets_router.notify_ticket_created,
        "delay",
        lambda ticket_id: calls.append(ticket_id),
    )
    return calls


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    def make(email, password="password123", admin=False):
        client.post("/auth/register", json={"email": email, "password": password})
        if admin:
            with SessionLocal() as db:
                user = db.scalar(select(User).where(User.email == email))
                user.role = "admin"
                db.commit()
        response = client.post("/auth/login", data={"username": email, "password": password})
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return make
