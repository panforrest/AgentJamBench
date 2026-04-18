from __future__ import annotations

import json
import re
from typing import Any


def run_deterministic(task: dict[str, Any], output_text: str) -> dict[str, Any]:
    """If task defines validation, return pass/fail + detail. Else unknown."""
    v = task.get("validation")
    if not v or not isinstance(v, dict):
        return {"applies": False}

    kind = v.get("type")
    text = output_text or ""

    if kind == "contains":
        needle = v.get("value", "")
        ok = needle in text
        return {"applies": True, "pass": ok, "detail": {"contains": needle}}

    if kind == "regex":
        pattern = v.get("pattern", "")
        try:
            ok = bool(re.search(pattern, text, re.DOTALL))
        except re.error as e:
            return {"applies": True, "pass": False, "detail": {"regex_error": str(e)}}
        return {"applies": True, "pass": ok, "detail": {"pattern": pattern}}

    if kind == "json_parse":
        try:
            json.loads(text.strip())
            return {"applies": True, "pass": True, "detail": {}}
        except json.JSONDecodeError as e:
            return {
                "applies": True,
                "pass": False,
                "detail": {"error": str(e)},
            }

    return {"applies": False}
