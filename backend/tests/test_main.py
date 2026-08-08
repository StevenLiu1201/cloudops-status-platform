"""API endpoint tests."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_status() -> None:
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.json() == {
        "service": "cloudops-api",
        "environment": "development",
        "status": "healthy",
    }


def test_version() -> None:
    response = client.get("/api/version")

    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}


class FakeDatabaseSession:
    """Small session substitute used to keep unit tests independent of PostgreSQL."""

    def execute(self, statement: object) -> None:
        return None


def override_get_db() -> FakeDatabaseSession:
    return FakeDatabaseSession()


def test_database_status() -> None:
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/api/database-status")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"database": "connected"}
