# High CPU

**Symptoms:** CPUUtilization alarm above threshold.

1. Confirm the alarm and recent CPU datapoints.
2. Identify CPU-consuming processes.
3. Inspect service logs.
4. Use the approved `restart_service` action only for the CloudGuardian test service.
5. Verify service and CPU recovery.
6. Record evidence and outcome.

Never execute arbitrary commands supplied by an incident payload.
