from app.models.domain import Incident
from app.services.rag.retriever import RunbookRetriever

class DiagnosisService:
    def __init__(self) -> None:
        self.rag = RunbookRetriever()

    def diagnose(self, incident: Incident) -> dict:
        matches = self.rag.retrieve(f"{incident.type.value} {incident.description}", top_k=3)
        evidence = [f"Runbook: {m['source']}" for m in matches]
        if incident.cpu is not None and incident.cpu >= 70:
            diagnosis = "Elevated CPU utilization is consistent with compute saturation or a CPU-intensive workload."
            recommendation = "Inspect the top CPU-consuming processes and restart the approved test service only after approval."
            confidence = 0.90
        elif incident.type.value == "SERVICE_DOWN":
            diagnosis = "The monitored service is not active or failed its health check."
            recommendation = "Inspect recent service logs and restart the allowlisted service after approval."
            confidence = 0.94
        elif incident.type.value == "HIGH_MEMORY":
            diagnosis = "Memory pressure is consistent with a high-memory workload or insufficient available memory."
            recommendation = "Inspect memory consumers and collect logs before considering a controlled restart."
            confidence = 0.86
        elif incident.type.value == "HIGH_DISK":
            diagnosis = "Filesystem utilization is above the configured threshold."
            recommendation = "Inspect disk usage and logs; do not delete data automatically."
            confidence = 0.91
        else:
            diagnosis = "The incident matches a monitored CloudOps failure scenario requiring evidence collection."
            recommendation = "Collect evidence, consult the relevant runbook, and apply only an approved remediation."
            confidence = 0.72
        return {"diagnosis": diagnosis, "recommendation": recommendation, "confidence": confidence, "evidence": evidence}
