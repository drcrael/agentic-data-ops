"""Command-line workflows for inspection, assessment, resolution and reassessment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import typer
from pydantic import ValidationError

from data_maturity.config import Config, load_config, load_yaml
from data_maturity.control.controller import AssessmentController
from data_maturity.evidence.store import EvidenceStore
from data_maturity.ingestion.base import ingest
from data_maturity.logging import configure_logging
from data_maturity.models.assessment import MissionContext, WorkbookAssessment
from data_maturity.models.control import AssessmentRun, Resolution
from data_maturity.profiling.columns import DatasetProfiler
from data_maturity.reporting.writer import write_reports
from data_maturity.security.data_policy import PolicyViolation
from data_maturity.util import stable_id

app = typer.Typer(
    no_args_is_help=True, help="Evidence-backed, local-first data maturity assessment."
)
Input = Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)]
ConfigOption = Annotated[Path | None, typer.Option("--config", exists=True, dir_okay=False)]
OutputOption = Annotated[
    Path | None, typer.Option("--output", "-o", help="New or empty output directory")
]


def error(exc: Exception) -> None:
    # Configuration/model errors may contain raw values, so never echo full ValidationError.
    message = (
        "Configuration or model validation failed" if isinstance(exc, ValidationError) else str(exc)
    )
    typer.echo(f"Assessment failed: {message}", err=True)
    raise typer.Exit(code=2) from exc


def config_for(path: Path | None, no_llm: bool = False) -> Config:
    config = load_config(path)
    if no_llm:
        config.llm_enabled = False
    configure_logging(config.runtime.verbosity)
    return config


def load_prior(path: Path) -> AssessmentRun | WorkbookAssessment:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "assessment" in payload and "iterations" in payload:
        return AssessmentRun.model_validate(payload)
    history = path.with_name("assessment_history.json")
    if history.exists():
        run = AssessmentRun.model_validate_json(history.read_text(encoding="utf-8"))
        if run.assessment.assessment_id != payload.get("assessment_id"):
            raise ValueError("Assessment and adjacent history do not match")
        return run
    return WorkbookAssessment.model_validate(payload)


@app.command("inspect")
def inspect_file(source: Input, config: ConfigOption = None) -> None:
    """Inspect source structure and detected tabular regions; no inference."""
    try:
        metadata, datasets = ingest(source, config_for(config))
        typer.echo(
            json.dumps(
                {
                    "source": metadata.model_dump(mode="json"),
                    "datasets": [
                        {
                            "dataset_id": d.dataset_id,
                            "structure": d.structure.model_dump(),
                            "fields": [f.model_dump() for f in d.fields],
                        }
                        for d in datasets
                    ],
                },
                indent=2,
            )
        )
    except (ValueError, OSError, PolicyViolation) as exc:
        error(exc)


@app.command()
def profile(source: Input, config: ConfigOption = None, output: OutputOption = None) -> None:
    """Run only deterministic measurements and evidence generation."""
    try:
        cfg = config_for(config, True)
        _, datasets = ingest(source, cfg)
        store = EvidenceStore()
        profiles = {
            d.dataset_id: DatasetProfiler().profile(d, cfg, store).model_dump(mode="json")
            for d in datasets
        }
        payload = json.dumps(
            {
                "profiles": profiles,
                "evidence": [e.model_dump(mode="json") for e in store.items.values()],
            },
            indent=2,
        )
        if output:
            output.mkdir(parents=True, exist_ok=False)
            (output / "profile.json").write_text(payload, encoding="utf-8")
        else:
            typer.echo(payload)
    except (ValueError, OSError, PolicyViolation) as exc:
        error(exc)


@app.command()
def analyze(
    source: Input,
    config: ConfigOption = None,
    output: OutputOption = None,
    mission: Annotated[Path | None, typer.Option(exists=True)] = None,
    no_llm: Annotated[bool, typer.Option("--no-llm")] = False,
    prior: Annotated[
        Path | None,
        typer.Option(exists=True, help="Prior assessment.json or assessment_history.json"),
    ] = None,
    baseline: Annotated[
        str | None, typer.Option(help="Create an immutable named baseline after gates pass")
    ] = None,
    compare_baseline: Annotated[
        str | None, typer.Option(help="Compare against a named baseline in --prior history")
    ] = None,
) -> None:
    """Assess data and produce the canonical evidence, reports and control decision."""
    try:
        cfg = config_for(config, no_llm)
        context = MissionContext.model_validate(load_yaml(mission)) if mission else None
        run = AssessmentController(cfg).run(
            source,
            context,
            load_prior(prior) if prior else None,
            baseline=baseline,
            compare_baseline=compare_baseline,
        )
        destination = write_reports(run, output or Path(cfg.runtime.output_directory))
        typer.echo(
            f"{run.iterations[-1].outcome}: {len(run.assessment.datasets)} datasets. Reports: {destination}"
        )
    except (ValueError, OSError, PolicyViolation) as exc:
        error(exc)


@app.command()
def resolve(
    assessment: Input,
    answers: Input,
    source: Annotated[
        Path,
        typer.Option(exists=True, dir_okay=False, help="Original source file (hash is checked)"),
    ],
    output: OutputOption = None,
    config: ConfigOption = None,
    baseline: Annotated[str | None, typer.Option()] = None,
) -> None:
    """Record SME answers, preserve assertion history and reassess affected components."""
    try:
        prior = load_prior(assessment)
        previous = prior.assessment if isinstance(prior, AssessmentRun) else prior
        cfg = config_for(config) if config else Config.model_validate(previous.configuration)
        payload: Any = load_yaml(answers)
        if isinstance(payload, dict) and "answers" in payload:
            resolutions = []
            for question_id, answer in payload["answers"].items():
                resolutions.append(
                    Resolution(
                        resolution_id=stable_id("resolution", question_id, answer),
                        question_id=question_id,
                        value=answer["answer"],
                        provided_by=answer["answered_by"],
                        authoritative=answer.get("authoritative", False),
                        authority=answer.get("authority"),
                        source_reference=answer.get("source_reference"),
                    )
                )
        else:
            resolutions = [Resolution.model_validate(r) for r in payload["resolutions"]]
        from data_maturity.util import file_hash

        if file_hash(source) != previous.source.sha256:
            raise ValueError("Source changed; run analyze --prior before resolving questions")
        run = AssessmentController(cfg).run(
            source, prior_assessment=prior, resolutions=resolutions, baseline=baseline
        )
        destination = write_reports(run, output or Path("resolved-output"))
        typer.echo(f"{run.iterations[-1].outcome}: resolution history saved to {destination}")
    except (ValueError, OSError, PolicyViolation, KeyError, TypeError) as exc:
        error(exc)


if __name__ == "__main__":
    app()
