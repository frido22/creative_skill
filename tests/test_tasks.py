from pathlib import Path

import pytest
from pydantic import ValidationError

from creative_bench.tasks import Task, load_tasks


def test_load_default_tasks() -> None:
    tasks = load_tasks()
    assert len(tasks) == 40
    assert len({task.task_id for task in tasks}) == 40


def test_task_schema_validation() -> None:
    task = Task.model_validate(
        {"task_id": "naming_001", "category": "naming", "prompt": "Name this."}
    )
    assert task.category == "naming"

    with pytest.raises(ValidationError):
        Task.model_validate({"task_id": "", "category": "naming", "prompt": "Name this."})


def test_duplicate_task_ids_fail(tmp_path: Path) -> None:
    path = tmp_path / "tasks.jsonl"
    path.write_text(
        '{"task_id":"x","category":"naming","prompt":"One."}\n'
        '{"task_id":"x","category":"writing","prompt":"Two."}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_tasks(path)
