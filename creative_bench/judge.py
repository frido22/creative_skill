from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field

from creative_bench.config import Settings, require_api_key
from creative_bench.tasks import Task, write_jsonl


JUDGE_SYSTEM_PROMPT = """You are judging two answers to the same user request.
Do not reward length.
Do not reward weirdness alone.
Prefer the answer that is more useful, original, feasible, specific, and simple.
Score each answer from 1 to 5 on:
1. originality
2. usefulness
3. feasibility
4. specificity
5. simplicity
Then choose:
overall_winner: A, B, or tie
Also return:
nonsense_a: true or false
nonsense_b: true or false
overcomplicated_a: true or false
overcomplicated_b: true or false
short_reason: string
Return JSON only."""


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
    return JudgmentPayload.model_validate(json.loads(text))


def _call_judge(client: OpenAI, settings: Settings, pair: dict) -> JudgmentPayload:
    last_error: Exception | None = None
    for _ in range(2):
        response = client.responses.create(
            model=settings.judge_model,
            temperature=0,
            input=[
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": _judge_prompt(pair)},
            ],
        )
        try:
            return _parse_payload(response.output_text)
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
    raise RuntimeError("Judge returned malformed JSON twice.") from last_error


def _fake_judgment(pair: dict, index: int) -> JudgmentPayload:
    creative_is_a = pair["hidden_label_a"] == "creative"
    creative_score = {
        "originality": 5 if index % 10 != 0 else 3,
        "usefulness": 4 if index % 8 != 0 else 3,
        "feasibility": 4 if index % 9 != 0 else 3,
        "specificity": 4,
        "simplicity": 4 if index % 7 != 0 else 3,
    }
    baseline_score = {
        "originality": 3,
        "usefulness": 3,
        "feasibility": 4,
        "specificity": 3,
        "simplicity": 4,
    }
    winner = "tie" if index % 13 == 0 else ("A" if creative_is_a else "B")
    if index % 11 == 0:
        winner = "B" if creative_is_a else "A"
    scores_a = creative_score if creative_is_a else baseline_score
    scores_b = baseline_score if creative_is_a else creative_score
    return JudgmentPayload(
        scores_a=AnswerScore(**scores_a),
        scores_b=AnswerScore(**scores_b),
        overall_winner=winner,
        nonsense_a=False,
        nonsense_b=False,
        overcomplicated_a=creative_is_a and index % 10 == 0,
        overcomplicated_b=(not creative_is_a) and index % 10 == 0,
        short_reason="Dry run judgment favors the answer that is more concrete and less generic.",
    )


def judge_pairs(
    pairs: list[dict],
    settings: Settings,
    dry_run: bool = False,
    output_path: Path | None = None,
) -> list[dict[str, Any]]:
    if dry_run:
        payloads = [_fake_judgment(pair, index) for index, pair in enumerate(pairs, start=1)]
    else:
        require_api_key()
        client = OpenAI()
        payloads = [_call_judge(client, settings, pair) for pair in pairs]

    rows = []
    for pair, payload in zip(pairs, payloads):
        rows.append(
            {
                "task_id": pair["task_id"],
                "category": pair["category"],
                "hidden_label_a": pair["hidden_label_a"],
                "hidden_label_b": pair["hidden_label_b"],
                **payload.model_dump(),
            }
        )
    if output_path:
        write_jsonl(output_path, rows)
    return rows
