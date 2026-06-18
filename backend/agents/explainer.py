from typing import Optional

from backend.agents.domain_router import get_expert_context
from backend.models.api import ExpertContext
from backend.services.knowledge_base import KnowledgeBase, get_term


def explain_term(
    term: str,
    knowledge_base: Optional[KnowledgeBase] = None,
) -> Optional[dict]:
    item = get_term(term, knowledge_base)
    if not item:
        return None

    context = get_expert_context(item["domain"])
    explanation = (
        f"**What it means:** {item['definition']}\n\n"
        f"**Why it matters:** Knowing this term helps us route you to the right "
        f"{item['domain']} expert context so you can ask follow-up questions in your own words."
    )
    return {
        **item,
        "explanation": explanation,
        "expert_context": ExpertContext(**context),
        "safety_note": context["safety_note"],
    }
