"""Validated YAML configuration. Environment variables carry credentials, never reports."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

import yaml
from pydantic import Field, model_validator

from data_maturity.models.assessment import QualityRule
from data_maturity.models.core import Model


class ProfilingConfig(Model):
    max_rows: int = Field(default=1_000_000, ge=1)
    sample_rows: int = Field(default=10_000, ge=1)
    top_values: int = Field(default=20, ge=0, le=100)
    max_columns: int = Field(default=256, ge=1, le=16384)
    max_file_bytes: int = Field(default=100_000_000, ge=1)
    max_excel_cells: int = Field(default=2_000_000, ge=1)
    max_uncompressed_bytes: int = Field(default=250_000_000, ge=1)
    max_field_chars: int = Field(default=100_000, ge=1)
    max_composite_candidates: int = Field(default=100, ge=0, le=10000)
    max_relationship_pairs: int = Field(default=5000, ge=0)
    include_value_summaries: bool = False


class RuntimeConfig(Model):
    output_directory: str = "output"
    random_seed: int = 42
    verbosity: Literal["INFO", "DEBUG", "WARNING"] = "INFO"


class SecurityConfig(Model):
    mode: Literal["local_only", "hybrid"] = "local_only"
    allow_raw_data_to_remote_models: bool = False
    allow_metadata_to_remote_models: bool = False


class ContextConfig(Model):
    include_samples: bool = False
    max_sample_rows: int = Field(default=20, ge=0, le=100)
    max_distinct_values: int = Field(default=30, ge=0, le=100)
    max_context_chars: int = Field(default=32000, ge=1000, le=1_000_000)


class ProviderConfig(Model):
    provider: Literal["mock", "ollama", "openai_compatible"] = "mock"
    model: str | None = None
    base_url: str | None = None
    api_key_env: str = "DATA_MATURITY_API_KEY"
    timeout: float = Field(default=30, gt=0, le=600)
    json_schema: bool = True
    temperature: float = Field(default=0, ge=0, le=2)
    max_output_tokens: int = Field(default=2048, ge=1, le=16000)

    @model_validator(mode="after")
    def endpoint(self) -> ProviderConfig:
        if self.provider != "mock":
            if not self.model or not self.base_url:
                raise ValueError("Inference providers require explicit model and base_url")
            parsed = urlsplit(self.base_url)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                raise ValueError("base_url must be an HTTP(S) endpoint")
            if parsed.username or parsed.password or parsed.query or parsed.fragment:
                raise ValueError(
                    "Credentials, query strings and fragments are forbidden in base_url"
                )
        return self


class ControlConfig(Model):
    max_iterations: int = Field(default=10, ge=1, le=100)
    stop_on_no_change: bool = True
    require_human_for_authoritative_resolution: Literal[True] = True


class Config(Model):
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    profiling: ProfilingConfig = Field(default_factory=ProfilingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    llm_context: ContextConfig = Field(default_factory=ContextConfig)
    models: dict[str, ProviderConfig] = Field(default_factory=dict)
    llm_enabled: bool = False
    llm_max_attempts: int = Field(default=2, ge=1, le=5)
    llm_cache: bool = False
    quality_rules_version: str = "1"
    quality_rules: list[QualityRule] = Field(default_factory=list)
    maturity_model: dict[str, Any] = Field(default_factory=dict)
    governance_metadata: dict[str, dict[str, Any]] = Field(default_factory=dict)
    assessment_control: ControlConfig = Field(default_factory=ControlConfig)
    severity_thresholds: dict[str, float] = Field(
        default_factory=lambda: {"high": 10.0, "medium": 1.0}
    )

    @model_validator(mode="after")
    def routing(self) -> Config:
        allowed = {
            "semantic_inference",
            "quality_reasoning",
            "governance_reasoning",
            "maturation_reasoning",
            "report_generation",
        }
        if set(self.models) - allowed:
            raise ValueError("Unknown model role")
        ids = [r.rule_id for r in self.quality_rules]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate quality rule IDs")
        for value in self.severity_thresholds.values():
            if not 0 <= value <= 100:
                raise ValueError("Severity thresholds must be between 0 and 100")
        if self.maturity_model:
            validate_maturity_model(self.maturity_model)
        return self


def validate_maturity_model(model: dict[str, Any]) -> None:
    if not isinstance(model.get("version"), (str, int)) or not isinstance(
        model.get("dimensions"), dict
    ):
        raise ValueError("Maturity model requires a version and dimensions mapping")
    for dimension, levels in model["dimensions"].items():
        if not isinstance(levels, dict) or not levels:
            raise ValueError(f"Invalid maturity dimension: {dimension}")
        if set(levels) != {f"level_{i}" for i in range(1, len(levels) + 1)} or len(levels) > 5:
            raise ValueError(
                "Maturity levels must be cumulative, contiguous levels 1 through at most 5"
            )
        for definition in levels.values():
            if (
                not isinstance(definition, dict)
                or not isinstance(definition.get("requirements"), list)
                or not definition["requirements"]
                or not all(isinstance(r, str) for r in definition["requirements"])
            ):
                raise ValueError("Every maturity level needs a nonempty list of criterion names")


def load_yaml(path: Path) -> Any:
    if path.stat().st_size > 2_000_000:
        raise ValueError("Configuration exceeds 2 MB limit")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_config(path: Path | None = None) -> Config:
    config = Config.model_validate(load_yaml(path) or {}) if path else Config()
    if not config.maturity_model:
        config.maturity_model = yaml.safe_load(
            files("data_maturity.resources").joinpath("maturity_model.yaml").read_text()
        )
    return config
