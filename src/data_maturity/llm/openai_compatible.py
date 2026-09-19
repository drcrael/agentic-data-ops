"""Configurable OpenAI-compatible transport, with no vendor SDK dependency."""

from data_maturity.llm.http_provider import HTTPProvider


class OpenAICompatibleProvider(HTTPProvider):
    """Compatible with local vLLM and explicitly permitted remote endpoints."""
