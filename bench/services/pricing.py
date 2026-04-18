"""Rough USD estimates per 1M tokens (input / output) — label outputs as *estimate*."""

# Hackathon defaults; tune to match billing dashboard.
PRICE_PER_1M = {
    "gpt-4o-mini": {"in": 0.15, "out": 0.60},
    "gpt-4o": {"in": 2.50, "out": 10.00},
    "gpt-4.1-mini": {"in": 0.40, "out": 1.60},
    "default": {"in": 0.50, "out": 2.00},
}


def estimate_cost_usd(
    model: str,
    prompt_tokens: int | None,
    completion_tokens: int | None,
) -> float | None:
    if prompt_tokens is None and completion_tokens is None:
        return None
    pt = int(prompt_tokens or 0)
    ct = int(completion_tokens or 0)
    key = model if model in PRICE_PER_1M else "default"
    rates = PRICE_PER_1M[key]
    return (pt / 1_000_000) * rates["in"] + (ct / 1_000_000) * rates["out"]
