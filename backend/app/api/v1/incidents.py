from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.models.domain import Approval, AuditEvent, Incident, Status
from app.models.store import store
from app.schemas.api import (
    ActionResponse,
    ApprovalRequest,
    DiagnosisResponse,
    IncidentCreate,
    IncidentUpdate,
    RemediationRequest,
)
from app.services.agent.orchestrator import ControlledAgent
from app.services.ai.diagnosis import DiagnosisService
from app.services.aws.client import AWSService
from app.services.remediation.engine import RemediationEngine
from app.services.risk import assess

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])
diagnosis = DiagnosisService()
aws = AWSService()
remediation = RemediationEngine(aws)
agent = ControlledAgent()

@router.post("", response_model=Incident, status_code=status.HTTP_201_CREATED)
def create(payload: IncidentCreate):
    incident = Incident(**payload.model_dump())
    store.incidents[incident.id] = incident
    store.add_audit(AuditEvent(incident_id=incident.id, event="INCIDENT_CREATED", details={"type": incident.type.value}))
    return incident

@router.get("", response_model=list[Incident])
def list_incidents():
    return list(store.incidents.values())

@router.get("/{incident_id}", response_model=Incident)
def get(incident_id: str):
    incident = store.incidents.get(incident_id)
    if not incident:
        raise HTTPException(404, "Incident not found")
    return incident

@router.put("/{incident_id}", response_model=Incident)
def update(incident_id: str, payload: IncidentUpdate):
    incident = store.incidents.get(incident_id)
    if not incident:
        raise HTTPException(404, "Incident not found")
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(400, "No fields supplied")
    for key, value in data.items():
        setattr(incident, key, value)
    incident.updated_at = datetime.now(UTC)
    return incident

@router.post("/{incident_id}/diagnose", response_model=DiagnosisResponse)
def diagnose_incident(incident_id: str):
    incident = get(incident_id)
    incident.status = Status.INVESTIGATING
    result = diagnosis.diagnose(incident)
    incident.diagnosis = result["diagnosis"]
    incident.recommendation = result["recommendation"]
    incident.confidence = result["confidence"]
    incident.evidence = result["evidence"]
    incident.status = Status.DIAGNOSED
    plan = agent.plan(incident.recommendation)
    store.add_audit(AuditEvent(incident_id=incident.id, event="DIAGNOSIS_COMPLETED", details={**result, **plan}))
    return DiagnosisResponse(
        incident_id=incident.id,
        **result,
        risk=plan["risk"],
        approval_required=plan["approval_required"],
    )

@router.post("/{incident_id}/approve")
def approve(incident_id: str, payload: ApprovalRequest):
    incident = get(incident_id)
    decision = assess(payload.action)
    if not decision.approval_required:
        raise HTTPException(400, "This action does not require approval")
    approval = Approval(incident_id=incident.id, action=payload.action, approved_by=payload.approved_by, approved=payload.approved)
    store.approvals[incident.id] = approval
    store.add_audit(AuditEvent(incident_id=incident.id, event="HUMAN_APPROVAL", actor=payload.approved_by, details=approval.model_dump(mode="json")))
    return approval

@router.post("/{incident_id}/remediate", response_model=ActionResponse)
def remediate(incident_id: str, payload: RemediationRequest):
    incident = get(incident_id)
    decision = assess(payload.action)
    approver = payload.approved_by
    if decision.approval_required:
        approval = store.approvals.get(incident.id)
        if not approval or not approval.approved or approval.action != payload.action:
            raise HTTPException(403, "Human approval is required for this action")
        approver = approval.approved_by
    try:
        result = remediation.execute(incident, payload.action, approver)
        return ActionResponse(incident_id=incident.id, action=payload.action, status="submitted", message="Controlled remediation submitted.", command_id=result["command_id"])
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
        incident.status = Status.FAILED
        raise HTTPException(502, str(exc)) from exc

@router.post("/{incident_id}/verify", response_model=Incident)
def verify(incident_id: str):
    incident = get(incident_id)
    if incident.type.value == "SERVICE_DOWN":
        if aws.enabled:
            result = aws.status(incident.instance)
            if result.get("state") != "running":
                incident.status = Status.FAILED
                return incident
        incident.status = Status.RESOLVED
    else:
        incident.status = Status.RESOLVED
    store.add_audit(AuditEvent(incident_id=incident.id, event="RECOVERY_VERIFIED", details={"status": incident.status.value}))
    return incident
