"""Shared bounded HTTP transport. No redirects, proxies, tools, or implicit credentials."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx
from pydantic import BaseModel

from data_maturity.config import ProviderConfig, SecurityConfig
from data_maturity.llm.base import LLMResponse, Message, ProviderCapabilities
from data_maturity.security.data_policy import classification, enforce


class HTTPProvider:
    def __init__(
        self,
        config: ProviderConfig,
        security: SecurityConfig,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.config = config
        self.security = security
        self.transport = transport
        self.capabilities = ProviderCapabilities(
            json_schema=config.json_schema, local_execution=classification(config) == "LOCAL"
        )

    def generate(
        self,
        messages: list[Message],
        response_schema: type[BaseModel] | None = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        enforce(self.config, self.security)
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [m.model_dump() for m in messages],
        }
        schema = response_schema.model_json_schema() if response_schema else None
        if self.config.provider == "ollama":
            endpoint = "/api/chat"
            payload.update(
                stream=False,
                options={"temperature": temperature, "num_predict": self.config.max_output_tokens},
            )
            if schema:
                payload["format"] = schema if self.config.json_schema else "json"
        else:
            endpoint = "/chat/completions"
            payload.update(temperature=temperature, max_tokens=self.config.max_output_tokens)
            if schema:
                payload["response_format"] = (
                    {
                        "type": "json_schema",
                        "json_schema": {"name": "assessment_reasoning", "schema": schema},
                    }
                    if self.config.json_schema
                    else {"type": "json_object"}
                )
        key = os.environ.get(self.config.api_key_env)
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        # trust_env=False also ignores proxy variables, preventing a loopback request from leaking.
        with httpx.Client(
            timeout=self.config.timeout,
            trust_env=False,
            follow_redirects=False,
            transport=self.transport,
        ) as client:
            with client.stream(
                "POST",
                (self.config.base_url or "").rstrip("/") + endpoint,
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()
                data = bytearray()
                for chunk in response.iter_bytes():
                    data.extend(chunk)
                    if len(data) > 1_000_000:
                        raise ValueError("Inference response exceeds 1 MB")
        result = json.loads(data)
        content = (
            result["message"]["content"]
            if self.config.provider == "ollama"
            else result["choices"][0]["message"]["content"]
        )
        return LLMResponse(content=content)
