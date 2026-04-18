# AgentJamBench

Agent evaluation workbench for **Enterprise Agent Jam NYC** — run the same benchmark tasks across multiple models (e.g., OpenAI + Baseten), compare latency, estimated cost, and judge scores, and review full run details via the API.

## Team

- Forrest Pan  
- Frank Yu  
- Fred Yan  
- Jin Thakur  

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add API keys; never commit .env
python manage.py migrate
python manage.py runserver
```

- Health: `GET http://127.0.0.1:8000/api/health/`  
- See `MVP_SPEC_FOR_CURSOR.md` for API routes and build notes.

## Repository

https://github.com/panforrest/AgentJamBench
