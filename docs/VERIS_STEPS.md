# Veris — how to “try access” (hackathon checklist)

**AgentJamBench** currently ships a **static** “Scenario Pack v1” JSON (`bench/data/default_suite.json`) for **Veris-style** demos. **Live Veris** uses the **Veris CLI** and (usually) **Docker** packaging of your agent — it is **not** the same as calling `/api/run/suite/` in Django.

Official docs: [Veris Quickstart](https://docs.veris.ai/quickstart) · [CLI installation](https://docs.veris.ai/cli/installation)

## Prerequisites

- Account / whitelist for **[console.veris.ai](https://console.veris.ai)** (organizers email you after signup).
- An **API key** from Veris when available (`veris login YOUR_API_KEY` or browser login).

## Minimum steps (from Veris quickstart)

1. **Install CLI** (pick one):

   ```bash
   pip install veris-cli
   # or
   uv tool install veris-cli
   ```

2. **Log in**

   ```bash
   veris login
   ```

   Browser auth, **or** for scripts/CI:

   ```bash
   veris login YOUR_API_KEY
   ```

3. **Create a Veris environment** (from your agent project directory — often a **separate** folder from this repo if you package the agent for simulation):

   ```bash
   cd /path/to/your-agent-project
   veris env create --name "my-agent"
   ```

   This creates **`.veris/`** with `veris.yaml`, `Dockerfile.sandbox`, etc.

4. **Configure** `.veris/veris.yaml` and `Dockerfile.sandbox` so Veris knows how to talk to your agent (HTTP port, entry command, secrets). See [Quickstart](https://docs.veris.ai/quickstart).

5. **Push + scenarios + run** (when config is ready):

   ```bash
   veris env push
   veris scenarios create
   veris run
   ```

   Or step-by-step: `veris simulations create`, `veris evaluations create`, `veris reports create` (see docs).

## Realistic expectations for a one-day hack

- **Full Veris integration** = packaging your agent, Veris build/push, scenarios — often **hours**, not minutes.
- **For judging today**, it’s OK to say: **scenario pack is Veris-aligned**; **full sandbox + CLI pipeline** is **next step** after the event.

## AgentJamBench API bridge (lightweight)

After `veris login`, if `veris` is on the **same PATH** Django uses:

- **`GET /api/veris/probe/`** — confirms the CLI is visible to the server + runs `veris --version`.
- **`GET /api/veris/scenarios/`** — runs **`veris scenarios list`** and returns stdout (scenario sets in your Veris account).

If Django still cannot find `veris`, set **`VERIS_CLI_PATH`** in `.env` to the full path (from `which veris`). The backend also tries **`~/.local/bin/veris`** (typical **pipx** location) even when that directory is missing from `PATH`.

This is **“import scenarios from Veris”** at the **list/metadata** level. Mapping those sets into our SQLite benchmark format is extra work. **Running inside the simulator** still requires **`veris env create`**, **`veris env push`**, and **`veris simulations create`** — not bundled into this endpoint.

## Optional: Python SDK (different use case)

For **tool mocking / FastAPI MCP** inside simulations, see [`veris-ai` on PyPI](https://pypi.org/project/veris-ai/) — useful when your code runs **inside** Veris’s simulation, not required for our current Django benchmark UI.
