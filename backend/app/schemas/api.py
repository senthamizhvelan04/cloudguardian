from datetime import datetime
from pydantic import BaseModel, Field
from app.models.domain import IncidentType, Severity, Status

class IncidentCreate(BaseModel):
    type: IncidentType
    instance: str = Field(min_length=1, max_length=128)
    severity: Severity
    description: str = Field(min_length=1, max_length=4000)
    cpu: float | None = Field(default=None, ge=0, le=100)

class IncidentUpdate(BaseModel):
    type: IncidentType | None = None
    instance: str | None = Field(default=None, min_length=1, max_length=128)
    severity: Severity | None = None
    status: Status | None = None
    description: str | None = Field(default=None, min_length=1, max_length=4000)
    cpu: float | None = Field(default=None, ge=0, le=100)

class DiagnosisResponse(BaseModel):
    incident_id: str
    diagnosis: str
    recommendation: str
    confidence: float
    evidence: list[str]
    risk: str
    approval_required: bool

class RemediationRequest(BaseModel):
    action: str
    approved_by: str | None = None

class ApprovalRequest(BaseModel):
    action: str
    approved_by: str = Field(min_length=2, max_length=128)
    approved: bool = True

class CloudWatchEvent(BaseModel):
    detail_type: str = "CloudWatch Alarm State Change"
    alarm_name: str
    state: str
    instance_id: str
    metric: str
    description: str = ""
    severity: Severity = Severity.HIGH

class ActionResponse(BaseModel):
    incident_id: str
    action: str
    status: str
    message: str
    command_id: str | None = None

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime
