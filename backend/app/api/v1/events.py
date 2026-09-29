from fastapi import APIRouter, Header, HTTPException, status

from app.config import get_settings
from app.models.domain import AuditEvent, Incident, IncidentType, Status
from app.models.store import store
from app.schemas.api import CloudWatchEvent
from app.services.agent.orchestrator import ControlledAgent
from app.services.ai.diagnosis import DiagnosisService


router = APIRouter(
    prefix="/api/v1/events",
    tags=["events"],
)


METRIC_MAP = {
    "CPUUtilization": IncidentType.HIGH_CPU,
    "mem_used_percent": IncidentType.HIGH_MEMORY,
    "used_percent": IncidentType.HIGH_DISK,
}


diagnosis = DiagnosisService()
agent = ControlledAgent()


@router.post(
    "/cloudwatch",
    response_model=Incident,
)
def cloudwatch_event(
    event: CloudWatchEvent,
    x_api_key: str | None = Header(default=None),
):
    settings = get_settings()

    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    incident_type = METRIC_MAP.get(
        event.metric,
        IncidentType.EC2_DEGRADATION,
    )

    incident = Incident(
        type=incident_type,
        instance=event.instance_id,
        severity=event.severity,
        description=(
            event.description
            or (
                f"CloudWatch alarm "
                f"{event.alarm_name} is {event.state}."
            )
        ),
        cpu=(
            event.metric_value
            if event.metric == "CPUUtilization"
            else None
        ),
    )

    store.incidents[incident.id] = incident

    store.add_audit(
        AuditEvent(
            incident_id=incident.id,
            event="CLOUDWATCH_EVENT_INGESTED",
            details=event.model_dump(),
        )
    )

    incident.status = Status.INVESTIGATING

    result = diagnosis.diagnose(incident)

    incident.diagnosis = result["diagnosis"]
    incident.recommendation = result["recommendation"]
    incident.confidence = result["confidence"]
    incident.evidence = result["evidence"]

    incident.status = Status.DIAGNOSED

    plan = agent.plan(
        incident.recommendation
    )

    if plan["approval_required"]:
        incident.status = Status.AWAITING_APPROVAL

    store.add_audit(
        AuditEvent(
            incident_id=incident.id,
            event="AUTOMATIC_DIAGNOSIS_COMPLETED",
            details={
                **result,
                **plan,
                "status": incident.status.value,
            },
        )
    )

    return incident