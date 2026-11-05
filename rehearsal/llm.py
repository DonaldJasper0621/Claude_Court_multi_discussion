"""Model backends: the real Anthropic client and a schema-driven mock.

Both expose one coroutine, `complete`, which returns a validated Pydantic
instance plus token usage. The engine never touches the SDK directly.
"""

from __future__ import annotations

import types
import typing
from typing import Any, Literal, Protocol, TypeVar, get_args, get_origin

from pydantic import BaseModel

from .schemas import Usage

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    """A role call failed in a way the engine should record rather than crash on."""


class RefusalError(LLMError):
    pass


class LLM(Protocol):
    async def complete(
        self,
        *,
        system: list[dict[str, Any]],
        user: str,
        schema: type[T],
        model: str,
        effort: str,
        max_tokens: int,
    ) -> tuple[T, Usage]: ...


# --------------------------------------------------------------------------- #
# Anthropic
# --------------------------------------------------------------------------- #


class AnthropicLLM:
    def __init__(self) -> None:
        import anthropic  # imported lazily so --mock works without credentials configured

        self._anthropic = anthropic
        # Zero-arg client: resolves ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, or an
        # `ant auth login` profile. Never hardcode a key here.
        self._client = anthropic.AsyncAnthropic()

    async def complete(
        self,
        *,
        system: list[dict[str, Any]],
        user: str,
        schema: type[T],
        model: str,
        effort: str,
        max_tokens: int,
    ) -> tuple[T, Usage]:
        a = self._anthropic
        try:
            response = await self._client.messages.parse(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
                output_format=schema,
                output_config={"effort": effort},
            )
        except a.AuthenticationError as e:
            raise LLMError(
                "Authentication failed. Set ANTHROPIC_API_KEY or run `ant auth login`."
            ) from e
        except a.BadRequestError as e:
            raise LLMError(f"Bad request: {e.message}") from e
        except a.RateLimitError as e:
            raise LLMError(f"Rate limited: {e.message}") from e
        except a.APIStatusError as e:
            raise LLMError(f"API error {e.status_code}: {e.message}") from e
        except a.APIConnectionError as e:
            raise LLMError(f"Connection error: {e}") from e

        if response.stop_reason == "refusal":
            details = getattr(response, "stop_details", None)
            category = getattr(details, "category", None) if details else None
            raise RefusalError(f"Model declined the request (category: {category}).")
        if response.stop_reason == "max_tokens":
            raise LLMError(
                f"Response hit max_tokens={max_tokens} before finishing. Raise max_tokens in config.yaml."
            )
        parsed = response.parsed_output
        if parsed is None:
            raise LLMError("Model returned no structured output.")

        u = response.usage
        usage = Usage(
            input_tokens=u.input_tokens or 0,
            output_tokens=u.output_tokens or 0,
            cache_read_input_tokens=getattr(u, "cache_read_input_tokens", 0) or 0,
            cache_creation_input_tokens=getattr(u, "cache_creation_input_tokens", 0) or 0,
        )
        return parsed, usage


# --------------------------------------------------------------------------- #
# Mock
# --------------------------------------------------------------------------- #


class MockLLM:
    """Returns schema-valid placeholder output so the pipeline and report can be
    exercised without credentials. Every string is prefixed with [mock]."""

    def __init__(self, list_length: int = 2) -> None:
        self.list_length = list_length
        self.calls: list[dict[str, Any]] = []

    async def complete(
        self,
        *,
        system: list[dict[str, Any]],
        user: str,
        schema: type[T],
        model: str,
        effort: str,
        max_tokens: int,
    ) -> tuple[T, Usage]:
        self.calls.append({"system": system, "user": user, "schema": schema.__name__, "model": model})
        instance = mock_instance(schema, list_length=self.list_length)
        words = len(user.split()) + sum(len(str(b.get("text", "")).split()) for b in system)
        return instance, Usage(input_tokens=int(words * 1.3), output_tokens=400)


def mock_instance(model_cls: type[T], *, list_length: int = 2, _path: str = "") -> T:
    values: dict[str, Any] = {}
    for name, field in model_cls.model_fields.items():
        values[name] = _mock_value(field.annotation, f"{_path}{name}", list_length)
    return model_cls(**values)


def _mock_value(annotation: Any, path: str, n: int) -> Any:
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Optional[X] / X | None  -> produce X
    if origin is typing.Union or origin is types.UnionType:
        non_none = [a for a in args if a is not type(None)]
        return _mock_value(non_none[0], path, n) if non_none else None
    if origin is Literal:
        return args[0]
    if origin in (list, typing.List):
        inner = args[0] if args else str
        return [_mock_value(inner, f"{path}[{i}]", n) for i in range(n)]
    if origin in (dict, typing.Dict):
        return {}
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return mock_instance(annotation, list_length=n, _path=f"{path}.")
    if annotation is bool:
        return True
    if annotation is int:
        return 1
    if annotation is float:
        return 1.0
    return f"[mock] {path}"
