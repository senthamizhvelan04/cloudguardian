# Service Down

1. Check `systemctl is-active cloudguardian-test.service`.
2. Inspect recent journal entries.
3. Determine whether the service stopped or failed.
4. Request human approval for restart.
5. Execute only the allowlisted restart action through SSM.
6. Verify service state and application health.
