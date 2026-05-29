"""
OpenForge CLI — entry point for all commands.

Commands:
  init    → scaffold a new project
  run     → execute a pipeline.yaml
  status  → show project state

All commands are thin shells that delegate to the relevant
agents and pipeline runner. Business logic never lives here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(
    name="openforge",
    help="AI-native data engineering platform. CSV → validated, documented tables.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

@app.command()
def init(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name (defaults to directory name)"),
    force: bool = typer.Option(False, "--force", "-f", help="Reinitialize an existing project"),
):
    """Initialize a new OpenForge project in the current directory."""
    from openforge.metadata import store
    from openforge.metadata.models import ProjectMetadata

    project_name = name or Path.cwd().name
    openforge_dir = Path(".openforge")

    if store.is_initialized() and not force:
        console.print("[yellow]⚠ Project already initialized.[/] Use --force to reinitialize.")
        raise typer.Exit(1)

    # Create .openforge/
    openforge_dir.mkdir(exist_ok=True)

    # Persist initial metadata
    meta = ProjectMetadata(project_name=project_name)
    store.save(meta)
    console.print(f"  [green]✓[/] Created [dim].openforge/metadata.json[/]")

    # Create sample_data/ if not present
    sample_dir = Path("sample_data")
    if not sample_dir.exists():
        sample_dir.mkdir()
        console.print(f"  [green]✓[/] Created [dim]sample_data/[/]  ← drop your CSV files here")

    # Create pipeline.yaml if not present
    pipeline_path = Path("pipeline.yaml")
    if not pipeline_path.exists():
        csvs = sorted(Path(".").glob("*.csv")) + sorted(sample_dir.glob("*.csv"))
        pipeline_path.write_text(_generate_pipeline_yaml(project_name, csvs))
        console.print(f"  [green]✓[/] Created [dim]pipeline.yaml[/]")

    console.print(
        Panel(
            f"[bold green]✓ Project initialized:[/] [bold]{project_name}[/]\n\n"
            "Next steps:\n"
            "  [cyan]1.[/] Drop CSV files in [bold]sample_data/[/]\n"
            "  [cyan]2.[/] Edit [bold]pipeline.yaml[/] to add quality rules\n"
            "  [cyan]3.[/] Run [bold]openforge run[/]",
            border_style="green",
            padding=(1, 2),
        )
    )


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

@app.command()
def run(
    pipeline: str = typer.Argument("pipeline.yaml", help="Path to pipeline.yaml"),
    docs: bool = typer.Option(
        False, "--docs", "-d",
        help="Generate AI documentation for tables (requires ANTHROPIC_API_KEY)"
    ),
    mock: bool = typer.Option(
        False, "--mock",
        help="Simulate AI documentation without calling the API (demo / dev mode)"
    ),
):
    """Execute a pipeline — ingest, validate, and optionally document your data."""
    from openforge.metadata import store
    from openforge.pipeline import runner

    if not store.is_initialized():
        console.print("[red]✗ No project found.[/] Run [bold]openforge init[/] first.")
        raise typer.Exit(1)

    success = runner.run(pipeline, use_llm=docs or mock, mock=mock)
    if not success:
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# chat
# ---------------------------------------------------------------------------

@app.command()
def chat(
    mock: bool = typer.Option(
        False, "--mock",
        help="Use mock AI responses (demo mode, no API key needed)"
    ),
):
    """Start a conversational session — describe your pipeline in natural language."""
    from openforge.metadata import store
    from openforge.llm import chat as chat_engine
    from rich.markdown import Markdown
    from rich.rule import Rule
    import yaml as _yaml

    if not store.is_initialized():
        console.print("[red]✗ No project found.[/] Run [bold]openforge init[/] first.")
        raise typer.Exit(1)

    meta = store.load()

    # Collect source files
    source_files = sorted(Path("sample_data").glob("*.csv")) if Path("sample_data").exists() else []

    # Build system prompt with full project context
    system = chat_engine.build_system_prompt(meta, source_files)

    # Header
    mock_tag = "  [dim](mock mode — responses are simulated)[/]" if mock else ""
    console.print()
    console.print(
        f"[bold blue]◆ OpenForge Chat[/] · [bold]{meta.project_name}[/]{mock_tag}"
    )
    console.print(
        f"  [dim]{len(meta.tables)} table(s) in context · "
        f"type your request, [bold]exit[/] to quit[/]"
    )
    console.print()

    history: list[dict] = []

    while True:
        # Prompt
        try:
            user_input = console.input("[bold cyan]you[/] › ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Session ended.[/]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "sair", "q"):
            console.print("[dim]Session ended.[/]")
            break

        # Add to history
        history.append({"role": "user", "content": user_input})

        # Get response
        try:
            with console.status("[dim]Thinking...[/]"):
                response = chat_engine.send(
                    messages=history,
                    system=system,
                    mock=mock,
                    user_input=user_input,
                )
        except EnvironmentError as e:
            console.print(f"\n[red]✗ {e}[/]")
            console.print("[dim]Tip: run with [bold]--mock[/] for demo mode[/]\n")
            history.pop()
            continue
        except Exception as e:
            console.print(f"\n[red]✗ Error: {e}[/]\n")
            history.pop()
            continue

        # Add assistant response to history
        history.append({"role": "assistant", "content": response})

        # Render response
        console.print()
        console.print("[bold green]openforge[/] ›")
        console.print(Markdown(response))
        console.print()

        # If response contains a pipeline YAML, offer to save it
        pipeline_yaml = chat_engine.extract_pipeline_yaml(response)
        if pipeline_yaml:
            save = console.input(
                "[dim]Pipeline generated. Save as[/] [bold]pipeline.yaml[/][dim]? (y/N)[/] › "
            ).strip().lower()
            if save in ("y", "yes", "sim", "s"):
                # Parse to validate before saving
                try:
                    _yaml.safe_load(pipeline_yaml)
                    Path("pipeline.yaml").write_text(pipeline_yaml)
                    console.print("[green]✓ Saved pipeline.yaml[/]  Run: [bold]openforge run[/]")
                except Exception as e:
                    console.print(f"[red]✗ Invalid YAML: {e}[/]")
            console.print()


# ---------------------------------------------------------------------------
# heal
# ---------------------------------------------------------------------------

@app.command()
def heal(
    table: Optional[str] = typer.Argument(None, help="Table to heal (defaults to last failed table)"),
):
    """Diagnose quality failures and get fix proposals for your data."""
    from openforge.metadata import store
    from openforge.agents import healer
    from rich.panel import Panel

    if not store.is_initialized():
        console.print("[red]✗ No project found.[/] Run [bold]openforge init[/] first.")
        raise typer.Exit(1)

    meta = store.load()

    if not meta.quality_results:
        console.print("[yellow]⚠ No quality results found.[/] Run [bold]openforge run[/] first.")
        raise typer.Exit(1)

    # Find target table
    target = table
    if not target:
        # Pick the table with the lowest quality score
        target = min(meta.quality_results, key=lambda t: meta.quality_results[t].score)

    result = meta.quality_results.get(target)
    if not result:
        console.print(f"[red]✗ No quality results for table '{target}'.[/]")
        raise typer.Exit(1)

    schema = meta.tables.get(target)
    if not schema:
        console.print(f"[red]✗ Table '{target}' not found in metadata.[/]")
        raise typer.Exit(1)

    if result.passed_all:
        console.print(
            f"\n[green]✓ Table [bold]{target}[/] is healthy[/] — "
            f"quality score [bold]{result.score}%[/] · all {result.total} checks passed.\n"
        )
        return

    # Run analysis
    report = healer.analyze(result, schema)

    console.print(f"\n[bold blue]◆ OpenForge Heal[/] · [bold]{target}[/]\n")
    console.print(
        f"  Quality score: [red]{report.quality_score}%[/]  ·  "
        f"[red]{report.critical_count} critical[/]  ·  "
        f"[yellow]{report.warning_count} warning[/]\n"
    )

    for i, proposal in enumerate(report.proposals, 1):
        severity_color = "red" if proposal.severity == "critical" else "yellow"
        severity_icon = "✗" if proposal.severity == "critical" else "⚠"

        console.print(
            Panel(
                f"[bold]{proposal.column}[/]  ·  rule: [dim]{proposal.rule}[/]  ·  "
                f"[{severity_color}]{severity_icon} {proposal.severity.upper()}[/]\n\n"
                f"[bold]Diagnosis:[/] {proposal.diagnosis}\n\n"
                f"[bold]Proposal:[/]  {proposal.proposal}",
                title=f"[{severity_color}]Issue {i} of {len(report.proposals)}[/]",
                border_style=severity_color,
                padding=(0, 1),
            )
        )

    console.print(
        f"\n[dim]Fix the issues above, then re-run: [bold]openforge run[/][/]\n"
    )


# ---------------------------------------------------------------------------
# inspect
# ---------------------------------------------------------------------------

@app.command()
def inspect(
    table: str = typer.Argument(..., help="Table name to profile"),
):
    """Show detailed column statistics for a table in the warehouse."""
    from openforge.metadata import store
    from openforge.agents import profiler
    from rich.table import Table as RichTable

    if not store.is_initialized():
        console.print("[red]✗ No project found.[/] Run [bold]openforge init[/] first.")
        raise typer.Exit(1)

    meta = store.load()
    if table not in meta.tables:
        available = ", ".join(meta.tables.keys()) or "none"
        console.print(f"[red]✗ Table '{table}' not found.[/] Available: {available}")
        raise typer.Exit(1)

    with console.status(f"Profiling [bold]{table}[/]..."):
        report = profiler.profile(table)

    console.print(f"\n[bold blue]◆ OpenForge Inspect[/] · [bold]{table}[/]")
    console.print(f"  [dim]{report.row_count:,} rows · {report.column_count} columns[/]\n")

    t = RichTable(show_header=True, header_style="bold cyan", border_style="dim")
    t.add_column("Column")
    t.add_column("Type", style="dim")
    t.add_column("Nulls", justify="right")
    t.add_column("Distinct", justify="right")
    t.add_column("Min", justify="right")
    t.add_column("Avg", justify="right")
    t.add_column("Max", justify="right")
    t.add_column("Top Values", max_width=40)

    for col in report.columns:
        null_str = (
            f"[red]{col.null_count}[/] [dim]({col.null_pct}%)[/]"
            if col.null_count > 0
            else f"[green]0[/]"
        )
        distinct_str = f"{col.distinct_count:,} [dim]({col.distinct_pct}%)[/]"

        min_str = str(col.min_val) if col.min_val is not None else "[dim]—[/]"
        avg_str = str(col.avg_val) if col.avg_val is not None else "[dim]—[/]"
        max_str = str(col.max_val) if col.max_val is not None else "[dim]—[/]"

        top = ", ".join(
            f"{v}×{c}" for v, c in col.top_values[:3]
        ) if col.top_values else "—"

        t.add_row(
            f"[bold]{col.name}[/]",
            col.type,
            null_str,
            distinct_str,
            min_str,
            avg_str,
            max_str,
            f"[dim]{top}[/]",
        )

    console.print(t)
    console.print()


# ---------------------------------------------------------------------------
# connect
# ---------------------------------------------------------------------------

@app.command()
def connect(
    connector_type: str = typer.Argument("duckdb", help="Connector to test: duckdb, trino"),
    host: str = typer.Option("localhost", "--host", help="Host (Trino)"),
    port: int = typer.Option(8080, "--port", help="Port (Trino default: 8080)"),
    user: str = typer.Option("admin", "--user", help="Username (Trino)"),
    catalog: str = typer.Option("hive", "--catalog", help="Catalog (Trino)"),
    schema: str = typer.Option("default", "--schema", help="Schema (Trino)"),
    http_scheme: str = typer.Option("http", "--http-scheme", help="http or https (Trino)"),
    password: str = typer.Option("", "--password", help="Password (Trino, optional)"),
):
    """Test a connector connection and show available tables."""
    from openforge.connectors.registry import get_connector
    from openforge.connectors.trino_connector import TrinoConfig, TrinoConnector
    from rich.table import Table as RichTable

    ct = connector_type.lower().strip()

    console.print(f"\n[bold blue]◆ OpenForge Connect[/] · [bold]{ct}[/]\n")

    try:
        if ct == "duckdb":
            connector = get_connector({"type": "duckdb"})
            with console.status("Testing DuckDB connection..."):
                ok = connector.test_connection()
            console.print(f"  [green]✓ DuckDB connected[/]  ·  warehouse: [dim].openforge/warehouse.db[/]")
            connector.close()

        elif ct == "trino":
            cfg = TrinoConfig(
                host=host, port=port, user=user,
                catalog=catalog, schema=schema,
                http_scheme=http_scheme, password=password,
            )
            connector = TrinoConnector(cfg)

            with console.status(f"Connecting to Trino at [dim]{http_scheme}://{host}:{port}[/]..."):
                ok = connector.test_connection()

            console.print(f"  [green]✓ Trino connected[/]  ·  [dim]{http_scheme}://{host}:{port}[/]")
            console.print(f"  User: [dim]{user}[/]  ·  Catalog: [dim]{catalog}[/]  ·  Schema: [dim]{schema}[/]")

            # Show catalogs
            with console.status("Listing catalogs..."):
                catalogs = connector.list_catalogs()
            console.print(f"\n  [bold]Catalogs:[/] {', '.join(catalogs)}")

            # Show tables in configured schema
            try:
                with console.status(f"Listing tables in {catalog}.{schema}..."):
                    tables = connector.list_tables()
                if tables:
                    t = RichTable(show_header=True, header_style="bold cyan", border_style="dim")
                    t.add_column("Table")
                    t.add_column("Catalog", style="dim")
                    t.add_column("Schema", style="dim")
                    for tbl in tables:
                        t.add_row(tbl, catalog, schema)
                    console.print()
                    console.print(t)
                else:
                    console.print(f"\n  [dim]No tables in {catalog}.{schema}[/]")
            except Exception:
                pass  # Schema might be empty — not a failure

            connector.close()

            # Print pipeline.yaml snippet
            console.print(f"""
[dim]Add this to your pipeline.yaml to use Trino:[/]

  [bold]connector:[/]
    type: trino
    host: {host}
    port: {port}
    user: {user}
    catalog: {catalog}
    schema: {schema}
    http_scheme: {http_scheme}
""")

        else:
            available = "duckdb, trino"
            console.print(f"[red]✗ Unknown connector: '{ct}'.[/] Available: {available}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"\n  [red]✗ Connection failed:[/] {e}")
        if ct == "trino":
            console.print(
                "\n  [dim]Make sure Trino is running. Quick start with Docker:\n"
                "  docker run -d --name trino -p 8080:8080 trinodb/trino[/]"
            )
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# ui
# ---------------------------------------------------------------------------

@app.command()
def ui(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(7433, "--port", "-p", help="Port to listen on"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open browser automatically"),
):
    """Start the web dashboard (http://localhost:7433)."""
    try:
        import uvicorn
    except ImportError:
        console.print("[red]✗ uvicorn not installed.[/] Run: pip install uvicorn")
        raise typer.Exit(1)

    from openforge.metadata import store
    if not store.is_initialized():
        console.print("[red]✗ No project found.[/] Run [bold]openforge init[/] first.")
        raise typer.Exit(1)

    url = f"http://{host}:{port}"
    console.print(f"\n[bold blue]◆ OpenForge UI[/]  →  [bold cyan]{url}[/]")
    console.print("  [dim]Press Ctrl+C to stop[/]\n")

    if open_browser:
        import threading, webbrowser, time
        def _open():
            time.sleep(0.8)
            webbrowser.open(url)
        threading.Thread(target=_open, daemon=True).start()

    uvicorn.run(
        "openforge.ui.server:app",
        host=host,
        port=port,
        log_level="warning",
        reload=False,
    )


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

@app.command()
def status():
    """Show current project state: tables, quality scores, docs coverage."""
    from openforge.metadata import store

    if not store.is_initialized():
        console.print("[red]✗ No project found.[/] Run [bold]openforge init[/] first.")
        raise typer.Exit(1)

    meta = store.load()

    console.print(f"\n[bold blue]◆ OpenForge[/] · [bold]{meta.project_name}[/]  v{meta.version}")
    console.print(f"  [dim]Last updated: {meta.updated_at.strftime('%Y-%m-%d %H:%M UTC')}[/]\n")

    if not meta.tables:
        console.print("  [dim]No tables yet. Run [bold]openforge run[/] to get started.[/]\n")
        return

    t = Table(show_header=True, header_style="bold cyan", border_style="dim")
    t.add_column("Table", style="bold")
    t.add_column("Rows", justify="right")
    t.add_column("Columns", justify="right")
    t.add_column("Quality", justify="right")
    t.add_column("Checks", justify="right")
    t.add_column("Docs", justify="center")
    t.add_column("Source", style="dim")

    total_rows = 0
    for name, table in meta.tables.items():
        qr = meta.quality_results.get(name)
        q_str = f"{qr.score}%" if qr else "—"
        q_style = "green" if qr and qr.passed_all else ("red" if qr else "dim")
        checks_str = f"{qr.passed}/{qr.total}" if qr else "—"
        docs_str = "[green]✓[/]" if any(c.description for c in table.columns) else "[dim]—[/]"
        source = Path(table.source_path).name if table.source_path else "—"
        total_rows += table.row_count

        t.add_row(
            name,
            f"[cyan]{table.row_count:,}[/]",
            str(len(table.columns)),
            f"[{q_style}]{q_str}[/]",
            checks_str,
            docs_str,
            source,
        )

    console.print(t)
    total_runs = len(meta.runs)
    last_run = meta.runs[-1] if meta.runs else None
    run_str = f"  [dim]{total_runs} run(s)"
    if last_run:
        run_str += f" · last: {last_run.started_at.strftime('%Y-%m-%d %H:%M UTC')}"
        run_str += f" · {'[green]success[/]' if last_run.success else '[red]failed[/]'}"
    run_str += f" · {len(meta.tables)} table(s) · {total_rows:,} total rows[/]"
    console.print(run_str + "\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_pipeline_yaml(project_name: str, csvs: list[Path]) -> str:
    slug = project_name.lower().replace(" ", "_").replace("-", "_")
    lines = [
        f"name: {slug}_pipeline",
        'version: "0.1.0"',
        f'description: "Pipeline for {project_name}"',
        "",
        "sources:",
    ]

    if csvs:
        for csv in csvs[:3]:
            stem = csv.stem.lower().replace("-", "_").replace(" ", "_")
            lines += [
                f"  - name: {stem}_raw",
                f"    type: csv",
                f"    path: {csv}",
            ]
    else:
        lines += [
            "  - name: my_data_raw",
            "    type: csv",
            "    path: sample_data/my_data.csv",
        ]

    lines += ["", "steps:"]

    if csvs:
        for csv in csvs[:3]:
            stem = csv.stem.lower().replace("-", "_").replace(" ", "_")
            lines += [
                "",
                f"  - name: ingest_{stem}",
                f"    type: ingest",
                f"    source: {stem}_raw",
                f"    target: {stem}",
                "",
                f"  - name: validate_{stem}",
                f"    type: quality",
                f"    table: {stem}",
                f"    rules:",
                f"      - column: id  # replace with your actual column",
                f"        checks: [not_null, unique]",
                "",
                f"  - name: document_{stem}",
                f"    type: docs",
                f"    table: {stem}",
                f"    use_llm: true",
            ]
    else:
        lines += [
            "",
            "  - name: ingest_my_data",
            "    type: ingest",
            "    source: my_data_raw",
            "    target: my_data",
            "",
            "  - name: validate_my_data",
            "    type: quality",
            "    table: my_data",
            "    rules: []",
        ]

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    app()
