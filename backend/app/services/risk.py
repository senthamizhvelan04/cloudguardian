from dataclasses import dataclass

@dataclass(frozen=True)
class RiskDecision:
    level: str
    approval_required: bool

ACTION_RISK = {
    "collect_logs": RiskDecision("LOW", False),
    "verify_recovery": RiskDecision("LOW", False),
    "inspect_and_restart_service": RiskDecision("MEDIUM", True),
    "restart_service": RiskDecision("MEDIUM", True),
}

def assess(action: str) -> RiskDecision:
    if action not in ACTION_RISK:
        raise ValueError("Action is not allowlisted")
    return ACTION_RISK[action]
