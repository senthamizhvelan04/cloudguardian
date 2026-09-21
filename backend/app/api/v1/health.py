from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas.api import HealthResponse
router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service="cloudguardian", version="1.0.0", timestamp=datetime.now(timezone.utc))

@router.get("/ready")
def ready():
    return {"status": "ready", "dependencies": {"api": "ok"}}
