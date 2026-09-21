from fastapi import APIRouter
from app.models.domain import Incident, IncidentType, AuditEvent
from app.models.store import store
from app.schemas.api import CloudWatchEvent
router = APIRouter(prefix="/api/v1/events", tags=["events"])

METRIC_MAP = {
    "CPUUtilization": IncidentType.HIGH_CPU,
    "mem_used_percent": IncidentType.HIGH_MEMORY,
    "used_percent": IncidentType.HIGH_DISK,
}

@router.post("/cloudwatch", response_model=Incident)
def cloudwatch_event(event: CloudWatchEvent):
    incident_type = METRIC_MAP.get(event.metric, IncidentType.EC2_DEGRADATION)
    incident = Incident(
        type=incident_type,
        instance=event.instance_id,
        severity=event.severity,
        description=event.description or f"CloudWatch alarm {event.alarm_name} is {event.state}.",
    )
    store.incidents[incident.id] = incident
    store.add_audit(AuditEvent(incident_id=incident.id, event="CLOUDWATCH_EVENT_INGESTED", details=event.model_dump()))
    return incident
