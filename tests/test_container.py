from backend.container import AppContainer, get_container, get_orchestrator, reset_container
from backend.services.knowledge_base import TERMS_CACHE_KEY


def test_get_orchestrator_returns_shared_instance():
    reset_container()
    first = get_orchestrator()
    second = get_orchestrator()
    assert first is second


def test_terms_are_cached_in_shared_container():
    reset_container()
    container = get_container()
    kb = container.knowledge_base

    first_load = kb.load_terms()
    mtime_key = f"{TERMS_CACHE_KEY}:{kb._data_path.stat().st_mtime}"
    assert container.cache.get(mtime_key) is first_load

    second_load = kb.load_terms()
    assert second_load is first_load


def test_isolated_containers_have_separate_caches():
    container_a = AppContainer.create()
    container_b = AppContainer.create()

    assert container_a.cache is not container_b.cache
    container_a.knowledge_base.load_terms()
    container_b.knowledge_base.load_terms()
    container_a.cache.clear()

    b_key = f"{TERMS_CACHE_KEY}:{container_b.knowledge_base._data_path.stat().st_mtime}"
    assert container_a.cache.get(b_key) is None
    assert container_b.cache.get(b_key) is not None
