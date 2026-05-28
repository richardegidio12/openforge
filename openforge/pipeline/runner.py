"""
Pipeline Runner — reads pipeline.yaml and executes steps in order.

Each step type maps to a Forge Agent:
  ingest  → Schema Agent + Ingestion Agent
  quality → Quality Agent
  docs    → LLM Client (optional, requires --docs flag)
  transform → (Phase 2)
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

from ..metadata import store
from ..metadata.models import PipelineDefinition, PipelineStep, PipelineSource, RunLog
from ..agents import schema as schema_agent
from ..agents import ingestion as ingestion_agent
from ..agents import quality as quality_agent

console = Console()


def load_pipeline(pipeline_path: str) -> PipelineDefinition:
    path = Path(pipeline_path)
    if not path.exists():
        raise FileNotFoundError(f"Pipeline file not found: {pipeline_path}")
    data = yaml.safe_load(path.read_text())
    return PipelineDefinition.model_validate(data)


def run(pipeline_path: str, use_llm: bool = False, mock: bool = False) -> bool:
    """
    Execute a pipeline. Returns True if all steps passed.

    Args:
        pipeline_path: Path to pipeline.yaml.
        use_llm: If True, doc generation steps are active (real or mock).
        mock: If True, doc generation uses mock responses instead of the real API.
    """
    pipeline = load_pipeline(pipeline_path)
    meta = store.load()

    console.print(f"\n[bold blue]◆ OpenForge[/] · [bold]{pipeline.name}[/]  v{pipeline.version}")
    if pipeline.description:
        console.print(f"  [dim]{pipeline.description}[/]")
    console.print()

    sources: dict[str, PipelineSource] = {s.name: s for s in pipeline.sources}

    run_log = RunLog(pipeline=pipeline.name, started_at=datetime.utcnow())
    success = True
    steps_run = 0

    for step in pipeline.steps:
        console.print(f"  [dim]▸[/] [bold]{step.name}[/]  [dim][{step.type}][/]")
        try:
            if step.type == "ingest":
                _run_ingest(step, sources)
            elif step.type == "quality":
                ok = _run_quality(step)
                if not ok:
                    success = False
            elif step.type == "docs":
                _run_docs(step, use_llm, mock)
            elif step.type == "transform":
                console.print("    [yellow]⚠ transform steps coming in Phase 2[/]")
            else:
                console.print(f"    [yellow]⚠ Unknown step type: {step.type}[/]")
            steps_run += 1
        except Exception as e:
            console.print(f"    [red]✗ {e}[/]")
            success = False

    # Persist run log
    run_log.finished_at = datetime.utcnow()
    run_log.success = success
    run_log.steps_run = steps_run
    meta = store.load()
    meta.runs.append(run_log)
    store.save(meta)

    _print_summary()
    return success


# ---------------------------------------------------------------------------
# Step executors
# ---------------------------------------------------------------------------

def _run_ingest(step: PipelineStep, sources: dict[str, PipelineSource]) -> None:
    src = sources.get(step.source)
    if not src:
        raise ValueError(f"Source '{step.source}' not found in pipeline sources")

    with console.status(f"    Inferring schema from [dim]{src.path}[/]..."):
        table_schema = schema_agent.infer(src.path, step.target or src.name)

    with console.status(f"    Loading into warehouse..."):
        row_count = ingestion_agent.load(table_schema)

    table_schema.row_count = row_count
    store.upsert_table(table_schema)

    console.print(
        f"    [green]✓[/] [bold]{table_schema.name}[/] loaded · "
        f"[cyan]{row_count:,}[/] rows · "
        f"[cyan]{len(table_schema.columns)}[/] columns"
    )


def _run_quality(step: PipelineStep) -> bool:
    if not step.rules:
        console.print("    [dim]⊘ No rules defined — skipping[/]")
        return True

    with console.status(f"    Running {len(step.rules)} check(s)..."):
        result = quality_agent.run_checks(step.table, step.rules)

    store.upsert_quality(result)

    icon = "[green]✓[/]" if result.passed_all else "[red]✗[/]"
    console.print(
        f"    {icon} [bold]{step.table}[/] · "
        f"{result.passed}/{result.total} checks passed · "
        f"score [bold]{result.score}%[/]"
    )

    if not result.passed_all:
        for d in result.details:
            if d["status"] == "fail":
                console.print(f"      [red]✗[/] {d['column']}.{d['rule']}: [dim]{d['message']}[/]")

    return result.passed_all


def _run_docs(step: PipelineStep, use_llm: bool, mock: bool = False) -> None:
    if not use_llm:
        console.print("    [dim]⊘ AI docs skipped · run with [bold]--docs[/] to enable[/]")
        return

    from ..llm import client as llm

    meta = store.load()
    table = meta.tables.get(step.table)
    if not table:
        raise ValueError(
            f"Table '{step.table}' not found in metadata. "
            "Run the ingest step before docs."
        )

    label = "Generating docs [dim](mock mode)[/]..." if mock else "Generating docs with AI..."
    with console.status(f"    {label}"):
        docs = llm.generate_table_docs(table, mock=mock)

    table.description = docs.get("table_description", "")
    col_docs: dict = docs.get("columns", {})
    for col in table.columns:
        if col.name in col_docs:
            col.description = col_docs[col.name]

    store.upsert_table(table)
    described = sum(1 for c in table.columns if c.description)
    mock_tag = " [dim](mock)[/]" if mock else ""
    console.print(
        f"    [green]✓[/] Docs generated for [bold]{step.table}[/]{mock_tag} · "
        f"[cyan]{described}[/] columns described"
    )


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

def _print_summary() -> None:
    meta = store.load()
    if not meta.tables:
        return

    console.print()
    t = Table(
        title="[bold]Pipeline Result[/]",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    t.add_column("Table", style="bold")
    t.add_column("Rows", justify="right")
    t.add_column("Columns", justify="right")
    t.add_column("Quality", justify="right")
    t.add_column("Docs", justify="center")

    for name, table in meta.tables.items():
        qr = meta.quality_results.get(name)
        if qr:
            q_style = "green" if qr.passed_all else "red"
            q_str = f"[{q_style}]{qr.score}%[/]"
        else:
            q_str = "[dim]—[/]"

        docs_str = "[green]✓[/]" if any(c.description for c in table.columns) else "[dim]—[/]"

        t.add_row(
            name,
            f"[cyan]{table.row_count:,}[/]",
            str(len(table.columns)),
            q_str,
            docs_str,
        )

    console.print(t)
    console.print()
