import json

import httpx
import pytest

from data_maturity.agents.orchestrator import AssessmentOrchestrator
from data_maturity.config import ProviderConfig, SecurityConfig, load_config
from data_maturity.evidence.validation import validate_assessment
from data_maturity.llm.base import Message, ReasoningResponse
from data_maturity.llm.gateway import LLMGateway, ReasoningFailure
from data_maturity.llm.http_provider import HTTPProvider
from data_maturity.llm.mock import MockLLMProvider

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "provider_name,schema_support",
    [
        ("ollama", True),
        ("ollama", False),
        ("openai_compatible", True),
        ("openai_compatible", False),
    ],
)
def test_provider_wire_protocol(provider_name, schema_support, monkeypatch):
    captured = []

    def handler(request):
        captured.append(request)
        payload = json.loads(request.content)
        assert payload["model"] == "configured-model"
        assert "tools" not in payload
        if provider_name == "ollama":
            assert request.url.path == "/api/chat"
            assert isinstance(payload["format"], dict) == schema_support
            return httpx.Response(200, json={"message": {"content": '{"proposals":[]}'}})
        assert request.url.path == "/v1/chat/completions"
        assert payload["response_format"]["type"] == (
            "json_schema" if schema_support else "json_object"
        )
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"proposals":[]}'}}]})

    monkeypatch.setenv("DATA_MATURITY_API_KEY", "test-token")
    config = ProviderConfig(
        provider=provider_name,
        model="configured-model",
        base_url="http://127.0.0.1:8000" + ("/v1" if provider_name == "openai_compatible" else ""),
        json_schema=schema_support,
    )
    response = HTTPProvider(config, SecurityConfig(), httpx.MockTransport(handler)).generate(
        [Message(role="user", content="context")], ReasoningResponse
    )
    assert ReasoningResponse.model_validate_json(response.content).proposals == []
    assert captured[0].headers["Authorization"] == "Bearer test-token"


def test_mock_response_enters_canonical_model(fixtures):
    config = load_config()
    first = AssessmentOrchestrator(config).assess(fixtures / "ambiguous_manufacturing.xlsx")
    d = first.datasets[0]
    semantic = {
        "proposals": [
            {
                "field_ids": [d.physical_schema.fields[0].field_id],
                "semantic_type": "identifier",
                "confidence": 0.8,
                "evidence_refs": d.profile.columns[0].evidence_refs,
                "reasoning": "Name suggests identifier",
                "alternatives": ["catalog code"],
            }
        ]
    }
    quality = {
        "interpretations": [
            {
                "finding_refs": [d.findings[0].finding_id],
                "evidence_refs": d.findings[0].evidence_refs,
                "explanation": "Obtain the authoritative definition before downstream use",
                "confidence": 0.7,
            }
        ]
    }
    config.llm_enabled = True
    config.models = {"semantic_inference": ProviderConfig(), "quality_reasoning": ProviderConfig()}
    gateway = LLMGateway(
        config,
        {
            "semantic_inference": MockLLMProvider([json.dumps(semantic)]),
            "quality_reasoning": MockLLMProvider([json.dumps(quality)]),
        },
    )
    result = AssessmentOrchestrator(config, gateway).assess(fixtures / "ambiguous_manufacturing.xlsx")
    validate_assessment(result)
    assert any(a.origin == "llm" and a.state == "INFERRED" for a in result.datasets[0].assertions)
    assert result.datasets[0].analyst_notes


def test_optional_failure_preserves_deterministic_results(fixtures):
    config = load_config()
    config.llm_enabled = True
    config.models = {"semantic_inference": ProviderConfig()}
    provider = MockLLMProvider(["This spreadsheet looks good!", "still prose"])
    result = AssessmentOrchestrator(
        config, LLMGateway(config, {"semantic_inference": provider})
    ).assess(fixtures / "dirty_customers.xlsx")
    assert result.datasets[0].profile.duplicate_record_count == 1
    assert any(c.status == "FAILED" for c in result.component_status)
    assert result.inference_records[0].attempts == 2
    validate_assessment(result)


def test_cache_bound_to_evidence_and_model(fixtures):
    config = load_config()
    config.llm_cache = True
    result = AssessmentOrchestrator(config).assess(fixtures / "clean_customers.xlsx")
    provider = MockLLMProvider()
    gateway = LLMGateway(config, {"semantic_inference": provider})
    gateway.generate("semantic_inference", result.datasets[0])
    gateway.generate("semantic_inference", result.datasets[0])
    assert len(provider.calls) == 1
    assert gateway.records[-1].status == "CACHED"
    result.datasets[0].profile.columns[0].null_count = 5
    gateway.generate("semantic_inference", result.datasets[0])
    assert len(provider.calls) == 2


def test_nonsemantic_role_cannot_propose_labels(fixtures):
    config = load_config()
    d = AssessmentOrchestrator(config).assess(fixtures / "clean_customers.xlsx").datasets[0]
    body = json.dumps(
        {
            "proposals": [
                {
                    "field_ids": [d.physical_schema.fields[0].field_id],
                    "semantic_type": "identifier",
                    "confidence": 0.5,
                    "evidence_refs": d.profile.columns[0].evidence_refs,
                    "reasoning": "test",
                }
            ]
        }
    )
    with pytest.raises(ReasoningFailure):
        LLMGateway(config, {"quality_reasoning": MockLLMProvider([body, body])}).generate(
            "quality_reasoning", d
        )
