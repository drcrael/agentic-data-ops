"""Exercise real local inference using the installed release, without mocked transports."""

import hashlib
import json
import subprocess
from pathlib import Path

import httpx
import yaml

from data_maturity.evidence.validation import validate_assessment
from data_maturity.models.control import AssessmentRun

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/live-model-audit"
ROLES = [
    "semantic_inference",
    "quality_reasoning",
    "governance_reasoning",
    "maturation_reasoning",
    "report_generation",
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = OUT / "parts.csv"
    source.write_text(
        "part_id,inspection_date,value\nP-001,2026-01-01,10\nP-002,2026-01-02,20\nP-003,2026-01-03,\n",
        encoding="utf-8",
    )
    original = hashlib.sha256(source.read_bytes()).hexdigest()
    with httpx.Client(trust_env=False) as client:
        version = client.get("http://127.0.0.1:11434/api/version").json()
        models = client.get("http://127.0.0.1:11434/api/tags").json()
    results = {"runtime": version, "models": models, "adapters": {}}
    for provider, base_url in [
        ("ollama", "http://127.0.0.1:11434"),
        ("openai_compatible", "http://127.0.0.1:11434/v1"),
    ]:
        config = OUT / f"{provider}.yaml"
        config.write_text(
            yaml.safe_dump(
                {
                    "llm_enabled": True,
                    "llm_max_attempts": 2,
                    "security": {"mode": "local_only"},
                    "models": {
                        role: {
                            "provider": provider,
                            "model": "qwen2.5:3b",
                            "base_url": base_url,
                            "timeout": 600,
                            "max_output_tokens": 2048,
                        }
                        for role in ROLES
                    },
                }
            ),
            encoding="utf-8",
        )
        target = OUT / provider
        run = subprocess.run(
            ["data-maturity", "analyze", str(source), "--config", str(config), "-o", str(target)],
            capture_output=True,
            text=True,
            timeout=3600,
        )
        (OUT / f"{provider}.log").write_text(run.stdout + run.stderr, encoding="utf-8")
        assert run.returncode == 0, (provider, run.stdout, run.stderr)
        history = AssessmentRun.model_validate_json(
            (target / "assessment_history.json").read_text()
        )
        validate_assessment(history.assessment, set())
        records = [r.model_dump(mode="json") for r in history.assessment.inference_records]
        results["adapters"][provider] = records
        (OUT / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(json.dumps({"provider": provider, "records": records}), flush=True)
        assert {r["role"] for r in records} == set(ROLES)
        assert all(r["status"] == "COMPLETE" and r["provider"] == provider for r in records)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == original
        manifest = json.loads((target / "run_manifest.json").read_text())
        for name, expected in manifest["artifact_sha256"].items():
            assert hashlib.sha256((target / name).read_bytes()).hexdigest() == expected
    print("Both live adapters completed all five reasoning roles.", flush=True)


if __name__ == "__main__":
    main()
