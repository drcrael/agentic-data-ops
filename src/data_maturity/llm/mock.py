"""Deterministic scripted provider; requests captured for trust-boundary tests."""

from __future__ import annotations

from collections import deque

from pydantic import BaseModel

from data_maturity.llm.base import LLMResponse, Message, ProviderCapabilities


class MockLLMProvider:
    capabilities = ProviderCapabilities(local_execution=True)

    def __init__(self, responses: list[str] | None = None) -> None:
        self.responses = deque(responses or [])
        self.calls: list[list[Message]] = []

    def register_response(self, role: str, response: BaseModel | str) -> None:
        # The gateway routes one mock instance per role; role retained in the interface.
        self.responses.append(response if isinstance(response, str) else response.model_dump_json())

    def generate(
        self,
        messages: list[Message],
        response_schema: type[BaseModel] | None = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        self.calls.append(messages)
        return LLMResponse(
            content=self.responses.popleft()
            if self.responses
            else '{"proposals":[],"interpretations":[]}'
        )
