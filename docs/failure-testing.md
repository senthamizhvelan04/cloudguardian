# Failure Testing

Use the scripts only on a disposable/test instance.

Recommended demo:

1. Start `cloudguardian-test.service`.
2. Trigger CPU failure.
3. Observe CloudWatch alarm.
4. Ingest/create incident.
5. Diagnose.
6. Show risk/approval requirement.
7. Approve.
8. Execute the allowlisted SSM restart.
9. Verify.
10. Show audit trail and resolved status.

Never test destructive failures on production infrastructure.
