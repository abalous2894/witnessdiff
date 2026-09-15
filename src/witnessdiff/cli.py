from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from witnessdiff.behavioral_suite import run_behavioral_suite
from witnessdiff.claim_parser import load_evidence_bundle
from witnessdiff.comparators import compare_witness_integrity
from witnessdiff.reports import (
    build_suite_summary,
    compare_to_baseline,
    load_suite_baseline,
    write_suite_report,
)
from witnessdiff.suite import run_evidence_suite
from witnessdiff.trace_parser import load_reference_trace

app = typer.Typer(
    name="witnessdiff",
    help="Compare instrumented reference traces with exported evidence bundles.",
    add_completion=False,
)
console = Console()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_evidence_dir() -> Path:
    return _repo_root() / "fixtures" / "evidence"


def _default_behavioral_dir() -> Path:
    return _repo_root() / "fixtures" / "behavioral"


def _default_baseline_path(suite: str) -> Path:
    return _repo_root() / "reports" / "baseline" / f"{suite}.json"


def _run_suite_cmd(
    title: str,
    suite_name: str,
    passed: int,
    failed: int,
    messages: list[str],
    case_results: dict,
    output: Path | None,
    baseline: Path | None,
) -> None:
    table = Table(title=title)
    table.add_column("Result")
    for message in messages:
        table.add_row(message)
    console.print(table)
    console.print(f"\nSummary: {passed} passed, {failed} failed")

    summary = build_suite_summary(suite_name, case_results, passed, failed)  # type: ignore[arg-type]
    if output:
        write_suite_report(summary, output)
        console.print(f"Wrote suite report to {output}")

    baseline_failed = False
    if baseline:
        if not baseline.exists():
            console.print(f"[yellow]Baseline not found at {baseline}; skipping comparison[/yellow]")
        else:
            errors = compare_to_baseline(case_results, load_suite_baseline(baseline))
            if errors:
                baseline_failed = True
                console.print("[red]Baseline regression detected:[/red]")
                for error in errors:
                    console.print(f"  - {error}")

    raise typer.Exit(code=1 if failed or baseline_failed else 0)


@app.command("compare")
def compare_cmd(
    reference: Path = typer.Argument(..., help="Path to reference trace JSON"),
    evidence: Path = typer.Argument(..., help="Path to evidence bundle JSON"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write report JSON to path"),
) -> None:
    """Compare one reference trace against one evidence bundle."""
    ref = load_reference_trace(reference)
    ev = load_evidence_bundle(evidence)
    report = compare_witness_integrity(ref, ev)

    payload = report.model_dump(mode="json", by_alias=True)
    text = json.dumps(payload, indent=2)
    if output:
        output.write_text(text + "\n", encoding="utf-8")
    console.print(text)

    raise typer.Exit(code=0 if report.ok else 1)


@app.command("run-evidence-suite")
def run_evidence_suite_cmd(
    fixtures_dir: Path = typer.Option(
        _default_evidence_dir(),
        "--fixtures-dir",
        help="Directory containing *.reference.json fixture triples",
    ),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write suite report JSON"),
    baseline: Path | None = typer.Option(
        None,
        "--baseline",
        help="Compare results to a committed suite baseline JSON",
    ),
) -> None:
    """Run all evidence-integrity fixtures and exit non-zero on regression."""
    passed, failed, messages, case_results = run_evidence_suite(fixtures_dir)
    baseline_path = baseline or _default_baseline_path("evidence")
    _run_suite_cmd(
        "WitnessDiff evidence-integrity suite",
        "evidence",
        passed,
        failed,
        messages,
        case_results,
        output,
        baseline_path,
    )


@app.command("run-behavioral-suite")
def run_behavioral_suite_cmd(
    fixtures_dir: Path = typer.Option(
        _default_behavioral_dir(),
        "--fixtures-dir",
        help="Directory containing *.scenario.json fixture pairs",
    ),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write suite report JSON"),
    baseline: Path | None = typer.Option(
        None,
        "--baseline",
        help="Compare results to a committed suite baseline JSON",
    ),
) -> None:
    """Run all behavioral policy fixtures and exit non-zero on regression."""
    passed, failed, messages, case_results = run_behavioral_suite(fixtures_dir)
    baseline_path = baseline or _default_baseline_path("behavioral")
    _run_suite_cmd(
        "WitnessDiff behavioral suite",
        "behavioral",
        passed,
        failed,
        messages,
        case_results,
        output,
        baseline_path,
    )


@app.command("run-all-suites")
def run_all_suites_cmd(
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        help="Directory for suite report JSON files",
    ),
) -> None:
    """Run behavioral and evidence suites with baseline comparison."""
    out = output_dir or (_repo_root() / "reports" / "local")
    exit_code = 0

    for suite_name, runner, fixtures_dir in (
        ("behavioral", run_behavioral_suite, _default_behavioral_dir()),
        ("evidence", run_evidence_suite, _default_evidence_dir()),
    ):
        passed, failed, messages, case_results = runner(fixtures_dir)
        baseline_path = _default_baseline_path(suite_name)
        summary = build_suite_summary(suite_name, case_results, passed, failed)  # type: ignore[arg-type]
        write_suite_report(summary, out / f"{suite_name}.json")

        baseline_errors: list[str] = []
        if baseline_path.exists():
            baseline_errors = compare_to_baseline(case_results, load_suite_baseline(baseline_path))

        console.print(f"\n[bold]{suite_name}[/bold]: {passed} passed, {failed} failed")
        for message in messages:
            console.print(f"  {message}")
        for error in baseline_errors:
            console.print(f"  [red]baseline: {error}[/red]")

        if failed or baseline_errors:
            exit_code = 1

    raise typer.Exit(code=exit_code)


@app.command("serve")
def serve_cmd(
    host: str = typer.Option("127.0.0.1", help="API bind host"),
    port: int = typer.Option(8080, help="API bind port"),
    reload: bool = typer.Option(False, help="Enable autoreload (dev only)"),
) -> None:
    """Start the WitnessDiff FastAPI server."""
    import uvicorn

    uvicorn.run(
        "witnessdiff.api.main:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    app()
