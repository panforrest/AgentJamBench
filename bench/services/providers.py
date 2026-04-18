from __future__ import annotations

import os
import time
from typing import Any

import httpx
from openai import OpenAI

from .mock_llm import mock_llm_enabled, mock_reply_for_prompt


def _extract_chat_text(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if choices:
        msg = (choices[0] or {}).get("message") or {}
        content = msg.get("content")
        if isinstance(content, str):
            return content
    for key in ("text", "output", "generated_text"):
        v = data.get(key)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def call_openai(
    *,
    prompt: str,
    model: str,
    system: str | None,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    if mock_llm_enabled():
        t0 = time.perf_counter()
        text = mock_reply_for_prompt(prompt)
        dt_ms = max(15, int((time.perf_counter() - t0) * 1000) + 12)
        return {
            "ok": True,
            "text": text,
            "duration_ms": dt_ms,
            "usage": {
                "prompt_tokens": 80,
                "completion_tokens": 120,
                "total_tokens": 200,
            },
            "raw_model": model,
            "mock": True,
        }

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {
            "ok": False,
            "error": {"type": "config", "message": "OPENAI_API_KEY is not set"},
        }

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    client = OpenAI(api_key=api_key)
    t0 = time.perf_counter()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as e:
        dt_ms = int((time.perf_counter() - t0) * 1000)
        return {
            "ok": False,
            "duration_ms": dt_ms,
            "error": {"type": "openai", "message": str(e)},
        }

    dt_ms = int((time.perf_counter() - t0) * 1000)
    text = (resp.choices[0].message.content or "").strip()
    usage = None
    if resp.usage:
        usage = {
            "prompt_tokens": resp.usage.prompt_tokens,
            "completion_tokens": resp.usage.completion_tokens,
            "total_tokens": resp.usage.total_tokens,
        }
    return {
        "ok": True,
        "text": text,
        "duration_ms": dt_ms,
        "usage": usage,
        "raw_model": model,
    }


def call_baseten(
    *,
    prompt: str,
    system: str | None,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    if mock_llm_enabled():
        t0 = time.perf_counter()
        text = mock_reply_for_prompt(prompt)
        dt_ms = max(18, int((time.perf_counter() - t0) * 1000) + 15)
        return {
            "ok": True,
            "text": text,
            "duration_ms": dt_ms,
            "usage": {
                "prompt_tokens": 80,
                "completion_tokens": 120,
                "total_tokens": 200,
            },
            "mock": True,
        }

    url = os.environ.get("BASETEN_DEPLOYMENT_URL", "").strip()
    api_key = os.environ.get("BASETEN_API_KEY", "").strip()
    if not url or not api_key:
        return {
            "ok": False,
            "error": {
                "type": "config",
                "message": "BASETEN_DEPLOYMENT_URL and BASETEN_API_KEY must be set",
            },
        }

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload: dict[str, Any] = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    model_id = os.environ.get("BASETEN_MODEL_ID", "").strip()
    if model_id:
        payload["model"] = model_id

    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/json",
    }

    t0 = time.perf_counter()
    try:
        with httpx.Client(timeout=120.0) as client:
            r = client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPStatusError as e:
        dt_ms = int((time.perf_counter() - t0) * 1000)
        body = ""
        try:
            body = e.response.text[:2000]
        except Exception:
            pass
        return {
            "ok": False,
            "duration_ms": dt_ms,
            "error": {
                "type": "baseten_http",
                "status": e.response.status_code,
                "message": str(e),
                "body": body,
            },
        }
    except Exception as e:
        dt_ms = int((time.perf_counter() - t0) * 1000)
        return {
            "ok": False,
            "duration_ms": dt_ms,
            "error": {"type": "baseten", "message": str(e)},
        }

    dt_ms = int((time.perf_counter() - t0) * 1000)
    text = _extract_chat_text(data if isinstance(data, dict) else {})
    usage = data.get("usage") if isinstance(data, dict) else None
    return {
        "ok": True,
        "text": text.strip(),
        "duration_ms": dt_ms,
        "usage": usage,
        "raw": data if isinstance(data, dict) else {"raw": data},
    }
