"""
Minimal HTTP agent for Veris `env push` / simulations.

Contract matches `.veris/veris.yaml`: request field `message`, response field `response`.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="AgentJamBench Veris Agent", version="0.1.0")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User or simulated-user turn")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent reply")


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    text = (req.message or "").strip()
    if not text:
        return ChatResponse(response="[stub] Empty message.")
    return ChatResponse(response=f"[AgentJamBench stub] {text[:4000]}")
