# MVP Plan

> Full product documentation: [PRODUCT.md](./PRODUCT.md)

## Core metric

**Intent Recovery Rate (IRR):** percent of sessions where the user confirms “yes, that is what I meant.”

## Current MVP status

| Area | Status |
|---|---|
| Local fuzzy intent recovery | Done |
| Suggestion confidence filter (≥ 80%) | Done |
| Optional LLM fallback | Done |
| Explain + domain routing | Done |
| Per-question follow-up guidance | Done |
| Consult capture + map-search care links | Done |
| Streamlit UI + FastAPI | Done |
| Provider API / booking | Not started |

## Build order (original)

1. ~~Local intent recovery with aliases~~
2. ~~Confirmation UI~~
3. ~~Expert explanation from curated data~~
4. ~~LLM fallback for low-confidence cases~~
5. Add multilingual examples and more aliases
6. Zip-aware care search links
7. Provider directory API integration

## Next domains to add to `terms.json`

Immigration, Tax, Real Estate, Product Management, Software Engineering, Automotive.

## Next engineering priorities

1. Analytics events for IRR measurement
2. Zip code field after consult submit for better map results
3. Provider directory spike (Google Places or health API)
4. Session persistence and user accounts

See [PRODUCT.md](./PRODUCT.md) for the full roadmap to a production-ready product.
