from fastapi import APIRouter
from app.models.store import store
router = APIRouter(prefix="/api/v1/audit", tags=["audit"])

@router.get("")
def audit():
    return store.audit
