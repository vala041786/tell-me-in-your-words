from typing import TYPE_CHECKING, Any, Dict, List, Optional

from backend.services.care_navigation import get_care_links
from backend.agents.consult import submit_consult
from backend.agents.explainer import explain_term
from backend.agents.followup import get_followup_guidance
from backend.agents.intent_recovery import recover_intent
from backend.agents.llm_fallback import recover_intent_with_llm
from backend.models.api import Suggestion
from backend.orchestrator.session import CareLink, ExplainView, SessionEvent, SessionState, SessionStep

if TYPE_CHECKING:
    from backend.container import AppContainer


class Orchestrator:
    """Routes session events to specialist agents and returns updated session state."""

    _NEXT_ACTIONS = {
        SessionStep.IDLE: ["submit_query", "set_example"],
        SessionStep.SUGGESTIONS: ["confirm_term", "submit_query", "set_example"],
        SessionStep.EXPLAIN: [
            "ask_followup",
            "request_consult",
            "back_to_suggestions",
            "close_explain",
        ],
    }

    def __init__(self, container: "AppContainer") -> None:
        self._container = container

    @property
    def _kb(self):
        return self._container.knowledge_base

    def handle(
        self,
        state: SessionState,
        event: SessionEvent,
        payload: Optional[Dict[str, Any]] = None,
    ) -> SessionState:
        payload = payload or {}
        handlers = {
            SessionEvent.SUBMIT_QUERY: self._submit_query,
            SessionEvent.SET_EXAMPLE: self._set_example,
            SessionEvent.CONFIRM_TERM: self._confirm_term,
            SessionEvent.ASK_FOLLOWUP: self._ask_followup,
            SessionEvent.REQUEST_CONSULT: self._request_consult,
            SessionEvent.BACK_TO_SUGGESTIONS: self._back_to_suggestions,
            SessionEvent.CLOSE_EXPLAIN: self._close_explain,
        }
        handler = handlers.get(event)
        if handler is None:
            return state
        return handler(state, payload)

    def next_actions(self, state: SessionState) -> List[str]:
        return self._NEXT_ACTIONS.get(state.step, [])

    def _submit_query(self, state: SessionState, payload: Dict[str, Any]) -> SessionState:
        query = (payload.get("query") or "").strip()
        state.user_query = query
        state.explain_view = None
        state.show_explain_modal = False

        if not query:
            state.step = SessionStep.IDLE
            state.suggestions = []
            state.message = ""
            return state

        raw = recover_intent(query, knowledge_base=self._kb)
        max_confidence = raw[0]["confidence"] if raw else 0.0
        if self._should_use_llm_fallback(max_confidence):
            llm_results = recover_intent_with_llm(
                query,
                self._container.llm_client,
                self._kb,
            )
            if llm_results:
                raw = llm_results

        threshold = self._container.config.suggestion_confidence_threshold
        strong_matches = [item for item in raw if item["confidence"] >= threshold]
        if strong_matches:
            raw = strong_matches

        state.suggestions = [Suggestion(**item) for item in raw]
        state.step = SessionStep.SUGGESTIONS
        state.message = (
            "You might mean one of these. Which sounds closest?"
            if state.suggestions
            else "I could not find a close match yet. Try describing it another way."
        )
        return state

    def _should_use_llm_fallback(self, max_confidence: float) -> bool:
        config = self._container.config
        return (
            config.llm_enabled
            and max_confidence < config.intent_confidence_threshold
        )

    def _set_example(self, state: SessionState, payload: Dict[str, Any]) -> SessionState:
        return self._submit_query(state, payload)

    def _confirm_term(self, state: SessionState, payload: Dict[str, Any]) -> SessionState:
        term = (payload.get("term") or "").strip()
        explained = explain_term(term, knowledge_base=self._kb)
        if not explained:
            state.message = "We could not load an explanation for that term."
            return state

        state.explain_view = ExplainView(
            term=explained["term"],
            domain=explained["domain"],
            explanation=explained["explanation"],
            source_name=explained["source_name"],
            source_url=explained["source_url"],
            followups=explained.get("followups", []),
            expert_context=explained["expert_context"],
            safety_note=explained["safety_note"],
        )
        state.step = SessionStep.EXPLAIN
        state.show_explain_modal = True
        state.message = f"Explaining {explained['term']} and routing to expert context."
        return state

    def _ask_followup(self, state: SessionState, payload: Dict[str, Any]) -> SessionState:
        if not state.explain_view:
            return state

        question = (payload.get("question") or "").strip()
        guidance = get_followup_guidance(
            state.explain_view.term,
            question,
            knowledge_base=self._kb,
        )
        if guidance:
            state.explain_view.followup_guidance = guidance
            state.explain_view.selected_followup = question
        return state

    def _request_consult(self, state: SessionState, payload: Dict[str, Any]) -> SessionState:
        if not state.explain_view:
            return state

        concern = (payload.get("concern") or state.user_query or "").strip()
        result = submit_consult(
            state.explain_view.term,
            concern,
            knowledge_base=self._kb,
        )
        if result["success"]:
            state.explain_view.consult_submitted = True
            state.explain_view.consult_concern = result["concern"]
            state.explain_view.care_links = [
                CareLink(**link)
                for link in get_care_links(state.explain_view.domain, state.explain_view.term)
            ]
            state.message = result["message"]
        else:
            state.message = result["message"]
        return state

    def _back_to_suggestions(self, state: SessionState, payload: Dict[str, Any]) -> SessionState:
        state.explain_view = None
        state.show_explain_modal = False
        state.step = SessionStep.SUGGESTIONS if state.user_query else SessionStep.IDLE
        return state

    def _close_explain(self, state: SessionState, payload: Dict[str, Any]) -> SessionState:
        return self._back_to_suggestions(state, payload)
