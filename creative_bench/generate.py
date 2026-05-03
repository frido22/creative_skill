from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from openai import OpenAI

from creative_bench.config import Settings, require_api_key
from creative_bench.tasks import Task, write_jsonl


BASELINE_SYSTEM_PROMPT = "You are a helpful assistant. Answer the user request clearly and practically."
CREATIVE_SYSTEM_PREFIX = "You are a helpful assistant. Use the Creative skill below for this task."


def _supports_temperature(model: str) -> bool:
    return not model.startswith("gpt-5.5")


def _fake_answer(task: Task, mode: str) -> str:
    if mode == "baseline":
        return (
            f"A practical answer for {task.task_id}: identify the main problem, choose a clear "
            "solution, explain the tradeoff, and give the next step."
        )
    return (
        f"A less default answer for {task.task_id}: invert the usual assumption, remove one "
        "unnecessary part, borrow a pattern from another field, and ship the smallest useful "
        "version.\n\nCreative move: replaced the generic checklist with a constrained reframing."
    )


def _call_openai(
    client: OpenAI,
    settings: Settings,
    system_prompt: str,
    user_prompt: str,
) -> str:
    request = {
        "model": settings.gen_model,
        "reasoning": {"effort": settings.reasoning_effort},
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    if _supports_temperature(settings.gen_model):
        request["temperature"] = settings.temperature
    response = client.responses.create(**request)
    return response.output_text


def generate_answers(
    tasks: list[Task],
    settings: Settings,
    mode: str,
    dry_run: bool = False,
    output_path: Path | None = None,
) -> list[dict]:
    if mode not in {"baseline", "creative"}:
        raise ValueError("mode must be baseline or creative")

    if dry_run:
        rows = [
            {
                "task_id": task.task_id,
                "category": task.category,
                "mode": mode,
                "answer": _fake_answer(task, mode),
                "model": f"dry-run-{settings.gen_model}",
            }
            for task in tasks
        ]
    else:
        require_api_key()
        client = OpenAI()
        skill = settings.skill_path.read_text(encoding="utf-8")
        system_prompt = (
            BASELINE_SYSTEM_PROMPT
            if mode == "baseline"
            else f"{CREATIVE_SYSTEM_PREFIX}\n\n{skill}"
        )
        handle = None
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            handle = output_path.open("w", encoding="utf-8")
        rows = []
        try:
            with ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
                future_to_task = {
                    executor.submit(
                        _call_openai,
                        client=client,
                        system_prompt=system_prompt,
                        user_prompt=task.prompt,
                        settings=settings,
                    ): task
                    for task in tasks
                }
                for completed, future in enumerate(as_completed(future_to_task), start=1):
                    task = future_to_task[future]
                    print(
                        f"Generated {mode} answer {completed}/{len(tasks)}: {task.task_id}",
                        flush=True,
                    )
                    row = {
                        "task_id": task.task_id,
                        "category": task.category,
                        "mode": mode,
                        "answer": future.result(),
                        "model": settings.gen_model,
                    }
                    rows.append(row)
                    if handle:
                        handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")
                        handle.flush()
        finally:
            if handle:
                handle.close()

    if output_path and dry_run:
        write_jsonl(output_path, rows)
    return rows
