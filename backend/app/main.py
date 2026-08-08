"""HTTP API for the CloudOps Status Platform."""

from fastapi import Depends, FastAPI, HTTPException, status as http_status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db


app = FastAPI(
    title="CloudOps Status Platform",
    description="A small API used to demonstrate Cloud and DevOps practices.",
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Report whether the API process is responding."""

    return {"status": "healthy"}


@app.get("/api/status", tags=["status"])
def status(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Return the service identity, environment, and current status."""

    return {
        "service": settings.name,
        "environment": settings.environment,
        "status": "healthy",
    }


@app.get("/api/version", tags=["status"])
def version(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Return the configured application version."""

    return {"version": settings.version}


@app.get("/api/database-status", tags=["health"])
def database_status(database: Session = Depends(get_db)) -> dict[str, str]:
    """Verify that PostgreSQL accepts a simple query."""

    try:
        database.execute(text("SELECT 1"))
    except (SQLAlchemyError, RuntimeError) as exc:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        ) from exc

    return {"database": "connected"}
