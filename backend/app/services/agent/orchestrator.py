from app.services.risk import assess

class ControlledAgent:
    """Bounded agent facade: selects only registered actions; never executes arbitrary commands."""

    def plan(self, recommendation: str) -> dict:
        text = recommendation.lower()
        action = "collect_logs"
        if "restart" in text:
            action = "restart_service"
        decision = assess(action)
        return {
            "action": action,
            "risk": decision.level,
            "approval_required": decision.approval_required,
            "reason": "Selected from the CloudGuardian allowlist based on the diagnosis."
        }
