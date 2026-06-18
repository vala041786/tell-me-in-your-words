from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from backend.config import AppConfig
from backend.services.cache import InMemoryCache
from backend.services.knowledge_base import KnowledgeBase
from backend.services.llm_client import LLMClient, NullLLMClient, OpenAILLMClient

if TYPE_CHECKING:
    from backend.orchestrator.orchestrator import Orchestrator

_container: Optional["AppContainer"] = None


@dataclass
class AppContainer:
    """Shared runtime dependencies for API, UI, and orchestrator."""

    config: AppConfig
    cache: InMemoryCache
    llm_client: LLMClient
    knowledge_base: KnowledgeBase
    _orchestrator: Optional["Orchestrator"] = field(default=None, repr=False, init=False)

    @classmethod
    def create(cls, config: AppConfig | None = None) -> "AppContainer":
        config = config or AppConfig.from_env()
        cache = InMemoryCache(default_ttl=config.cache_ttl_seconds)
        return cls(
            config=config,
            cache=cache,
            llm_client=cls._build_llm_client(config),
            knowledge_base=KnowledgeBase(cache=cache),
        )

    @staticmethod
    def _build_llm_client(config: AppConfig) -> LLMClient:
        if not config.llm_enabled:
            return NullLLMClient()
        if not config.openai_api_key:
            raise ValueError("LLM_ENABLED=true requires OPENAI_API_KEY")
        return OpenAILLMClient(
            api_key=config.openai_api_key,
            model=config.llm_model,
        )

    @property
    def orchestrator(self) -> "Orchestrator":
        if self._orchestrator is None:
            from backend.orchestrator.orchestrator import Orchestrator

            self._orchestrator = Orchestrator(self)
        return self._orchestrator


def get_container(config: AppConfig | None = None) -> AppContainer:
    global _container
    if _container is None:
        _container = AppContainer.create(config)
    return _container


def get_orchestrator() -> "Orchestrator":
    return get_container().orchestrator


def reset_container() -> None:
    """Clear the process singleton. Useful in tests."""
    global _container
    _container = None
