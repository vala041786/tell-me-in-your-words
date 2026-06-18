from backend.agents.llm_fallback import recover_intent_with_llm
from backend.config import AppConfig
from backend.container import AppContainer
from backend.orchestrator import Orchestrator, SessionEvent, SessionState
from backend.services.cache import InMemoryCache
from backend.services.knowledge_base import KnowledgeBase


class FakeLLMClient:
    def __init__(self, response: str) -> None:
        self._response = response
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._response


def _container_with_llm(response: str, threshold: float = 0.75) -> AppContainer:
    config = AppConfig(
        llm_enabled=True,
        openai_api_key="test-key",
        intent_confidence_threshold=threshold,
    )
    cache = InMemoryCache()
    return AppContainer(
        config=config,
        cache=cache,
        llm_client=FakeLLMClient(response),
        knowledge_base=KnowledgeBase(cache=cache),
    )


def test_recover_intent_with_llm_maps_catalog_terms():
    client = FakeLLMClient(
        '[{"term": "Migraine", "confidence": 0.82, "matched_alias": "bad headache"}]'
    )
    kb = KnowledgeBase(cache=InMemoryCache())

    results = recover_intent_with_llm("splitting headache", client, kb)

    assert len(results) == 1
    assert results[0]["term"] == "Migraine"
    assert results[0]["confidence"] == 0.82
    assert results[0]["matched_alias"] == "bad headache"


def test_recover_intent_with_llm_ignores_unknown_terms():
    client = FakeLLMClient('[{"term": "Not In Catalog", "confidence": 0.9}]')
    kb = KnowledgeBase(cache=InMemoryCache())

    results = recover_intent_with_llm("mystery symptom", client, kb)

    assert results == []


def test_orchestrator_uses_llm_when_confidence_below_threshold():
    container = _container_with_llm(
        '[{"term": "Migraine", "confidence": 0.88, "matched_alias": "head hurts"}]',
        threshold=0.95,
    )
    orchestrator = Orchestrator(container)

    state = orchestrator.handle(
        SessionState(),
        SessionEvent.SUBMIT_QUERY,
        {"query": "my head hurts badly"},
    )

    assert state.suggestions[0].term == "Migraine"
    assert state.suggestions[0].confidence == 0.88
    assert len(container.llm_client.prompts) == 1


def test_orchestrator_skips_llm_when_fuzzy_confidence_is_high():
    container = _container_with_llm(
        '[{"term": "Migraine", "confidence": 0.99, "matched_alias": "ignored"}]',
        threshold=0.75,
    )
    orchestrator = Orchestrator(container)

    state = orchestrator.handle(
        SessionState(),
        SessionEvent.SUBMIT_QUERY,
        {"query": "I have fingles"},
    )

    assert state.suggestions[0].term == "Shingles"
    assert container.llm_client.prompts == []


def test_container_requires_api_key_when_llm_enabled():
    config = AppConfig(llm_enabled=True, openai_api_key=None)

    try:
        AppContainer.create(config)
        raised = False
    except ValueError:
        raised = True

    assert raised
