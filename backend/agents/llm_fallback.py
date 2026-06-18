import json
import re
from typing import Any, Optional

from backend.services.knowledge_base import KnowledgeBase
from backend.services.llm_client import LLMClient

_JSON_ARRAY_RE = re.compile(r"\[[\s\S]*\]")


def recover_intent_with_llm(
    user_text: str,
    llm_client: LLMClient,
    knowledge_base: KnowledgeBase,
    limit: int = 4,
) -> list[dict[str, Any]]:
    text = (user_text or "").strip()
    if not text:
        return []

    terms = knowledge_base.load_terms()
    term_by_name = {item["term"].lower(): item for item in terms}
    catalog = [
        {
            "term": item["term"],
            "domain": item["domain"],
            "aliases": item.get("aliases", []),
            "definition": item["definition"],
        }
        for item in terms
    ]

    prompt = f"""You help match everyday language to expert terms from a fixed catalog.

User query:
{text}

Catalog (only choose terms from this list):
{json.dumps(catalog, ensure_ascii=False)}

Return a JSON array with up to {limit} best matches, sorted by relevance.
Each item must use this shape:
{{"term": "<exact catalog term>", "confidence": <0.0-1.0>, "matched_alias": "<phrase from the user query or catalog that explains the match>"}}

Rules:
- Only include terms that appear in the catalog.
- confidence must be between 0 and 1.
- If nothing is a reasonable match, return [].
- Return JSON only, no markdown or commentary.
"""

    try:
        raw_response = llm_client.complete(prompt)
    except Exception:
        return []

    parsed = _parse_llm_matches(raw_response)
    results: list[dict[str, Any]] = []
    for match in parsed[:limit]:
        term_name = str(match.get("term", "")).strip()
        item = term_by_name.get(term_name.lower())
        if item is None:
            continue

        confidence = _clamp_confidence(match.get("confidence", 0.5))
        matched_alias = str(match.get("matched_alias") or text).strip() or text
        results.append({
            **item,
            "confidence": confidence,
            "matched_alias": matched_alias,
        })

    return results


def _parse_llm_matches(raw_response: str) -> list[dict[str, Any]]:
    text = raw_response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = _JSON_ARRAY_RE.search(text)
        if match is None:
            return []
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            return []

    if not isinstance(payload, list):
        return []

    return [item for item in payload if isinstance(item, dict)]


def _clamp_confidence(value: Any) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        confidence = 0.5
    return round(max(0.0, min(confidence, 1.0)), 2)
