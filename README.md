# Tell Me In Your Words

**You don't need the right words.**

A lightweight MVP for intent recovery before expert guidance. Users describe a problem in everyday language; the app suggests likely expert terms, asks for confirmation, explains the term, and routes to trusted context and practical next steps.

📄 **Full product documentation:** [docs/PRODUCT.md](docs/PRODUCT.md) — scope, architecture, configuration, roadmap to full product.

## Repository structure

```text
tell-me-in-your-words/
├── backend/
│   ├── main.py                 # FastAPI entrypoint
│   ├── cli.py                  # tmiyw launcher
│   ├── container.py            # Shared AppContainer singleton
│   ├── config.py               # Environment configuration
│   ├── agents/                 # Single-responsibility agents
│   ├── orchestrator/           # Workflow + session state
│   ├── models/                 # Pydantic API + session models
│   ├── services/               # Knowledge base, cache, care navigation, LLM
│   └── data/terms.json         # Curated term dictionary
├── frontend/
│   ├── app.py                  # Streamlit UI entrypoint
│   ├── session_store.py        # UI ↔ orchestrator bridge
│   └── components/             # Explain dialog, etc.
├── bin/tmiyw                   # Run-from-anywhere launcher
├── tests/
└── docs/
    ├── PRODUCT.md              # Professional MVP + roadmap
    ├── ARCHITECTURE.md
    └── MVP_PLAN.md
```

## Run locally

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**From anywhere** (after `bin/install-alias`):

```bash
tmiyw
```

**Or from project root:**

```bash
streamlit run frontend/app.py
```

**API mode:**

```bash
uvicorn backend.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

### Optional environment

```bash
LLM_ENABLED=true
OPENAI_API_KEY=sk-...
SUGGESTION_CONFIDENCE_THRESHOLD=0.80
```

## Primary API

`POST /session/next` — event-driven session flow:

```json
{
  "session_id": "default",
  "event": "submit_query",
  "payload": { "query": "I have fingles" }
}
```

## Try these

- I think I have fingles
- That paper that keeps secrets
- I want company baskets
- Ho una strana eruzione cutanea dolorosa
- Mujhe daane wali bimari hai

## What the MVP does

1. **Intent recovery** — fuzzy match + optional LLM fallback
2. **Confirmation** — user picks the closest term
3. **Explanation** — curated definition + trusted source
4. **Follow-up guidance** — per-question answers
5. **Consult capture** — stores concern + **Find care near you** map links

## What the MVP does not do

- Diagnose or give personalized medical, legal, or financial advice
- Book appointments or verify providers
- Store accounts or HIPAA-regulated health records

## Architecture

**Orchestrator owns the flow. Agents own one task.**

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/PRODUCT.md](docs/PRODUCT.md).

## Product principle

The AI should not say “you are wrong.” It should say: **“You might mean this. Is that what you were looking for?”**
