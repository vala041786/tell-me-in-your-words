import json
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from backend.services.cache import InMemoryCache

if TYPE_CHECKING:
    from backend.container import AppContainer

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "terms.json"
TERMS_CACHE_KEY = "terms"


class KnowledgeBase:
    def __init__(
        self,
        cache: InMemoryCache,
        data_path: Path = DATA_PATH,
    ) -> None:
        self._cache = cache
        self._data_path = data_path

    def load_terms(self) -> list:
        cache_key = f"{TERMS_CACHE_KEY}:{self._data_path.stat().st_mtime}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        with self._data_path.open("r", encoding="utf-8") as f:
            terms = json.load(f)
        self._cache.set(cache_key, terms)
        return terms

    def get_term(self, term_name: str) -> dict | None:
        wanted = term_name.strip().lower()
        for item in self.load_terms():
            if item["term"].lower() == wanted:
                return item
        return None


def _default_knowledge_base() -> KnowledgeBase:
    from backend.container import get_container

    return get_container().knowledge_base


def load_terms(knowledge_base: Optional[KnowledgeBase] = None) -> list:
    kb = knowledge_base or _default_knowledge_base()
    return kb.load_terms()


def get_term(term_name: str, knowledge_base: Optional[KnowledgeBase] = None) -> dict | None:
    kb = knowledge_base or _default_knowledge_base()
    return kb.get_term(term_name)
