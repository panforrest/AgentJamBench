# AgentJamBench

## Introduction

**AgentJamBench** is a hackathon project for **Enterprise Agent Jam NYC**. It is an agent evaluation workbench: you run a **shared task suite** against **more than one model provider**, store results in one place, and compare **speed, estimated cost, and quality** in a small dashboard—useful for demos and for iterating on prompts and model choice.

## Core features

- **Multi-provider runs** — Same tasks through **OpenAI** and **Baseten** (HTTP deployment), with normalized responses and timing.
- **Suite & batch benchmarks** — Default **Scenario Pack** (JSON task suite), single-task and full-suite runs via the REST API.
- **LLM-as-judge** — Rubric-style scoring (with a **mock** path when `MOCK_LLM=1` for offline rehearsal).
- **Run history & drill-down** — Persisted runs and per-task results for review in the **React + Vite** UI (`frontend/`).
- **Veris-friendly stub** — Root **`app/`** FastAPI stub + **`pyproject.toml`** for **`veris env push`** / sandbox alignment (separate from the Django API).

For API routes and build notes, see `MVP_SPEC_FOR_CURSOR.md`. For Veris CLI and sandbox steps, see `docs/VERIS_STEPS.md`.

## Team

- Forrest Pan  
- Frank Yu  
- Fred Yan  
- Jin Thakur  

## Tech stack

| Layer | Technologies |
|--------|----------------|
| **Backend** | Python 3, **Django 5**, **Django REST Framework** |
| **Database** | **SQLite** (default; swap for Postgres/MySQL in production if needed) |
| **Config & HTTP** | **python-dotenv** (`.env` for secrets), **httpx** (Baseten / HTTP calls) |
| **API & CORS** | **django-cors-headers** (React or other frontends on another origin) |
| **LLM integrations** | **OpenAI** Python SDK (baseline runs + LLM-as-judge), **Baseten** via deployment URL + API key |
| **Frontend** | **React 19**, **TypeScript**, **Vite** — dashboard (`frontend/`), **React Router** |

## Quick start

**Backend (Django):**

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add API keys; never commit .env
# Rehearsal without keys: set MOCK_LLM=1 in .env (default in template). Use MOCK_LLM=0 for real APIs.
python manage.py migrate
python manage.py runserver   # http://127.0.0.1:8000
```

**Frontend (in a second terminal):**

```bash
cd frontend
npm install
npm run dev                  # http://127.0.0.1:5173 — proxies /api → Django
```

Open the Vite URL in your browser. The UI loads suite info, runs the benchmark (OpenAI and/or Baseten), lists recent runs, and links to per-run detail.

- **`http://127.0.0.1:8000/`** — short HTML landing page with API links (not the React app).  
- **`http://127.0.0.1:5173/`** — full dashboard (run `npm run dev` in `frontend/`).

- API health: `GET http://127.0.0.1:8000/api/health/`  
- Veris CLI (after `veris login`): `GET http://127.0.0.1:8000/api/veris/probe/` and `GET http://127.0.0.1:8000/api/veris/scenarios/`  
- See `MVP_SPEC_FOR_CURSOR.md` for API routes and build notes.  
- **Veris (CLI / sandbox):** `docs/VERIS_STEPS.md` — how to try the official Veris flow (separate from the in-app static scenario pack).

## How we build & test

We implement in small steps and **pause for manual testing** (API + UI) before moving on — especially before demo time.

## Repository

https://github.com/panforrest/AgentJamBench
