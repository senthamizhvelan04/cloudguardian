from app.models.domain import Incident, Status, AuditEvent
from app.models.store import store
from app.services.aws.client import AWSService
from app.services.risk import assess

class RemediationEngine:
    def __init__(self, aws: AWSService) -> None:
        self.aws = aws

    def execute(self, incident: Incident, action: str, approved_by: str | None = None) -> dict:
        decision = assess(action)
        if decision.approval_required and not approved_by:
            raise PermissionError(f"{action} requires human approval")
        incident.status = Status.REMEDIATING
        command_id = self.aws.send_ssm(incident.instance, action)
        incident.status = Status.VERIFYING
        store.add_audit(AuditEvent(
            incident_id=incident.id,
            event="REMEDIATION_EXECUTED",
            actor=approved_by or "system",
            details={"action": action, "risk": decision.level, "command_id": command_id},
        ))
        return {"action": action, "command_id": command_id}
