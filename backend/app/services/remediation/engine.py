import logging

from app.models.domain import AuditEvent, Incident, Status
from app.models.store import store
from app.services.aws.client import AWSService
from app.services.risk import assess

logger = logging.getLogger(__name__)


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

        try:
            command_id = self.aws.send_ssm(
                incident.instance,
                action,
            )
        except Exception:
            logger.exception("Failed to send SSM command")
            incident.status = Status.FAILED
            logger.warning("Remediation failed. Manual intervention may be required.")
            return {
                "action": action,
                "status": "failed",
                "message": "Failed to send SSM command",
            }

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

        try:
            command_result = self.aws.wait_for_ssm_command(
                command_id,
                incident.instance,
            )
        except Exception:
            logger.exception("Failed to wait for SSM command")
            incident.status = Status.FAILED
            logger.warning("Remediation failed. Manual intervention may be required.")
            return {
                "action": action,
                "status": "failed",
                "message": "Failed to wait for SSM command",
            }

        if command_result["status"] != "Success":
            incident.status = Status.FAILED
            logger.warning("Remediation failed with status %s. Manual intervention may be required.", command_result["status"])

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

        try:
            recovery = self.aws.verify_recovery(
                incident.instance,
            )
        except Exception:
            logger.exception("Failed to verify recovery")
            incident.status = Status.FAILED
            logger.warning("Recovery verification failed. Manual intervention may be required.")
            return {
                "action": action,
                "status": "failed",
                "message": "Failed to verify recovery",
            }

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
        logger.warning("Recovery verification failed. Manual intervention may be required.")

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

