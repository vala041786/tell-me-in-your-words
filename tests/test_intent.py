from backend.agents.intent_recovery import recover_intent

def test_fingles_matches_shingles():
    result = recover_intent("I have fingles")
    assert result[0]["term"] == "Shingles"


def test_fingles_only_shingles_above_display_threshold():
    from backend.container import AppContainer
    from backend.orchestrator import Orchestrator, SessionEvent, SessionState

    container = AppContainer.create()
    orchestrator = Orchestrator(container)
    state = orchestrator.handle(
        SessionState(),
        SessionEvent.SUBMIT_QUERY,
        {"query": "I think I have fingles"},
    )

    assert len(state.suggestions) == 1
    assert state.suggestions[0].term == "Shingles"
    assert state.suggestions[0].confidence >= 0.80


def test_company_baskets_matches_etf():
    result = recover_intent("company baskets")
    assert result[0]["term"] == "ETF"
