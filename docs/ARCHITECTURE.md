# Architecture

## Overview

The app uses an **event-driven orchestrator** pattern. The UI and API send events; the orchestrator updates session state and delegates to specialist agents.

## Session flow

```text
IDLE
  └─ submit_query / set_example
       └─ SUGGESTIONS
            └─ confirm_term
                 └─ EXPLAIN (modal)
                      ├─ ask_followup
                      ├─ request_consult → care_links (map search)
                      ├─ back_to_suggestions
                      └─ close_explain
```

## Components

| Layer | Responsibility |
|---|---|
| `frontend/app.py` | Render UI, dispatch events |
| `frontend/session_store.py` | Persist session in Streamlit state |
| `backend/container.py` | Shared config, cache, LLM, knowledge base |
| `backend/orchestrator/` | Route events, own workflow |
| `backend/agents/` | One capability per agent |
| `backend/services/` | Data access, care navigation, cache |
| `backend/models/` | Pydantic schemas |

## Agents

| Agent | File | Role |
|---|---|---|
| Intent recovery | `intent_recovery.py` | Fuzzy match user text to terms |
| LLM fallback | `llm_fallback.py` | OpenAI match when confidence is low |
| Explainer | `explainer.py` | Term explanation + expert context |
| Follow-up | `followup.py` | Question-specific guidance |
| Consult | `consult.py` | Capture user concern |
| Domain router | `domain_router.py` | Healthcare / legal / finance copy |

## Care navigation

After `request_consult`, the orchestrator attaches `care_links` to `ExplainView` using `backend/services/care_navigation.py`. Links are Google Maps searches — no provider API in MVP.

## LLM fallback

Enabled when `LLM_ENABLED=true` and top fuzzy confidence is below `INTENT_CONFIDENCE_THRESHOLD`. Wired in `AppContainer` and called from orchestrator `_submit_query`.

## Adding a new agent

1. Create `backend/agents/your_agent.py` with a single public function.
2. Add a `SessionEvent` in `backend/orchestrator/session.py` if needed.
3. Handle the event in `backend/orchestrator/orchestrator.py`.
4. Update UI in `frontend/components/` if user-facing.
5. Add tests in `tests/`.

## Maintenance notes

- Term data lives in `backend/data/terms.json` (include `followup_guidance` per question).
- Domain routing config lives in `backend/agents/domain_router.py`.
- Keep agents stateless; all session data stays in `SessionState`.
- Use `get_orchestrator()` from `backend/container.py` — do not instantiate `Orchestrator` in UI or API layers.

## Further reading

- [PRODUCT.md](./PRODUCT.md) — scope, roadmap, compliance
- [MVP_PLAN.md](./MVP_PLAN.md) — metrics and domain expansion
