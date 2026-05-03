from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from creative_bench.config import Settings, require_api_key
from creative_bench.tasks import Task, write_jsonl


BASELINE_SYSTEM_PROMPT = "You are a helpful assistant. Answer the user request clearly and practically."
CREATIVE_SYSTEM_PREFIX = "You are a helpful assistant. Use the Creative skill below for this task."


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


def _call_openai(client: OpenAI, model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    response = client.responses.create(
        model=model,
        temperature=temperature,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
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
        rows = []
        for task in tasks:
            rows.append(
                {
                    "task_id": task.task_id,
                    "category": task.category,
                    "mode": mode,
                    "answer": _call_openai(
                        client=client,
                        model=settings.gen_model,
                        system_prompt=system_prompt,
                        user_prompt=task.prompt,
                        temperature=settings.temperature,
                    ),
                    "model": settings.gen_model,
                }
            )

    if output_path:
        write_jsonl(output_path, rows)
    return rows
