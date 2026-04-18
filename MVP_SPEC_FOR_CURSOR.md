# AgentJamBench — MVP spec for Cursor (Enterprise Agent Jam NYC)

**Product:** Agent evaluation workbench — run the **same task suite** against **multiple models** (Baseten-hosted + OpenAI baseline), compare **latency / estimated cost / quality**, optionally framed as **Veris-style production stress tests**, and **export** a judge-scored report.

**Repo / folder:** `AgentJamBench`  
**Git:** Clean repo initialized in this directory; `.env` is **gitignored** — use `.env.example` as the template.

**Local setup (run once):**

```bash
cd AgentJamBench
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp -n .env.example .env     # then edit .env — never commit .env
python manage.py migrate
python manage.py runserver
```

If `venv` fails on Debian/Ubuntu: `sudo apt install python3.12-venv` (version may vary).

**Process agreement:** After **each build step** below, **pause for review and manual testing** with your teammate before moving on.

---

## KEY FEATURES (build priority order)

1. **End-to-end “happy path” API** — One endpoint runs **one task** through **OpenAI** and returns text + timing (proves wiring).
2. **Baseten path** — Second provider: call your **Baseten deployment URL** with server-side key; normalize response shape to match OpenAI path.
3. **Batch suite run** — N tasks × M models with **bounded concurrency** (e.g., 2–3 workers), **progress** via polling (`run` id + status %) or simple synchronous MVP for ≤10 tasks.
4. **Deterministic scoring** — For **subset of tasks**: JSON-schema validation, exact match, or scripted checks → **pass/fail** + points.
5. **LLM-as-judge (OpenAI)** — Rubric dimensions (e.g., correctness, instruction following, safety tone); **structured JSON** output from judge; aggregate per model.
6. **Latency & cost panel** — Per task and aggregates: duration (and optional TTFT if streaming later); **estimated $** from a small in-code pricing table (labeled **estimate**).
7. **Leaderboard view** — Sortable table: model, mean rubric score, avg latency, est. cost, deterministic pass rate.
8. **Per-task drill-down** — Prompt → each model output → judge breakdown + errors (redact API keys).
9. **Veris narrative (MVP)** — **“Scenario Pack v1”**: bundled JSON of **10–20** enterprise-ish / adversarial-safe prompts (personas, ambiguity, policy); badge in UI; optional future: import from Veris when available.
10. **Export** — Download **HTML** (fast) or **JSON** report: summary, methodology, results table, appendix snippets.
11. **Stretch (only if ahead of schedule)** — Streaming TTFT; third model slot; tool-calling tasks + mock tools; prompt-diff rerun for “regression” story.

---

## TECHNOLOGY INTEGRATIONS (tech stack)

| Layer | Choice | Notes |
|--------|--------|--------|
| Backend | **Django 5** + **Django REST Framework** | Orchestrates runs, stores results, serves API. |
| Config | **python-dotenv** | Loads **`.env`** (never commit). |
| DB | **SQLite** | Hackathon default; swap later if needed. |
| Frontend | **React (Vite) + TypeScript** (recommended) | Dashboard, leaderboard, traces, export trigger. |
| CORS | **django-cors-headers** | Dev + local React origin via `CORS_ALLOWED_ORIGINS` or DEBUG fallback. |
| OpenAI | **openai** Python SDK | Baseline completions/chat + **judge** model. |
| Baseten | **httpx** (or SDK if you standardize) | POST to `BASETEN_DEPLOYMENT_URL` with `BASETEN_API_KEY`. |
| Veris | **Narrative + static pack MVP** | Real API/import if credentials + docs available; not blocking for MVP. |

**Environment variables (see `.env.example`):** `DJANGO_SECRET_KEY`, `OPENAI_API_KEY`, `BASETEN_API_KEY`, `BASETEN_DEPLOYMENT_URL`, optional `VERIS_API_KEY`, `CORS_ALLOWED_ORIGINS`.

---

## VISUAL DESIGN & WEB PAGES (Visual Design)

**Principles:** Read well on a projector; **dense but legible** tables; one **hero** chart (e.g., bar: avg latency by model).

| Page / view | Purpose |
|-------------|---------|
| **Landing / Dashboard** | Project title **AgentJamBench**, CTA “Run benchmark”, last run summary. |
| **Suite** | List tasks (tags: difficulty, category); show **Scenario Pack v1** badge; optional import JSON. |
| **Run setup** | Pick models (OpenAI model id, Baseten deployment), temperature, max tokens; **Run** button. |
| **Live progress** | Progress bar + per-model status; cancel is optional. |
| **Results — Leaderboard** | Table + small charts (latency, est. cost). |
| **Results — Task detail** | Side-by-side answers; judge scores; deterministic checks; error badges (timeout, rate limit, invalid JSON). |
| **Export** | Button: download HTML/JSON report. |

**Style:** Dark or light **single theme**; monospace for prompts; **color-coded** pass/warn/fail; avoid clutter — judges have ~3 minutes.

---

## BUILD STEPS (order: do first → later)

Each step ends with: **stop → review → test → then continue**.

1. **Repo & env** — `.env` / `.env.example`, `.gitignore`, `pip install -r requirements.txt`, `python3 manage.py migrate`, verify server starts.
2. **Health API** — `GET /api/health/` returns `{ "ok": true }`.
3. **OpenAI single task** — `POST /api/run/once/` body: `{ "prompt", "model" }` → text + `duration_ms` + token usage if available.
4. **Baseten single task** — Same contract as (3) for Baseten deployment; unify response DTO in code.
5. **Models & Run models** — Django models for `BenchmarkRun`, `TaskResult` (task id, model key, raw output, timings, errors).
6. **Suite runner** — Load default **10-task** JSON; run all tasks across **two** providers with **concurrency limit**; persist results.
7. **Deterministic checks** — Implement 3–4 tasks with automatic validation.
8. **Judge** — OpenAI call: rubric JSON per task/model output; store scores + short rationale.
9. **Aggregation** — Mean scores, worst tasks, pass rate; API for leaderboard + task detail.
10. **React shell** — Vite app: pages above; consume API; **charts** (e.g., Recharts or Chart.js).
11. **Export** — Server generates HTML bundle or JSON export from stored run.
12. **Veris pack & copy** — Wire **Scenario Pack v1** content + sponsor slide copy (Baseten / OpenAI / Veris).
13. **Polish & demo script** — 3-minute path rehearsed; failure screenshot path if API fails.

---

## MVP constants (do not exceed without time buffer)

- **10 tasks** max for demo run.
- **2 models** (OpenAI + Baseten).
- **Non-streaming** first.
- **Judge:** one model, one rubric template.

---

## Sponsor mapping (for demo narrative)

- **Baseten:** Non-OpenAI inference slot; show latency/cost vs baseline.
- **OpenAI:** Baseline model + LLM-as-judge.
- **Veris:** “Production-like” **scenario pack** + regression mindset (same suite, compare runs).

---

## GitHub remote

Create `https://github.com/panforrest/AgentJamBench` and:

```bash
git remote add origin git@github.com:panforrest/AgentJamBench.git
git push -u origin main
```

(Use `main` after `git branch -m main`.)
