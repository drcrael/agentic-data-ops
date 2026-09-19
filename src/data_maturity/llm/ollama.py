"""Ollama chat provider using its local structured-output API."""

from data_maturity.llm.http_provider import HTTPProvider


class OllamaProvider(HTTPProvider):
    """Provider specialization selected and configured by the central gateway."""
