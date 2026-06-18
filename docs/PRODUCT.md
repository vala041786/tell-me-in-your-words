# Tell Me In Your Words — Product Documentation

## Executive summary

**Tell Me In Your Words** helps people describe problems in everyday language, recover the expert term they likely mean, confirm it, and route them to trusted educational context plus practical next steps.

The current release is an **MVP**: intent recovery, explanation, follow-up guidance, and lightweight care navigation via map-search links. It does **not** diagnose, give personalized medical/legal/financial advice, or book appointments with providers.

**Tagline:** *You don't need the right words.*

---

## Problem statement

Users often know their symptom, goal, or concern but not the expert vocabulary (e.g. “fingles” → Shingles, “company baskets” → ETF). Search and chat tools assume the user already has the right term. This product inverts that: **recover intent first**, then explain and route.

---

## Target users

| Segment | Example need |
|---|---|
| Healthcare consumers | Describe symptoms without medical jargon |
| Legal / business newcomers | Name documents and structures correctly |
| Personal finance learners | Understand investment and retirement terms |
| Multilingual users | Express concerns in everyday or non-English phrasing |

---

## MVP scope (what ships today)

### In scope

| Capability | Implementation |
|---|---|
| Intent recovery | Local fuzzy matching (`rapidfuzz`) over curated `terms.json` aliases |
| Confidence filtering | Suggestions shown only at ≥ 80% confidence (`SUGGESTION_CONFIDENCE_THRESHOLD`) |
| LLM fallback | Optional OpenAI fallback when fuzzy confidence is low (`LLM_ENABLED`) |
| Term confirmation | User picks the closest match before explanation |
| Expert explanation | Curated definitions + domain routing (healthcare, legal, finance) |
| Follow-up Q&A | Per-question guidance from `followup_guidance` in `terms.json` |
| Consult capture | Stores user concern in session; shows domain-specific success message |
| Care navigation (quick win) | Google Maps search links after consult submit (no provider API) |
| Dual interface | Streamlit UI + FastAPI event API |
| Shared runtime | `AppContainer` singleton (config, cache, LLM client, knowledge base) |

### Out of scope (MVP)

- Real-time provider matching, availability, or booking
- User accounts, persistence across devices, or PHI storage
- Diagnosis, treatment plans, legal advice, or investment recommendations
- HIPAA-compliant data handling (required for full healthcare product)
- Payment, insurance, or telehealth video sessions

---

## User flow

```text
1. User describes problem in own words
2. App suggests high-confidence expert terms
3. User confirms term → Explain modal opens
4. User reads explanation + trusted source link
5. Optional: tap follow-up question → specific guidance
6. Optional: submit concern → success message + “Find care near you” links
```

---

## Architecture

```text
Streamlit UI / FastAPI
        ↓
   AppContainer (singleton)
        ↓
   Orchestrator (event router)
        ↓
   Agents (stateless)
        ↓
   Services (knowledge base, cache, care navigation, LLM)
```

### Session events

| Event | Action |
|---|---|
| `submit_query` | Intent recovery (+ optional LLM fallback) |
| `confirm_term` | Explain term + open modal |
| `ask_followup` | Question-specific guidance |
| `request_consult` | Capture concern + attach care links |
| `back_to_suggestions` / `close_explain` | Return to matches or idle |

See [ARCHITECTURE.md](./ARCHITECTURE.md) for developer handover.

---

## Tech stack

| Layer | Choice |
|---|---|
| UI | Streamlit 1.41 |
| API | FastAPI + Uvicorn |
| Matching | RapidFuzz 3.14 |
| Models | Pydantic 2.x |
| LLM (optional) | OpenAI Chat Completions via stdlib HTTP client |
| Data | Curated JSON (`backend/data/terms.json`) |
| Tests | pytest |

**Python:** 3.13 recommended (3.14 has package compatibility issues with some pins).

---

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `LLM_ENABLED` | `false` | Enable OpenAI intent fallback |
| `OPENAI_API_KEY` | — | Required when LLM enabled |
| `LLM_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `INTENT_CONFIDENCE_THRESHOLD` | `0.75` | When to call LLM fallback |
| `SUGGESTION_CONFIDENCE_THRESHOLD` | `0.80` | Minimum score to show a suggestion |
| `CACHE_TTL_SECONDS` | unset | In-memory cache TTL for terms |

---

## Running the project

```bash
# One-time setup
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run UI from anywhere (after install-alias)
tmiyw

# Or directly
streamlit run frontend/app.py

# API mode
uvicorn backend.main:app --reload
```

---

## Core metric

**Intent Recovery Rate (IRR):** % of sessions where the user confirms “yes, that is what I meant” on the first or second suggestion.

Track via session events in a future analytics layer.

---

## Data model

- **Terms** — `term`, `domain`, `aliases`, `definition`, `source_*`, `followups`, `followup_guidance`
- **Session** — `user_query`, `suggestions`, `explain_view`, step enum
- **ExplainView** — explanation, follow-ups, consult state, `care_links`

---

## Care navigation (MVP quick win)

After consult submit, the app shows **map search links** (Google Maps) such as:

- Healthcare: urgent care, primary care, pharmacies, term-specific specialist search
- Legal: attorneys, legal aid
- Finance: financial planners, tax professionals

**Important:** Links open external search results. The app does not verify providers, ratings, insurance, or availability.

Implementation: `backend/services/care_navigation.py`

---

## Testing

```bash
pytest tests/ -q
```

Covers orchestrator flow, intent recovery, follow-up guidance, LLM fallback, container singleton, and care navigation links.

---

## Roadmap: MVP → full product

### Phase 1 — MVP hardening (current → 4 weeks)

- [x] Orchestrator + agents architecture
- [x] LLM fallback for low-confidence queries
- [x] Per-question follow-up guidance
- [x] Map-search care links after consult
- [ ] Analytics event logging (IRR, drop-off by step)
- [ ] Expand `terms.json` (more domains from MVP_PLAN)
- [ ] Zip code input to improve map search context

### Phase 2 — Provider discovery (4–8 weeks)

- [ ] Integrate provider directory API (e.g. Google Places, Zocdoc, Healthgrades)
- [ ] Filter by domain/term → provider type (urgent care vs specialist)
- [ ] Display name, address, phone, hours (read-only)
- [ ] “Call” / “Get directions” deep links
- [ ] User location consent flow + privacy notice

### Phase 3 — Accounts & persistence (8–12 weeks)

- [ ] Auth (email/OAuth)
- [ ] Save session history and concerns (encrypted at rest)
- [ ] Resume incomplete flows across devices
- [ ] Admin UI for term dictionary curation

### Phase 4 — Expert handoff (12–20 weeks)

- [ ] Telehealth partner integration (API or referral URL with context)
- [ ] Appointment request form → partner queue (not in-app diagnosis)
- [ ] Legal/finance referral partners (attorney networks, fiduciary platforms)
- [ ] SLA and escalation for urgent healthcare keywords

### Phase 5 — Compliance & enterprise (20+ weeks)

- [ ] HIPAA risk assessment and BAA with infrastructure vendors
- [ ] SOC 2 / security audit if storing health-related concerns
- [ ] Jurisdiction-specific legal disclaimers
- [ ] FINRA-aware flows for investment terms
- [ ] Multi-tenant deployment for clinics, legal aid, or employers

---

## Compliance notes

| Domain | MVP stance | Full product requirement |
|---|---|---|
| Healthcare | Educational only; no diagnosis | HIPAA, clinician oversight, triage protocols |
| Legal | General information; not legal advice | State bar rules, attorney referral compliance |
| Finance | Educational only; not investment advice | SEC/FINRA marketing and advice rules |

Always show safety disclaimers. Never present map links as endorsements.

---

## Repository map

```text
backend/
  agents/          # intent, explain, followup, consult, llm_fallback
  orchestrator/    # session state + event routing
  services/        # knowledge base, cache, care navigation, LLM
  container.py     # shared AppContainer singleton
  config.py        # environment-driven settings
frontend/
  app.py           # main Streamlit UI
  components/      # explain dialog
docs/
  PRODUCT.md       # this document
  ARCHITECTURE.md  # technical handover
  MVP_PLAN.md      # metrics and domain expansion list
```

---

## Product principle

The AI should not say “you are wrong.” It should say:

> **“You might mean this. Is that what you were looking for?”**

---

## Contact & next steps for contributors

1. Read [ARCHITECTURE.md](./ARCHITECTURE.md) before adding agents or events.
2. Add terms and `followup_guidance` in `backend/data/terms.json`.
3. Run `pytest` before opening a PR.
4. For provider APIs, start with a spike in `backend/services/` behind a feature flag.
