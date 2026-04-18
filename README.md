# AgentJamBench

Agent evaluation workbench for **Enterprise Agent Jam NYC** — run the same benchmark tasks across multiple models (e.g., OpenAI + Baseten), compare latency, estimated cost, and judge scores, and review full run details via the API.

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

- API health: `GET http://127.0.0.1:8000/api/health/`  
- See `MVP_SPEC_FOR_CURSOR.md` for API routes and build notes.

## How we build & test

We implement in small steps and **pause for manual testing** (API + UI) before moving on — especially before demo time.

## Repository

https://github.com/panforrest/AgentJamBench
