from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from backend.models.api import ExpertContext, Suggestion


class CareLink(BaseModel):
    label: str
    url: str


class SessionStep(str, Enum):
    IDLE = "idle"
    SUGGESTIONS = "suggestions"
    EXPLAIN = "explain"


class SessionEvent(str, Enum):
    SUBMIT_QUERY = "submit_query"
    SET_EXAMPLE = "set_example"
    CONFIRM_TERM = "confirm_term"
    ASK_FOLLOWUP = "ask_followup"
    REQUEST_CONSULT = "request_consult"
    BACK_TO_SUGGESTIONS = "back_to_suggestions"
    CLOSE_EXPLAIN = "close_explain"


class ExplainView(BaseModel):
    term: str
    domain: str
    explanation: str
    source_name: str
    source_url: str
    followups: List[str]
    expert_context: ExpertContext
    safety_note: str
    followup_guidance: Optional[str] = None
    selected_followup: Optional[str] = None
    consult_submitted: bool = False
    consult_concern: Optional[str] = None
    care_links: List[CareLink] = Field(default_factory=list)


class SessionState(BaseModel):
    session_id: str = "default"
    step: SessionStep = SessionStep.IDLE
    user_query: str = ""
    suggestions: List[Suggestion] = Field(default_factory=list)
    message: str = ""
    show_explain_modal: bool = False
    explain_view: Optional[ExplainView] = None

    @property
    def has_suggestions(self) -> bool:
        return bool(self.suggestions)
