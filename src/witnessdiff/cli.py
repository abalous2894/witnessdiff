from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from witnessdiff.claim_parser import load_evidence_bundle
from witnessdiff.comparators import compare_witness_integrity
from witnessdiff.suite import run_evidence_suite
from witnessdiff.trace_parser import load_reference_trace

app = typer.Typer(
    name="witnessdiff",
    help="Compare instrumented reference traces with exported evidence bundles.",
    add_completion=False,
)
console = Console()


def _default_fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "fixtures" / "evidence"


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

    payload = report.model_dump(mode="json")
    text = json.dumps(payload, indent=2)
    if output:
        output.write_text(text + "\n", encoding="utf-8")
    console.print(text)

    raise typer.Exit(code=0 if report.ok else 1)


@app.command("run-evidence-suite")
def run_evidence_suite_cmd(
    fixtures_dir: Path = typer.Option(
        _default_fixtures_dir(),
        "--fixtures-dir",
        help="Directory containing *.reference.json fixture triples",
    ),
) -> None:
    """Run all evidence-integrity fixtures and exit non-zero on regression."""
    passed, failed, messages = run_evidence_suite(fixtures_dir)

    table = Table(title="WitnessDiff evidence-integrity suite")
    table.add_column("Result")
    for message in messages:
        table.add_row(message)
    console.print(table)
    console.print(f"\nSummary: {passed} passed, {failed} failed")

    raise typer.Exit(code=1 if failed else 0)


if __name__ == "__main__":
    app()
