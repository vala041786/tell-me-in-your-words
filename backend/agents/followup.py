from typing import Optional

from backend.agents.domain_router import get_expert_context
from backend.services.knowledge_base import KnowledgeBase, get_term


def get_followup_guidance(
    term: str,
    question: str,
    knowledge_base: Optional[KnowledgeBase] = None,
) -> Optional[str]:
    item = get_term(term, knowledge_base)
    if not item or question not in item.get("followups", []):
        return None

    context = get_expert_context(item["domain"])
    guidance_map = item.get("followup_guidance", {})
    answer = guidance_map.get(question)

    if not answer:
        answer = (
            f"This is a useful follow-up to explore with a {context['expert_type'].lower()} "
            f"when you are ready to go deeper on **{item['term']}**."
        )

    source_url = item["source_url"]
    return (
        f"**Your follow-up:** {question}\n\n"
        f"{answer}\n\n"
        f"**Helpful resource:** [{item['source_name']}](<{source_url}>)\n\n"
        f"**Reminder:** {context['safety_note']}"
    )
