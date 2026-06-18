from typing import Optional

from backend.agents.domain_router import get_expert_context
from backend.services.knowledge_base import KnowledgeBase, get_term


def submit_consult(
    term: str,
    concern: str,
    knowledge_base: Optional[KnowledgeBase] = None,
) -> dict:
    item = get_term(term, knowledge_base)
    if not item:
        return {"success": False, "message": "Term not found."}

    context = get_expert_context(item["domain"])
    if not concern.strip():
        return {"success": False, "message": "Please describe your concern before continuing."}

    return {
        "success": True,
        "term": item["term"],
        "domain": item["domain"],
        "concern": concern.strip(),
        "message": context["consult_success"],
    }
