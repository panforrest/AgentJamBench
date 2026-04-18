"""Offline mock LLM for local demos when API keys are not set.

Set MOCK_LLM=1 in .env. Disable for real OpenAI/Baseten calls.
"""

from __future__ import annotations

import os


def mock_llm_enabled() -> bool:
    return os.environ.get("MOCK_LLM", "").strip().lower() in ("1", "true", "yes")


def mock_reply_for_prompt(prompt: str) -> str:
    p = prompt.strip()
    low = p.lower()

    if "exactly the word" in low and "bench" in low:
        return "BENCH"

    if "valid json" in low and "seconds" in low and "minutes" in low:
        return '{"answer":1.5,"unit":"minutes"}'

    if "7 * 8" in p or "(7 * 8)" in p:
        return "61"

    if "system instructions" in low or "reveal system" in low:
        return (
            "I can’t share my system or developer instructions. "
            "I’m happy to help with your task another way."
        )

    if "ambiguous" in low and "ship it friday" in low:
        return "Which Friday did you mean — this week’s Friday or a specific date?"

    if "bypass security review" in low or "polite refusal" in low:
        return (
            "We can’t skip the security review for production. "
            "I can help schedule an expedited review or prepare materials."
        )

    if "clarifying question" in low and "ambiguous" in low:
        return "Which Friday should we target — this week or next?"

    if "p95 latency" in low or ("p95" in low and "one sentence" in low):
        return (
            "p95 latency is the 95th percentile response time — 95% of requests "
            "complete faster than this value."
        )

    if "benchmark harness" in low and "vp" in low:
        return (
            "A benchmark harness runs the same tasks repeatedly across models "
            "so you can compare quality, latency, and cost before rollout."
        )

    if "incident triage" in low and "5xx" in low:
        return (
            "- Confirm scope and blast radius\n"
            "- Check recent deploys and feature flags\n"
            "- Roll back or scale if needed; communicate status"
        )

    if "latency matters" in low and "customer-facing" in low:
        return (
            "Latency directly affects user trust and completion rates for agents. "
            "High tail latency (p95/p99) drives churn in interactive workflows."
        )

    return (
        "[MOCK_LLM] Acknowledged. Configure OPENAI_API_KEY and set MOCK_LLM=0 for real runs."
    )
