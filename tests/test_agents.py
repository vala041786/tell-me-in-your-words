from backend.agents.explainer import explain_term
from backend.agents.followup import get_followup_guidance


def test_explain_term_includes_expert_context():
    result = explain_term("Shingles")
    assert result is not None
    assert result["term"] == "Shingles"
    assert result["expert_context"].domain == "healthcare"
    assert result["expert_context"].expert_type == "Healthcare professional"
    assert "painful rash" in result["explanation"]


def test_followup_guidance_for_known_question():
    symptoms = get_followup_guidance("Shingles", "What symptoms should I watch for?")
    contagious = get_followup_guidance("Shingles", "Is shingles contagious?")
    nda = get_followup_guidance("NDA", "When do I need an NDA?")

    assert symptoms is not None
    assert contagious is not None
    assert "burning, tingling" in symptoms
    assert "chickenpox" in contagious
    assert symptoms != contagious
    assert "CDC" in contagious
    assert "%28nda%29" in nda or "non-disclosure_agreement" in nda
    assert "](<https://" in nda
