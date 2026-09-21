from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class IncidentType(str, Enum):
    HIGH_CPU = "HIGH_CPU"
    HIGH_MEMORY = "HIGH_MEMORY"
    HIGH_DISK = "HIGH_DISK"
    SERVICE_DOWN = "SERVICE_DOWN"
    HTTP_5XX = "HTTP_5XX"
    HEALTH_CHECK_FAILED = "HEALTH_CHECK_FAILED"
    BAD_CONFIGURATION = "BAD_CONFIGURATION"
    FAILED_DEPLOYMENT = "FAILED_DEPLOYMENT"
    EC2_DEGRADATION = "EC2_DEGRADATION"

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Status(str, Enum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    DIAGNOSED = "DIAGNOSED"
    REMEDIATING = "REMEDIATING"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"

class Incident(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: IncidentType
    instance: str
    severity: Severity
    status: Status = Status.DETECTED
    description: str
    cpu: float | None = Field(default=None, ge=0, le=100)
    evidence: list[str] = Field(default_factory=list)
    diagnosis: str | None = None
    recommendation: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class Approval(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str
    action: str
    approved_by: str | None = None
    approved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class AuditEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str | None = None
    event: str
    actor: str = "system"
    details: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
