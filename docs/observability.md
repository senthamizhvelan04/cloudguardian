# Observability

The service exposes Prometheus metrics at `/metrics`.

Recommended production signals:

- request rate
- API error rate
- incident detection count
- diagnosis latency
- remediation success/failure
- verification success/failure
- MTTD
- MTTR
- SSM command latency
- CloudWatch event ingestion failures
