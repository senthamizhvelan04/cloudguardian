<<<<<<< HEAD
# CloudGuardian — AI-Powered CloudOps & Self-Healing Platform

CloudGuardian is an engineering-focused CloudOps/SRE platform that detects AWS infrastructure incidents, gathers evidence, diagnoses probable causes with an AI/RAG layer, evaluates remediation risk, requests human approval for sensitive actions, executes only allowlisted SSM actions, verifies recovery, and records an auditable incident trail.

## Architecture

```text
AWS EC2 / CloudWatch
        │
        ▼
 Incident Event Ingestion
        │
        ▼
 FastAPI Incident Engine ───────► Audit Log
        │
        ├──► AWS Evidence (CloudWatch / EC2 / SSM)
        │
        ▼
 AI Diagnosis ◄──── RAG Runbooks / Vector Store
        │
        ▼
 Risk & Policy Engine
        │
        ├── LOW ─────────────► Controlled Tool
        │
        └── MED/HIGH ───────► Human Approval
                                  │
                                  ▼
                            SSM Remediation
                                  │
                                  ▼
                             Verification
                                  │
                                  ▼
                         RESOLVED / FAILED
```

## Repository

- `backend/` production-oriented FastAPI service
- `dashboard/` lightweight control-center UI
- `runbooks/` operational knowledge base
- `terraform/` reference AWS infrastructure
- `scripts/` safe failure-injection and smoke tests
- `.github/workflows/` CI, security and deployment workflows
- `docs/` architecture, security, deployment, RAG, agent and demo guides

## Quick start

### Local

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

### Docker

```powershell
docker compose up --build
```

Open `http://localhost:8000`.

### Configuration

Copy `.env.example` to `.env`. Never commit `.env`.

The application is intentionally usable without an LLM or AWS credentials. In local mode, deterministic diagnosis and mock-safe integrations make the API demonstrable. Real AWS remediation requires valid AWS credentials/role permissions and `AWS_ENABLED=true`.

## Core API

- `GET /health`
- `GET /ready`
- `GET /metrics`
- `GET /api/v1/incidents`
- `POST /api/v1/incidents`
- `GET /api/v1/incidents/{id}`
- `POST /api/v1/incidents/{id}/diagnose`
- `POST /api/v1/incidents/{id}/remediate`
- `POST /api/v1/incidents/{id}/approve`
- `POST /api/v1/incidents/{id}/verify`
- `GET /api/v1/aws/status/{instance_id}`
- `GET /api/v1/aws/cpu/{instance_id}`
- `POST /api/v1/events/cloudwatch`

Swagger/OpenAPI is available at `/docs`.

## Safety model

CloudGuardian never accepts arbitrary shell commands through the API. Remediation is selected from an explicit action allowlist. Actions are risk-classified. Medium/high-risk actions require an approval record before execution. AWS access should use IAM roles/short-lived credentials, not embedded keys.

## Production notes

The Terraform directory is a reference deployment stack and should be reviewed against your AWS account, region, budget and existing VPC before `terraform apply`. The default application database is SQLite for portability; PostgreSQL can be introduced by setting `DATABASE_URL`.

See `docs/deployment.md` for the deployment sequence and `docs/aws-setup.md` for the manual AWS work.
=======
# cloudguardian
>>>>>>> fce92c5a71939568c2ea8f99ad881d190336a245
