SAFETY_NOTES = {
    "healthcare": (
        "This is educational information, not a medical diagnosis. "
        "For urgent symptoms or personal medical advice, contact a licensed clinician."
    ),
    "legal": (
        "This is general legal information, not legal advice. "
        "For decisions or documents, consult a qualified attorney in your jurisdiction."
    ),
    "finance": (
        "This is educational information, not financial advice. "
        "Consider your goals, risk tolerance, and a qualified advisor before investing."
    ),
}

DOMAIN_CONFIG = {
    "healthcare": {
        "expert_type": "Healthcare professional",
        "icon": "🩺",
        "routing_message": (
            "Your question fits a healthcare context. Use the trusted source below for general education, "
            "and talk to a clinician for personal symptoms, diagnosis, or treatment."
        ),
        "next_steps": [
            "Review symptoms and timing using the trusted source below",
            "Write down questions for your next doctor visit",
            "Seek urgent care if symptoms are severe or getting worse",
        ],
        "resource_label": "Trusted health source",
        "consult_label": "Consult a healthcare expert",
        "consult_prompt": (
            "Describe your symptoms or concern in your own words. "
            "We'll route you toward the right type of healthcare guidance."
        ),
        "consult_cta": "Continue to healthcare expert consult",
        "consult_success": (
            "Your concern has been captured. Next, speak with a licensed clinician, "
            "your primary care provider, or urgent care if symptoms are severe."
        ),
    },
    "legal": {
        "expert_type": "Qualified attorney",
        "icon": "⚖️",
        "routing_message": (
            "Your question fits a legal context. Use the trusted source below for general concepts, "
            "and consult an attorney before signing documents or making legal decisions."
        ),
        "next_steps": [
            "Read the overview on the trusted legal source below",
            "Gather relevant documents or contracts before speaking to counsel",
            "Avoid acting on general information alone for time-sensitive matters",
        ],
        "resource_label": "Trusted legal source",
        "consult_label": "Consult a legal expert",
        "consult_prompt": "Describe your legal question in your own words.",
        "consult_cta": "Continue to legal expert consult",
        "consult_success": (
            "Your question has been captured. Next, consult a qualified attorney in your jurisdiction "
            "before signing documents or making legal decisions."
        ),
    },
    "finance": {
        "expert_type": "Financial advisor or planner",
        "icon": "📈",
        "routing_message": (
            "Your question fits a finance context. Use the trusted source below for educational basics, "
            "and consider a qualified advisor for decisions tied to your goals and risk tolerance."
        ),
        "next_steps": [
            "Review definitions and examples on the trusted finance source below",
            "Clarify your goals, timeline, and risk tolerance before investing",
            "Compare fees and options before committing money",
        ],
        "resource_label": "Trusted finance source",
        "consult_label": "Consult a finance expert",
        "consult_prompt": "Describe your financial question or goal in your own words.",
        "consult_cta": "Continue to finance expert consult",
        "consult_success": (
            "Your question has been captured. Next, review your goals with a qualified financial advisor "
            "before making investment or tax decisions."
        ),
    },
}

DEFAULT_DOMAIN_CONFIG = {
    "expert_type": "Subject-matter expert",
    "icon": "💬",
    "routing_message": "Use the trusted source below for general education on this topic.",
    "next_steps": [
        "Review the trusted source below",
        "Ask follow-up questions in your own words",
    ],
    "resource_label": "Trusted source",
    "consult_label": "Consult an expert",
    "consult_prompt": "Describe what you would like help with.",
    "consult_cta": "Continue to expert consult",
    "consult_success": "Your question has been captured. Next, speak with a subject-matter expert.",
}


def get_expert_context(domain: str) -> dict:
    config = DOMAIN_CONFIG.get(domain, DEFAULT_DOMAIN_CONFIG)
    return {
        **config,
        "domain": domain,
        "safety_note": SAFETY_NOTES.get(domain, "This is general educational information."),
    }
