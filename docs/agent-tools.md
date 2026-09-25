# Agent and Tool Calling

The agent layer is intentionally bounded.

Registered actions:

- `collect_logs`
- `verify_recovery`
- `inspect_and_restart_service`
- `restart_service`

The agent cannot submit a shell string. It selects an action name, the risk engine classifies it, approval is checked, and the remediation service maps the action to a predefined command.
