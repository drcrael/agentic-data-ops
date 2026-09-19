import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

from data_maturity.evidence.validation import validate_assessment
from data_maturity.models.control import AssessmentRun

repo = Path(__file__).resolve().parents[1]
cli = shutil.which("data-maturity")
assert cli, "Installed entry point missing"
fixtures = repo / "tests/fixtures"
out = repo / "output/platform-audit"
out.mkdir(parents=True, exist_ok=True)
checks = []


def command(label, args, code=0):
    r = subprocess.run([str(cli), *map(str, args)], cwd=out, capture_output=True, text=True)
    assert r.returncode == code, (label, r.returncode, r.stdout, r.stderr)
    checks.append({"check": label, "passed": True, "exit_code": r.returncode})
    return r


def bundle(path):
    manifest = json.loads((path / "run_manifest.json").read_text())
    for name, digest in manifest["artifact_sha256"].items():
        assert hashlib.sha256((path / name).read_bytes()).hexdigest() == digest, (name, path)
    history = AssessmentRun.model_validate_json((path / "assessment_history.json").read_text())
    validate_assessment(history.assessment, {r.resolution_id for r in history.resolutions})
    assert history.assessment.application_version == "0.1.2"
    if os.name != "nt":
        assert (path.stat().st_mode & 0o077) == 0
    return history


for name in [
    "clean_customers",
    "dirty_customers",
    "semi_structured",
    "relational",
    "ambiguous_manufacturing",
    "anomalies",
    "prompt_injection",
    "small.csv",
    "small.tsv",
]:
    source = fixtures / (name if "." in name else name + ".xlsx")
    initial = hashlib.sha256(source.read_bytes()).hexdigest()
    target = out / name.replace(".", "-")
    command("analyze " + name, ["analyze", source, "--no-llm", "-o", target])
    run = bundle(target)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == initial
    assert run.assessment.source.sha256 == initial
    assert all(
        d.proposed_contract and d.proposed_contract.status == "proposed"
        for d in run.assessment.datasets
    )
    assert all(len(d.maturity.dimensions) == 10 for d in run.assessment.datasets)
command("inspect manufacturing", ["inspect", fixtures / "ambiguous_manufacturing.xlsx"])
command(
    "profile manufacturing",
    ["profile", fixtures / "ambiguous_manufacturing.xlsx", "-o", out / "profile"],
)
command(
    "mock manufacturing + mission",
    [
        "analyze",
        fixtures / "ambiguous_manufacturing.xlsx",
        "--config",
        repo / "configs/test_mock_llm.yaml",
        "--mission",
        repo / "examples/manufacturing_operations.yaml",
        "-o",
        out / "mock",
    ],
)
run = bundle(out / "mock")
assert len(run.assessment.inference_records) == 5
assert {m.requirement_id: m.status for m in run.assessment.mission_fitness} == {
    "part-identity-completeness": "FIT",
    "coordinate-frame": "UNDETERMINED",
    "coordinate-units": "UNDETERMINED",
}

# Drive a complete persistent baseline lifecycle through actual installed console processes.
source = out / "production.csv"
source.write_text("part_id,value\nP-001,10\nP-002,20\nP-003,30\n")
command("initial baseline assessment", ["analyze", source, "--no-llm", "-o", out / "initial"])
initial = bundle(out / "initial")
resolutions = []
for d in initial.assessment.datasets:
    for q in d.unresolved_questions:
        if q.blocking:
            resolutions.append(
                {
                    "resolution_id": "risk:" + q.question_id,
                    "question_id": q.question_id,
                    "resolution_type": "ACCEPTED_RISK",
                    "value": "Synthetic test only",
                    "provided_by": "Test owner",
                    "authority": "Fixture specification",
                    "authoritative": True,
                    "rationale": "Exercise CLI baseline lifecycle",
                    "scope": "Synthetic test records only",
                    "review_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                }
            )
answers = out / "risks.yaml"
answers.write_text(yaml.safe_dump({"resolutions": resolutions}))
command(
    "resolve and establish named baseline",
    [
        "resolve",
        out / "initial/assessment_history.json",
        answers,
        "--source",
        source,
        "--baseline",
        "audit-approved",
        "-o",
        out / "baseline",
    ],
)
baseline = bundle(out / "baseline")
assert baseline.baselines[0].name == "audit-approved"
assert baseline.iterations[-1].outcome == "BASELINE_ESTABLISHED"
command(
    "unchanged reassessment",
    [
        "analyze",
        source,
        "--prior",
        out / "baseline/assessment_history.json",
        "-o",
        out / "unchanged",
    ],
)
unchanged = bundle(out / "unchanged")
checks.append(
    {
        "check": "unchanged serialized resolutions skip all recomputation",
        "passed": unchanged.iterations[-1].components_executed == [],
        "observed_trigger": unchanged.iterations[-1].trigger,
        "components_executed": unchanged.iterations[-1].components_executed,
    }
)
source.write_text("part_id,value\nP-001,10\n,20\n,30\n")
command(
    "changed-source baseline comparison",
    [
        "analyze",
        source,
        "--prior",
        out / "unchanged/assessment_history.json",
        "--compare-baseline",
        "audit-approved",
        "-o",
        out / "regressed",
    ],
)
regressed = bundle(out / "regressed")
assert any(c.classification == "REGRESSED" for c in regressed.delta.quality)
assert regressed.iterations[-1].outcome == "WAITING_FOR_HUMAN"
command(
    "reject stale-source resolution",
    [
        "resolve",
        out / "initial/assessment_history.json",
        answers,
        "--source",
        source,
        "-o",
        out / "stale",
    ],
    2,
)
command("reject existing output", ["analyze", source, "-o", out / "initial"], 2)
command(
    "reject missing baseline",
    [
        "analyze",
        source,
        "--prior",
        out / "regressed/assessment_history.json",
        "--compare-baseline",
        "missing",
        "-o",
        out / "missing",
    ],
    2,
)
bad = out / "bad-config.yaml"
bad.write_text("unexpected_setting: true\n")
command(
    "reject invalid configuration",
    ["analyze", source, "--config", bad, "-o", out / "bad-config"],
    2,
)
ragged = out / "ragged.csv"
ragged.write_text("id,value\n1,2,3\n")
command("reject malformed CSV", ["analyze", ragged, "-o", out / "bad-csv"], 2)
policy = out / "denied.yaml"
policy.write_text(
    "llm_enabled: true\nmodels:\n  semantic_inference:\n    provider: openai_compatible\n    model: test\n    base_url: https://example.com/v1\n"
)
command(
    "reject remote provider under local policy",
    ["analyze", source, "--config", policy, "-o", out / "denied"],
    2,
)
for name in ["stale", "missing", "bad-config", "bad-csv", "denied"]:
    assert not (out / name).exists(), name
(out / "results.json").write_text(json.dumps(checks, indent=2))
print(
    json.dumps(
        {
            "checks": len(checks),
            "passed": sum(c["passed"] for c in checks),
            "failed": [c for c in checks if not c["passed"]],
        },
        indent=2,
    )
)

print(json.dumps({"os": platform.platform(), "python": sys.version, "cli": cli}, indent=2))
assert all(c["passed"] for c in checks)
