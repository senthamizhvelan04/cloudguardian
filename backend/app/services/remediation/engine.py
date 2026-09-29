from app.models.domain import AuditEvent, Incident, Status
from app.models.store import store
from app.services.aws.client import AWSService
from app.services.risk import assess


class RemediationEngine:
    def __init__(self, aws: AWSService) -> None:
        self.aws = aws

    def execute(
        self,
        incident: Incident,
        action: str,
        approved_by: str | None = None,
    ) -> dict:
        decision = assess(action)

        if decision.approval_required and not approved_by:
            raise PermissionError(
                f"{action} requires human approval"
            )

        incident.status = Status.REMEDIATING

        command_id = self.aws.send_ssm(
            incident.instance,
            action,
        )

        store.add_audit(
            AuditEvent(
                incident_id=incident.id,
                event="REMEDIATION_EXECUTED",
                actor=approved_by or "system",
                details={
                    "action": action,
                    "risk": decision.level,
                    "command_id": command_id,
                },
            )
        )

        incident.status = Status.VERIFYING

        command_result = self.aws.wait_for_ssm_command(
            command_id,
            incident.instance,
        )

        if command_result["status"] != "Success":
            incident.status = Status.FAILED

            store.add_audit(
                AuditEvent(
                    incident_id=incident.id,
                    event="REMEDIATION_FAILED",
                    actor=approved_by or "system",
                    details={
                        "action": action,
                        "command_id": command_id,
                        "ssm_status": command_result["status"],
                        "stderr": command_result.get(
                            "stderr",
                            "",
                        ),
                    },
                )
            )

            return {
                "action": action,
                "command_id": command_id,
                "status": "failed",
                "ssm_status": command_result["status"],
            }

        recovery = self.aws.verify_recovery(
            incident.instance,
        )

        if recovery["success"]:
            incident.status = Status.RESOLVED

            store.add_audit(
                AuditEvent(
                    incident_id=incident.id,
                    event="RECOVERY_VERIFIED",
                    actor="system",
                    details={
                        "action": action,
                        "command_id": command_id,
                        "verification": recovery,
                    },
                )
            )

            return {
                "action": action,
                "command_id": command_id,
                "status": "resolved",
                "message": (
                    "Remediation completed and "
                    "recovery verified."
                ),
            }

        incident.status = Status.FAILED

        store.add_audit(
            AuditEvent(
                incident_id=incident.id,
                event="RECOVERY_VERIFICATION_FAILED",
                actor="system",
                details={
                    "action": action,
                    "command_id": command_id,
                    "verification": recovery,
                },
            )
        )

        return {
            "action": action,
            "command_id": command_id,
            "status": "failed",
            "message": (
                "Remediation completed but "
                "recovery verification failed."
            ),
        }

