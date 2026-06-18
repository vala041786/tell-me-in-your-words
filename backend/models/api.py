from typing import List, Optional

from pydantic import BaseModel


class Suggestion(BaseModel):
    term: str
    domain: str
    confidence: float
    matched_alias: str
    definition: str
    source_name: str
    source_url: str
    followups: List[str]


class ExpertContext(BaseModel):
    domain: str
    expert_type: str
    icon: str
    routing_message: str
    next_steps: List[str]
    resource_label: str
    safety_note: str
    consult_label: str
    consult_prompt: str
    consult_cta: str
    consult_success: str


class RecoverRequest(BaseModel):
    text: str
    language_hint: Optional[str] = None


class RecoverResponse(BaseModel):
    original_text: str
    suggestions: List[Suggestion]
    message: str


class ExplainRequest(BaseModel):
    term: str


class ExplainResponse(BaseModel):
    term: str
    domain: str
    explanation: str
    source_name: str
    source_url: str
    followups: List[str]
    expert_context: ExpertContext
    safety_note: str


class SessionNextRequest(BaseModel):
    session_id: str = "default"
    event: str
    payload: dict = {}


class SessionNextResponse(BaseModel):
    session: dict
    next_actions: List[str]
