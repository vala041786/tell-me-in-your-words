from backend.container import AppContainer, reset_container
from backend.orchestrator import Orchestrator, SessionEvent, SessionState, SessionStep


def _orchestrator() -> Orchestrator:
    return AppContainer.create().orchestrator


def test_submit_query_finds_shingles():
    reset_container()
    orchestrator = _orchestrator()
    state = orchestrator.handle(
        SessionState(),
        SessionEvent.SUBMIT_QUERY,
        {"query": "I have fingles"},
    )
    assert state.step == SessionStep.SUGGESTIONS
    assert state.suggestions[0].term == "Shingles"


def test_confirm_term_opens_explain_view():
    reset_container()
    orchestrator = _orchestrator()
    state = orchestrator.handle(
        SessionState(),
        SessionEvent.SUBMIT_QUERY,
        {"query": "I have fingles"},
    )
    state = orchestrator.handle(state, SessionEvent.CONFIRM_TERM, {"term": "Shingles"})
    assert state.step == SessionStep.EXPLAIN
    assert state.show_explain_modal is True
    assert state.explain_view.term == "Shingles"
    assert state.explain_view.expert_context.domain == "healthcare"


def test_request_consult_captures_concern():
    reset_container()
    orchestrator = _orchestrator()
    state = orchestrator.handle(SessionState(), SessionEvent.CONFIRM_TERM, {"term": "Shingles"})
    state = orchestrator.handle(
        state,
        SessionEvent.REQUEST_CONSULT,
        {"concern": "Painful rash for 3 days"},
    )
    assert state.explain_view.consult_submitted is True
    assert state.explain_view.consult_concern == "Painful rash for 3 days"


def test_back_to_suggestions_closes_explain():
    reset_container()
    orchestrator = _orchestrator()
    state = orchestrator.handle(
        SessionState(),
        SessionEvent.SUBMIT_QUERY,
        {"query": "I have fingles"},
    )
    state = orchestrator.handle(state, SessionEvent.CONFIRM_TERM, {"term": "Shingles"})
    state = orchestrator.handle(state, SessionEvent.BACK_TO_SUGGESTIONS)
    assert state.step == SessionStep.SUGGESTIONS
    assert state.show_explain_modal is False
    assert state.explain_view is None
