"""
Metadata store — reads and writes .openforge/metadata.json.

This is the single source of truth for project state.
All agents read from and write to this store.
Migration path to PostgreSQL: replace the JSON file operations
with SQLModel queries — the Pydantic models stay identical.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .models import ProjectMetadata, QualityResult, TableSchema

OPENFORGE_DIR = ".openforge"
METADATA_FILE = "metadata.json"
WAREHOUSE_FILE = "warehouse.db"


def _dir(root: Path | None = None) -> Path:
    return (root or Path.cwd()) / OPENFORGE_DIR


def get_warehouse_path(root: Path | None = None) -> Path:
    return _dir(root) / WAREHOUSE_FILE


def is_initialized(root: Path | None = None) -> bool:
    return (_dir(root) / METADATA_FILE).exists()


def load(root: Path | None = None) -> ProjectMetadata:
    meta_path = _dir(root) / METADATA_FILE
    if not meta_path.exists():
        raise FileNotFoundError(
            "No OpenForge project found. Run 'openforge init' first."
        )
    return ProjectMetadata.model_validate(json.loads(meta_path.read_text()))


def save(meta: ProjectMetadata, root: Path | None = None) -> None:
    meta_path = _dir(root) / METADATA_FILE
    meta.updated_at = datetime.utcnow()
    meta_path.write_text(meta.model_dump_json(indent=2))


def upsert_table(table: TableSchema, root: Path | None = None) -> None:
    meta = load(root)
    table.updated_at = datetime.utcnow()
    meta.tables[table.name] = table
    save(meta, root)


def upsert_quality(result: QualityResult, root: Path | None = None) -> None:
    meta = load(root)
    meta.quality_results[result.table] = result
    save(meta, root)
