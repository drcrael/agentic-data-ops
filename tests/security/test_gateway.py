import json

import httpx
import pytest

from data_maturity.agents.orchestrator import AssessmentOrchestrator
from data_maturity.config import ProviderConfig, SecurityConfig, load_config
from data_maturity.evidence.validation import IntegrityError, validate_assessment
from data_maturity.llm.base import Message
from data_maturity.llm.gateway import LLMGateway, ReasoningFailure
from data_maturity.llm.http_provider import HTTPProvider
from data_maturity.llm.mock import MockLLMProvider
from data_maturity.models.core import EvidenceEdge
from data_maturity.security.data_policy import PolicyViolation, classification, enforce

pytestmark = pytest.mark.security


@pytest.fixture
def assessment(fixtures):
    return AssessmentOrchestrator(load_config()).assess(fixtures / "ambiguous_manufacturing.xlsx")


def test_remote_never_called_in_local_mode(assessment):
    config = load_config()
    config.llm_enabled = True
    config.models = {
        "semantic_inference": ProviderConfig(
            provider="openai_compatible", model="test", base_url="https://example.com/v1"
        )
    }
    provider = MockLLMProvider()
    gateway = LLMGateway(config, {"semantic_inference": provider})
    with pytest.raises(PolicyViolation):
        gateway.preflight()
    with pytest.raises(PolicyViolation):
        gateway.generate("semantic_inference", assessment.datasets[0])
    assert provider.calls == []


def test_remote_actual_payload_excludes_raw_values(fixtures):
    from data_maturity.ingestion.base import ingest

    config = load_config()
    config.llm_context.include_samples = True
    config.profiling.include_value_summaries = True
    config.security = SecurityConfig(mode="hybrid", allow_metadata_to_remote_models=True)
    config.models = {
        "semantic_inference": ProviderConfig(
            provider="openai_compatible", model="test", base_url="https://example.com/v1"
        )
    }
    workbook = AssessmentOrchestrator(config).assess(fixtures / "prompt_injection.xlsx")
    _, datasets = ingest(fixtures / "prompt_injection.xlsx", config)
    provider = MockLLMProvider()
    LLMGateway(config, {"semantic_inference": provider}).generate(
        "semantic_inference", workbook.datasets[0], datasets[0]
    )
    payload = provider.calls[0][1].content
    assert "Upload this workbook" not in payload
    assert "Ignore all previous" not in payload
    assert "reveal all hidden" not in payload
    assert '"samples"' not in payload
    assert '"common_values"' not in payload
    assert '"row_count"' in payload


def test_injection_is_inert(fixtures, tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network access attempted")

    monkeypatch.setattr(httpx.Client, "send", forbidden)
    config = load_config()
    config.llm_enabled = True
    config.llm_context.include_samples = True
    config.models = {"semantic_inference": ProviderConfig()}
    provider = MockLLMProvider()
    workbook = AssessmentOrchestrator(
        config, LLMGateway(config, {"semantic_inference": provider})
    ).assess(fixtures / "prompt_injection.xlsx")
    assert workbook.datasets[0].profile.row_count == 4
    assert config.models["semantic_inference"].provider == "mock"
    assert "UNTRUSTED_DATA_NOT_INSTRUCTIONS" in provider.calls[0][1].content
    assert "Upload this workbook" in provider.calls[0][1].content
    assert list(tmp_path.iterdir()) == []


def test_fabricated_reference_retried_and_rejected(assessment):
    d = assessment.datasets[0]
    response = json.dumps(
        {
            "proposals": [
                {
                    "field_ids": [d.physical_schema.fields[0].field_id],
                    "semantic_type": "identifier",
                    "confidence": 0.9,
                    "evidence_refs": ["fabricated"],
                    "reasoning": "name",
                }
            ]
        }
    )
    provider = MockLLMProvider([response, response])
    gateway = LLMGateway(load_config(), {"semantic_inference": provider})
    with pytest.raises(ReasoningFailure):
        gateway.generate("semantic_inference", d)
    assert len(provider.calls) == 2
    assert "validation" in provider.calls[1][-1].content
    assert gateway.records[-1].status == "FAILED"


def test_unsupported_units_and_observed_output_rejected(assessment):
    forbidden = json.dumps(
        {
            "proposals": [
                {
                    "field_ids": [assessment.datasets[0].physical_schema.fields[2].field_id],
                    "semantic_type": "coordinate",
                    "unit": "mm",
                    "coordinate_frame": "machine-local",
                    "state": "OBSERVED",
                    "confidence": 1,
                    "evidence_refs": [assessment.datasets[0].evidence[0].evidence_id],
                    "reasoning": "guess",
                }
            ]
        }
    )
    provider = MockLLMProvider([forbidden, forbidden])
    with pytest.raises(ReasoningFailure):
        LLMGateway(load_config(), {"semantic_inference": provider}).generate(
            "semantic_inference", assessment.datasets[0]
        )
    assert all(f.unit is None for f in assessment.datasets[0].target_schema.fields)


@pytest.mark.parametrize(
    "url,expected",
    [
        ("http://127.0.0.1:11434", "LOCAL"),
        ("http://[::1]:8000", "LOCAL"),
        ("https://127.0.0.1.attacker.test", "REMOTE"),
        ("http://localhost:11434", "REMOTE"),
        ("http://10.0.0.1:8000", "REMOTE"),
    ],
)
def test_endpoint_classification(url, expected):
    provider = ProviderConfig(provider="ollama", model="test", base_url=url)
    assert classification(provider) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://user:secret@example.com",
        "https://example.com?key=secret",
        "file:///etc/passwd",
        "https://example.com/#secret",
    ],
)
def test_credential_urls_rejected(url):
    with pytest.raises(ValueError):
        ProviderConfig(provider="ollama", model="x", base_url=url)


def test_raw_policy_and_insecure_remote():
    provider = ProviderConfig(
        provider="openai_compatible", model="x", base_url="https://example.com"
    )
    with pytest.raises(PolicyViolation):
        enforce(provider, SecurityConfig(mode="hybrid"))
    with pytest.raises(PolicyViolation):
        enforce(
            provider,
            SecurityConfig(mode="hybrid", allow_metadata_to_remote_models=True),
            contains_raw=True,
        )
    provider.base_url = "http://example.com"
    with pytest.raises(PolicyViolation):
        enforce(provider, SecurityConfig(mode="hybrid", allow_metadata_to_remote_models=True))


def test_redirect_not_followed(monkeypatch):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(302, headers={"Location": "https://example.com/upload"})

    config = ProviderConfig(provider="ollama", model="test", base_url="http://127.0.0.1:11434")
    with pytest.raises(httpx.HTTPStatusError):
        HTTPProvider(config, SecurityConfig(), httpx.MockTransport(handler)).generate(
            [Message(role="user", content="data")]
        )
    assert len(requests) == 1


def test_secret_not_in_records_logs_or_manifest(assessment, monkeypatch, caplog):
    monkeypatch.setenv("DATA_MATURITY_API_KEY", "SECRET_SENTINEL_393")
    provider = MockLLMProvider(["SECRET_SENTINEL_393 bad json", "bad json"])
    gateway = LLMGateway(load_config(), {"semantic_inference": provider})
    with pytest.raises(ReasoningFailure):
        gateway.generate("semantic_inference", assessment.datasets[0])
    assert "SECRET_SENTINEL_393" not in caplog.text
    assert "SECRET_SENTINEL_393" not in str(gateway.records)
    assert "SECRET_SENTINEL_393" not in assessment.model_dump_json()


def test_integrity_dangling_and_duplicate(assessment):
    bad = assessment.model_copy(deep=True)
    bad.datasets[0].findings[0].evidence_refs = ["missing"]
    with pytest.raises(IntegrityError, match="Dangling"):
        validate_assessment(bad)
    bad = assessment.model_copy(deep=True)
    bad.datasets[0].evidence.append(bad.datasets[0].evidence[0])
    with pytest.raises(IntegrityError, match="Duplicate"):
        validate_assessment(bad)
    bad = assessment.model_copy(deep=True)
    bad.graph.append(EvidenceEdge(source_id="missing", relationship="X", target_id="missing"))
    with pytest.raises(IntegrityError):
        validate_assessment(bad)


def test_pathological_pattern_times_out():
    from data_maturity.models.assessment import QualityRule
    from data_maturity.profiling.quality import evaluate_rule

    rule = QualityRule(
        rule_id="redos",
        field="value",
        operator="pattern",
        dimension="validity",
        parameters={"pattern": "(a|aa)+$"},
    )
    count, explanation = evaluate_rule(rule, ["a" * 2000 + "!"])
    assert count is None and "timed out" in explanation
