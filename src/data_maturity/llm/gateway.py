"""Central routing, preflight policy, validated retries and content-keyed caching."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from importlib.resources import files

import httpx
from pydantic import ValidationError

from data_maturity.config import Config, ProviderConfig
from data_maturity.llm.base import LLMProvider, Message, ReasoningResponse
from data_maturity.llm.context import build_context
from data_maturity.llm.mock import MockLLMProvider
from data_maturity.llm.ollama import OllamaProvider
from data_maturity.llm.openai_compatible import OpenAICompatibleProvider
from data_maturity.models.assessment import DatasetAssessment, InferenceRecord
from data_maturity.models.core import Dataset
from data_maturity.security.data_policy import enforce
from data_maturity.util import digest

logger = logging.getLogger(__name__)
PROMPT_VERSION = "v1"


class ReasoningFailure(RuntimeError):
    """Optional component exhausted bounded attempts; deterministic results remain valid."""


class LLMGateway:
    def __init__(self, config: Config, providers: dict[str, LLMProvider] | None = None) -> None:
        self.config = config
        self.providers = providers or {}
        self.records: list[InferenceRecord] = []
        self.cache: dict[str, ReasoningResponse] = {}

    def preflight(self) -> None:
        if self.config.llm_enabled:
            for provider in self.config.models.values():
                enforce(provider, self.config.security)

    def generate(
        self, role: str, assessment: DatasetAssessment, dataset: Dataset | None = None
    ) -> ReasoningResponse:
        provider_config = self.config.models.get(role, ProviderConfig())
        enforce(provider_config, self.config.security)
        context, contains_raw = build_context(assessment, dataset, self.config, provider_config)
        enforce(provider_config, self.config.security, contains_raw)
        prompt = files("data_maturity.prompts").joinpath(f"{role}.v1.txt").read_text()
        key = digest(
            {
                "context": context,
                "source_hash": assessment.source.sha256,
                "prompt": prompt,
                "provider": provider_config,
                "role": role,
            }
        )
        evidence_ids = {e["evidence_id"] for e in context["evidence"]}
        field_ids = {f["field_id"] for f in context["fields"]}
        finding_ids = {f["finding_id"] for f in context["findings"]}

        def validate(response: ReasoningResponse) -> None:
            if role != "semantic_inference" and response.proposals:
                raise ValueError("Only semantic role may propose semantic labels")
            for proposal in response.proposals:
                if (
                    not set(proposal.field_ids) <= field_ids
                    or not set(proposal.evidence_refs) <= evidence_ids
                ):
                    raise ValueError("Proposal references IDs absent from supplied context")
            for note in response.interpretations:
                if (
                    not set(note.finding_refs) <= finding_ids
                    or not set(note.evidence_refs) <= evidence_ids
                ):
                    raise ValueError("Interpretation references IDs absent from supplied context")

        if self.config.llm_cache and key in self.cache:
            cached = self.cache[key].model_copy(deep=True)
            validate(cached)
            self.records.append(
                InferenceRecord(
                    role=role,
                    provider=provider_config.provider,
                    model=provider_config.model,
                    prompt_version=PROMPT_VERSION,
                    attempts=0,
                    status="CACHED",
                    context_hash=key,
                )
            )
            return cached
        if role not in self.providers:
            factories: dict[str, Callable[[], LLMProvider]] = {
                "mock": MockLLMProvider,
                "ollama": lambda: OllamaProvider(provider_config, self.config.security),
                "openai_compatible": lambda: OpenAICompatibleProvider(
                    provider_config, self.config.security
                ),
            }
            self.providers[role] = factories[provider_config.provider]()
        messages = [
            Message(
                role="system",
                content=prompt
                + "\nOUTPUT SCHEMA:\n"
                + json.dumps(ReasoningResponse.model_json_schema()),
            ),
            Message(
                role="user", content=json.dumps({"untrusted_dataset_context": context}, default=str)
            ),
        ]
        last_error = "unknown"
        for attempt in range(1, self.config.llm_max_attempts + 1):
            logger.info("llm_call", extra={"component": role, "attempt": attempt})
            try:
                output = self.providers[role].generate(
                    messages, ReasoningResponse, provider_config.temperature
                )
                response = ReasoningResponse.model_validate_json(output.content)
                validate(response)
                self.records.append(
                    InferenceRecord(
                        role=role,
                        provider=provider_config.provider,
                        model=provider_config.model,
                        prompt_version=PROMPT_VERSION,
                        attempts=attempt,
                        status="COMPLETE",
                        context_hash=key,
                    )
                )
                if self.config.llm_cache:
                    self.cache[key] = response.model_copy(deep=True)
                return response
            except (ValidationError, ValueError, KeyError, TypeError, httpx.HTTPError) as exc:
                # Never copy model output, API errors, URLs or raw values into logs or retry feedback.
                last_error = type(exc).__name__
                logger.warning(
                    "llm_validation_or_transport_failure",
                    extra={"component": role, "error_type": last_error, "attempt": attempt},
                )
                feedback = "Previous response failed schema/reference validation. Return only the required JSON schema and IDs supplied in context."
                messages = [*messages[:2], Message(role="user", content=feedback)]
        self.records.append(
            InferenceRecord(
                role=role,
                provider=provider_config.provider,
                model=provider_config.model,
                prompt_version=PROMPT_VERSION,
                attempts=self.config.llm_max_attempts,
                status="FAILED",
                context_hash=key,
                error=last_error,
            )
        )
        raise ReasoningFailure(
            f"{role} failed after {self.config.llm_max_attempts} attempts ({last_error})"
        )
