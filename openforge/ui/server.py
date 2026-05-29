"""
OpenForge Web UI — FastAPI dashboard.

Serves a browser-based view of the project metadata:
  /           → dashboard (tables, quality, recent runs)
  /table/<n>  → table detail (columns, quality, docs, profile)
  /api/status → JSON — full project state
  /api/tables → JSON — all tables
  /api/quality→ JSON — all quality results

Start: openforge ui
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..metadata import store

TEMPLATES_DIR = Path(__file__).parent / "templates"

app = FastAPI(title="OpenForge UI", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ---------------------------------------------------------------------------
# HTML routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        meta = store.load()
    except FileNotFoundError:
        return HTMLResponse(_not_initialized_html(), status_code=200)

    tables_data = []
    for name, table in meta.tables.items():
        qr = meta.quality_results.get(name)
        tables_data.append({
            "name": name,
            "rows": table.row_count,
            "columns": len(table.columns),
            "quality_score": qr.score if qr else None,
            "quality_passed": qr.passed_all if qr else None,
            "has_docs": any(c.description for c in table.columns),
            "source": Path(table.source_path).name if table.source_path else "—",
        })

    runs = list(reversed(meta.runs[-5:]))  # last 5, newest first
    runs_data = [
        {
            "pipeline": r.pipeline,
            "started_at": r.started_at.strftime("%Y-%m-%d %H:%M"),
            "success": r.success,
            "steps": r.steps_run,
        }
        for r in runs
    ]

    total_rows = sum(t["rows"] for t in tables_data)
    avg_quality = (
        sum(t["quality_score"] for t in tables_data if t["quality_score"] is not None)
        / max(1, sum(1 for t in tables_data if t["quality_score"] is not None))
    )

    return templates.TemplateResponse(request=request, name="index.html", context={
        "project_name": meta.project_name,
        "version": meta.version,
        "tables": tables_data,
        "runs": runs_data,
        "total_tables": len(tables_data),
        "total_rows": total_rows,
        "avg_quality": round(avg_quality, 1) if tables_data else None,
        "total_runs": len(meta.runs),
    })


@app.get("/table/{table_name}", response_class=HTMLResponse)
async def table_detail(request: Request, table_name: str):
    try:
        meta = store.load()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not initialized")

    table = meta.tables.get(table_name)
    if not table:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

    qr = meta.quality_results.get(table_name)

    columns_data = [
        {
            "name": c.name,
            "type": c.type,
            "nullable": c.nullable,
            "null_count": c.null_count,
            "null_pct": round((c.null_count / table.row_count) * 100, 1) if table.row_count > 0 else 0,
            "distinct_count": c.distinct_count,
            "sample_values": c.sample_values[:3],
            "description": c.description,
        }
        for c in table.columns
    ]

    checks_data = []
    if qr:
        for d in qr.details:
            checks_data.append({
                "column": d["column"],
                "rule": d["rule"],
                "status": d["status"],
                "message": d["message"],
            })

    return templates.TemplateResponse(request=request, name="table.html", context={
        "project_name": meta.project_name,
        "version": meta.version,
        "table_name": table_name,
        "row_count": table.row_count,
        "description": table.description,
        "source": Path(table.source_path).name if table.source_path else "—",
        "columns": columns_data,
        "quality": {
            "score": qr.score,
            "passed": qr.passed,
            "failed": qr.failed,
            "total": qr.total,
            "passed_all": qr.passed_all,
        } if qr else None,
        "checks": checks_data,
    })


# ---------------------------------------------------------------------------
# JSON API routes
# ---------------------------------------------------------------------------

@app.get("/api/status")
async def api_status():
    try:
        meta = store.load()
        return json.loads(meta.model_dump_json())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not initialized")


@app.get("/api/tables")
async def api_tables():
    meta = store.load()
    return {
        name: {
            "rows": t.row_count,
            "columns": len(t.columns),
            "source": t.source_path,
            "description": t.description,
        }
        for name, t in meta.tables.items()
    }


@app.get("/api/quality")
async def api_quality():
    meta = store.load()
    return {
        name: {
            "score": qr.score,
            "passed": qr.passed,
            "failed": qr.failed,
            "total": qr.total,
        }
        for name, qr in meta.quality_results.items()
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _not_initialized_html() -> str:
    return """<!DOCTYPE html>
<html><head><title>OpenForge</title>
<style>body{font-family:system-ui;display:flex;align-items:center;justify-content:center;
height:100vh;margin:0;background:#f8fafc;}
.box{text-align:center;padding:2rem;}
h1{color:#1e3a5f;}code{background:#f1f5f9;padding:.2rem .5rem;border-radius:4px;}</style>
</head><body><div class="box">
<h1>◆ OpenForge</h1>
<p>No project found in this directory.</p>
<p>Run <code>openforge init</code> to get started.</p>
</div></body></html>"""
