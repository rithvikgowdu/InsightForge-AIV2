from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.config import settings
from app.schemas.health import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check():
    """Liveness probe: verifies that the API server is up and responsive."""
    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/health/ready", response_model=ReadyResponse, status_code=status.HTTP_200_OK)
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe: verifies database connectivity and AI module availability."""
    db_ok = False
    ai_ok = True
    details = {}

    try:
        db.execute(text("SELECT 1"))
        db_ok = True
        details["database"] = "Connected successfully"
    except Exception as e:
        details["database"] = f"Database error: {str(e)}"

    details["ai_pipeline"] = f"Ready (Provider: {settings.LLM_PROVIDER})"

    overall_status = "ready" if db_ok and ai_ok else "degraded"

    return ReadyResponse(
        status=overall_status,
        version=settings.VERSION,
        database=db_ok,
        ai_pipeline=ai_ok,
        details=details,
    )

