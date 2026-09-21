from fastapi import APIRouter, HTTPException
from app.services.aws.client import AWSService
router = APIRouter(prefix="/api/v1/aws", tags=["aws"])
aws = AWSService()

@router.get("/status/{instance_id}")
def status(instance_id: str):
    try:
        return aws.status(instance_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.get("/cpu/{instance_id}")
def cpu(instance_id: str):
    try:
        return {"instance_id": instance_id, "cpu_percent": aws.cpu(instance_id)}
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
