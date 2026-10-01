# Service Down

1. Check deployment state: `docker ps | grep cloudguardian` (Docker) or `systemctl is-active cloudguardian-test.service` (systemd).
2. Inspect recent container logs or journal entries.
3. Determine whether the service stopped or failed.
4. Request human approval for restart.
5. Execute only the allowlisted restart action through SSM. Note that automated SSM remediation targets the Docker container.
6. Verify service state and application health.
