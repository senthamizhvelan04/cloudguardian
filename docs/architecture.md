# Architecture

CloudGuardian separates detection, evidence gathering, diagnosis, decisioning and execution.

## Principles

- least privilege
- explicit tool allowlist
- human approval for risky actions
- evidence before remediation
- recovery verification
- immutable-style audit events
- deterministic fallback when external AI is unavailable

## Data flow

CloudWatch alarm/event → event ingestion → incident record → AWS evidence → RAG retrieval → diagnosis → risk decision → approval → SSM → verification → audit.
