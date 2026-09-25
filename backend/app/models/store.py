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

store = MemoryStore()
