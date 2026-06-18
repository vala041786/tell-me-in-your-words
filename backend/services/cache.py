import time
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class _CacheEntry:
    value: Any
    expires_at: Optional[float]


class InMemoryCache:
    """Process-local cache shared across API and UI entry points."""

    def __init__(self, default_ttl: Optional[int] = None) -> None:
        self._default_ttl = default_ttl
        self._store: dict[str, _CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expires_at is not None and time.time() >= entry.expires_at:
            del self._store[key]
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        effective_ttl = self._default_ttl if ttl is None else ttl
        expires_at = time.time() + effective_ttl if effective_ttl is not None else None
        self._store[key] = _CacheEntry(value=value, expires_at=expires_at)

    def clear(self) -> None:
        self._store.clear()
