from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from django.conf import settings


@lru_cache(maxsize=8)
def load_suite(suite_id: str = "default") -> dict:
    base = Path(settings.BASE_DIR) / "bench" / "data"
    if suite_id in ("default", "scenario_pack_v1"):
        path = base / "default_suite.json"
    else:
        path = base / f"{suite_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Suite not found: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)
