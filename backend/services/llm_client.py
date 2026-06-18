import json
import urllib.error
import urllib.request
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...


class NullLLMClient:
    """Used when LLM fallback is disabled."""

    def complete(self, prompt: str) -> str:
        raise RuntimeError("LLM is not configured. Set LLM_ENABLED=true to enable.")


class OpenAILLMClient:
    """Thin OpenAI chat-completions client (stdlib only)."""

    def __init__(self, api_key: str, model: str, timeout_seconds: int = 30) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout_seconds = timeout_seconds

    def complete(self, prompt: str) -> str:
        body = json.dumps(
            {
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI request failed ({exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenAI request failed: {exc.reason}") from exc

        try:
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("OpenAI response did not include message content") from exc
