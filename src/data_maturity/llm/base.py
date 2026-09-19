"""Vendor-independent, structured generation interface."""

from __future__ import annotations

from typing import Literal, Protocol

from pydantic import BaseModel, Field

from data_maturity.models.core import Model


class Message(Model):
    role: Literal["system", "user", "assistant"]
    content: str


class ProviderCapabilities(Model):
    structured_output: bool = True
    json_schema: bool = True
    tool_calling: bool = False
    streaming: bool = False
    local_execution: bool = False
    context_window: int | None = None


class LLMResponse(Model):
    content: str


class LLMProvider(Protocol):
    capabilities: ProviderCapabilities

    def generate(
        self,
        messages: list[Message],
        response_schema: type[BaseModel] | None = None,
        temperature: float = 0.0,
    ) -> LLMResponse: ...


class SemanticProposal(Model):
    field_ids: list[str] = Field(min_length=1)
    semantic_type: Literal[
        "identifier",
        "timestamp",
        "coordinate",
        "status",
        "category",
        "name",
        "email",
        "phone",
        "URL",
        "country",
        "state",
        "postal_code",
        "currency",
        "percentage",
        "latitude",
        "longitude",
        "duration",
        "measurement",
        "free_text",
    ]
    confidence: float = Field(ge=0, le=1)
    evidence_refs: list[str] = Field(min_length=1)
    reasoning: str = Field(min_length=1, max_length=2000)
    alternatives: list[str] = Field(default_factory=list, max_length=10)


class Interpretation(Model):
    finding_refs: list[str] = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)
    explanation: str = Field(min_length=1, max_length=2000)
    confidence: float = Field(ge=0, le=1)


class ReasoningResponse(Model):
    """No output fields exist for authoritative units, keys, scores or tool actions."""

    proposals: list[SemanticProposal] = Field(default_factory=list, max_length=100)
    interpretations: list[Interpretation] = Field(default_factory=list, max_length=100)
