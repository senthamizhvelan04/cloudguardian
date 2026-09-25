from datetime import UTC, datetime

from fastapi import APIRouter

from app.schemas.api import HealthResponse

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "CloudGuardian CI/CD deployment successful"}

@router.get("/ready")
def ready():
    return {"status": "ready", "dependencies": {"api": "ok"}}
