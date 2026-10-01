from threading import Lock

from app.models.domain import Approval, AuditEvent, Incident


class MemoryStore:
    def __init__(self) -> None:
        self.incidents: dict[str, Incident] = {}
        self.approvals: dict[str, Approval] = {}
        self.audit: list[AuditEvent] = []
        self.lock = Lock()

    def add_audit(self, event: AuditEvent) -> AuditEvent:
        with self.lock:
            self.audit.append(event)
        return event

    def add_incident(self, incident: Incident) -> None:
        with self.lock:
            self.incidents[incident.id] = incident

    def get_incident(self, id: str) -> Incident | None:
        with self.lock:
            return self.incidents.get(id)

    def update_incident(self, id: str, incident: Incident) -> None:
        with self.lock:
            self.incidents[id] = incident

    def list_incidents(self) -> list[Incident]:
        with self.lock:
            return list(self.incidents.values())

    def add_approval(self, approval: Approval) -> None:
        with self.lock:
            self.approvals[approval.incident_id] = approval

    def get_approval(self, id: str) -> Approval | None:
        with self.lock:
            return self.approvals.get(id)

store = MemoryStore()
