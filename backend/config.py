import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    llm_enabled: bool = False
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    intent_confidence_threshold: float = 0.75
    suggestion_confidence_threshold: float = 0.80
    cache_ttl_seconds: int | None = None

    @classmethod
    def from_env(cls) -> "AppConfig":
        ttl_raw = os.getenv("CACHE_TTL_SECONDS")
        api_key = os.getenv("OPENAI_API_KEY")
        return cls(
            llm_enabled=os.getenv("LLM_ENABLED", "false").lower() == "true",
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            openai_api_key=api_key.strip() if api_key else None,
            intent_confidence_threshold=float(
                os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.75")
            ),
            suggestion_confidence_threshold=float(
                os.getenv("SUGGESTION_CONFIDENCE_THRESHOLD", "0.80")
            ),
            cache_ttl_seconds=int(ttl_raw) if ttl_raw else None,
        )
