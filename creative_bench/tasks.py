from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from creative_bench.config import DATA_DIR


class Task(BaseModel):
    task_id: str = Field(min_length=1)
    category: str = Field(min_length=1)
    prompt: str = Field(min_length=1)


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSON on line {line_number} in {path}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")


def load_tasks(path: Path | None = None) -> list[Task]:
    task_path = path or DATA_DIR / "tasks.jsonl"
    tasks = [Task.model_validate(row) for row in read_jsonl(task_path)]
    task_ids = [task.task_id for task in tasks]
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("Task IDs must be unique.")
    return tasks
