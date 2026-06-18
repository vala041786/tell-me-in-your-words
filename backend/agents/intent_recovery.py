from typing import Optional

from rapidfuzz import fuzz

from backend.services.knowledge_base import KnowledgeBase, load_terms


def recover_intent(
    user_text: str,
    limit: int = 4,
    knowledge_base: Optional[KnowledgeBase] = None,
):
    text = (user_text or "").strip().lower()
    if not text:
        return []

    results = []
    for item in load_terms(knowledge_base):
        candidates = [item["term"]] + item.get("aliases", [])
        best_score = 0
        best_alias = item["term"]

        for alias in candidates:
            alias_l = alias.lower()
            scores = [
                fuzz.WRatio(text, alias_l),
                fuzz.partial_ratio(text, alias_l),
                fuzz.token_set_ratio(text, alias_l),
            ]
            score = max(scores)
            if alias_l in text or text in alias_l:
                score = max(score, 96)
            if score > best_score:
                best_score = score
                best_alias = alias

        if best_score >= 45:
            results.append({
                **item,
                "confidence": round(best_score / 100, 2),
                "matched_alias": best_alias,
            })

    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:limit]
