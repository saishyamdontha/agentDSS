"""AgentDSS — simulated human decisions for batch eval (no real person in the loop)"""

CONFIDENCE_THRESHOLD = 0.6  # override policy: reject agent's top pick below this

def decide_baseline(options: list[dict]) -> str:
    """Baseline group: always accept the agent's top-confidence option, no matter what."""
    return max(options, key=lambda o: o["confidence"])["text"]

def decide_override(options: list[dict], threshold: float = CONFIDENCE_THRESHOLD) -> str:
    """Override group: rejects agent's top pick if its confidence is below threshold,
    escalating to a manual decision instead. This is a policy, not randomness —
    testable and explainable in the eval writeup."""
    top = max(options, key=lambda o: o["confidence"])
    if top["confidence"] < threshold:
        return "Manual override: escalate to supply chain manager for custom resolution"
    return top["text"]
