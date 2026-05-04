from __future__ import annotations

import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field

from creative_bench.config import Settings, require_api_key
from creative_bench.tasks import Task, write_jsonl


JUDGE_SYSTEM_PROMPT = """You are the blind judge for a benchmark comparing two answers to the same user request.
Do not reward length.
Do not reward weirdness alone.
Do not infer which answer used a special prompt or skill.
Prefer the answer that is more useful, original, feasible, specific, and simple.

Judge by answering these five plain-English questions:
1. Originality: Which answer is less default and brings a better non-obvious angle?
2. Usefulness: Which answer helps the user make more progress on the actual request?
3. Feasibility: Which answer could more realistically work without hidden assumptions?
4. Specificity: Which answer gives more concrete details, tradeoffs, or next actions?
5. Simplicity: Which answer avoids unnecessary complexity, ceremony, or bloat?

Score each answer from 1 to 5 for originality, usefulness, feasibility, specificity, and simplicity.
Then choose:
overall_winner: A, B, or tie
Choose tie only when neither answer is meaningfully better overall.
Also return:
nonsense_a: true or false
nonsense_b: true or false
overcomplicated_a: true or false
overcomplicated_b: true or false
short_reason: string
Return JSON only.
Use exactly these top-level keys:
scores_a, scores_b, overall_winner, nonsense_a, nonsense_b, overcomplicated_a, overcomplicated_b, short_reason.
scores_a and scores_b must each contain exactly:
originality, usefulness, feasibility, specificity, simplicity."""


def _supports_temperature(model: str) -> bool:
    return not model.startswith("gpt-5.5")


class AnswerScore(BaseModel):
    originality: int = Field(ge=1, le=5)
    usefulness: int = Field(ge=1, le=5)
    feasibility: int = Field(ge=1, le=5)
    specificity: int = Field(ge=1, le=5)
    simplicity: int = Field(ge=1, le=5)


class JudgmentPayload(BaseModel):
    scores_a: AnswerScore
    scores_b: AnswerScore
    overall_winner: str
    nonsense_a: bool
    nonsense_b: bool
    overcomplicated_a: bool
    overcomplicated_b: bool
    short_reason: str


def make_pairs(
    tasks: list[Task],
    baseline_rows: list[dict],
    creative_rows: list[dict],
    seed: int,
    output_path: Path | None = None,
) -> list[dict]:
    baseline_by_id = {row["task_id"]: row for row in baseline_rows}
    creative_by_id = {row["task_id"]: row for row in creative_rows}
    rng = random.Random(seed)
    pairs: list[dict] = []
    for task in tasks:
        if rng.choice([True, False]):
            answer_a, answer_b = baseline_by_id[task.task_id], creative_by_id[task.task_id]
        else:
            answer_a, answer_b = creative_by_id[task.task_id], baseline_by_id[task.task_id]
        pairs.append(
            {
                "task_id": task.task_id,
                "category": task.category,
                "prompt": task.prompt,
                "answer_a": answer_a["answer"],
                "answer_b": answer_b["answer"],
                "hidden_label_a": answer_a["mode"],
                "hidden_label_b": answer_b["mode"],
            }
        )
    if output_path:
        write_jsonl(output_path, pairs)
    return pairs


def _judge_prompt(pair: dict) -> str:
    return (
        f"User request:\n{pair['prompt']}\n\n"
        f"Answer A:\n{pair['answer_a']}\n\n"
        f"Answer B:\n{pair['answer_b']}"
    )


def _parse_payload(text: str) -> JudgmentPayload:
    payload = json.loads(text)
    if "scores_a" not in payload and "answer_a" in payload:
        payload["scores_a"] = payload.pop("answer_a")
    if "scores_b" not in payload and "answer_b" in payload:
        payload["scores_b"] = payload.pop("answer_b")
    if "scores_a" not in payload and "scores" in payload:
        scores = payload.pop("scores")
        payload["scores_a"] = scores.get("A") or scores.get("a")
        payload["scores_b"] = scores.get("B") or scores.get("b")
    if "scores_a" not in payload and "originality_a" in payload:
        payload["scores_a"] = {
            "originality": payload.pop("originality_a"),
            "usefulness": payload.pop("usefulness_a"),
            "feasibility": payload.pop("feasibility_a"),
            "specificity": payload.pop("specificity_a"),
            "simplicity": payload.pop("simplicity_a"),
        }
        payload["scores_b"] = {
            "originality": payload.pop("originality_b"),
            "usefulness": payload.pop("usefulness_b"),
            "feasibility": payload.pop("feasibility_b"),
            "specificity": payload.pop("specificity_b"),
            "simplicity": payload.pop("simplicity_b"),
        }
    return JudgmentPayload.model_validate(payload)


def _call_judge(client: OpenAI, settings: Settings, pair: dict) -> JudgmentPayload:
    last_error: Exception | None = None
    for _ in range(2):
        request = {
            "model": settings.judge_model,
            "reasoning": {"effort": settings.reasoning_effort},
            "input": [
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": _judge_prompt(pair)},
            ],
        }
        if _supports_temperature(settings.judge_model):
            request["temperature"] = 0
        response = client.responses.create(**request)
        try:
            return _parse_payload(response.output_text)
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
    raise RuntimeError("Judge returned malformed JSON twice.") from last_error


def judge_pairs(
    pairs: list[dict],
    settings: Settings,
    output_path: Path | None = None,
) -> list[dict[str, Any]]:
    rows = []
    handle = None
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        handle = output_path.open("w", encoding="utf-8")

    require_api_key()
    client = OpenAI()
    try:
        with ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
            future_to_pair = {
                executor.submit(_call_judge, client, settings, pair): pair for pair in pairs
            }
            for completed, future in enumerate(as_completed(future_to_pair), start=1):
                pair = future_to_pair[future]
                print(
                    f"Judged pair {completed}/{len(pairs)}: {pair['task_id']}",
                    flush=True,
                )
                payload = future.result()
                row = {
                    "task_id": pair["task_id"],
                    "category": pair["category"],
                    "hidden_label_a": pair["hidden_label_a"],
                    "hidden_label_b": pair["hidden_label_b"],
                    **payload.model_dump(),
                }
                rows.append(row)
                if handle:
                    handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")
                    handle.flush()
    finally:
        if handle:
            handle.close()
    return rows
