from __future__ import annotations

from collections import defaultdict
from typing import Any


THRESHOLDS = {
    "creative_valid_win_rate": (">=", 0.60),
    "creative_originality_win_rate": (">=", 0.70),
    "creative_feasibility_loss_rate": ("<=", 0.15),
    "creative_overcomplication_rate": ("<=", 0.20),
}


SCORE_FIELDS = ["originality", "usefulness", "feasibility", "specificity", "simplicity"]


def _rate(count: int, total: int) -> float:
    return 0.0 if total == 0 else count / total


def _creative_side(row: dict[str, Any]) -> str:
    if row["hidden_label_a"] == "creative":
        return "a"
    if row["hidden_label_b"] == "creative":
        return "b"
    raise ValueError("Judgment row does not identify a creative answer.")


def _baseline_side(row: dict[str, Any]) -> str:
    return "b" if _creative_side(row) == "a" else "a"


def _score(row: dict[str, Any], side: str, field: str) -> int:
    return int(row[f"scores_{side}"][field])


def _compute_rows(rows: list[dict[str, Any]]) -> dict[str, float]:
    total = len(rows)
    counts = defaultdict(int)
    deltas = defaultdict(float)

    for row in rows:
        creative_side = _creative_side(row)
        baseline_side = _baseline_side(row)
        creative_winner = creative_side.upper()
        creative_won = row["overall_winner"] == creative_winner
        feasibility_loss = _score(row, creative_side, "feasibility") < _score(
            row, baseline_side, "feasibility"
        )
        nonsense = bool(row[f"nonsense_{creative_side}"])
        overcomplicated = bool(row[f"overcomplicated_{creative_side}"])

        counts["creative_overall_win"] += int(creative_won)
        counts["creative_valid_win"] += int(creative_won and not nonsense and not feasibility_loss)
        counts["creative_originality_win"] += int(
            _score(row, creative_side, "originality") > _score(row, baseline_side, "originality")
        )
        counts["creative_usefulness_win"] += int(
            _score(row, creative_side, "usefulness") > _score(row, baseline_side, "usefulness")
        )
        counts["creative_feasibility_loss"] += int(feasibility_loss)
        counts["creative_overcomplication"] += int(overcomplicated)
        counts["tie"] += int(row["overall_winner"] == "tie")

        for field in SCORE_FIELDS:
            deltas[field] += _score(row, creative_side, field) - _score(row, baseline_side, field)

    return {
        "creative_valid_win_rate": _rate(counts["creative_valid_win"], total),
        "creative_overall_win_rate": _rate(counts["creative_overall_win"], total),
        "creative_originality_win_rate": _rate(counts["creative_originality_win"], total),
        "creative_usefulness_win_rate": _rate(counts["creative_usefulness_win"], total),
        "creative_feasibility_loss_rate": _rate(counts["creative_feasibility_loss"], total),
        "creative_overcomplication_rate": _rate(counts["creative_overcomplication"], total),
        "tie_rate": _rate(counts["tie"], total),
        "average_originality_delta": _rate(deltas["originality"], total),
        "average_usefulness_delta": _rate(deltas["usefulness"], total),
        "average_feasibility_delta": _rate(deltas["feasibility"], total),
        "average_specificity_delta": _rate(deltas["specificity"], total),
        "average_simplicity_delta": _rate(deltas["simplicity"], total),
    }


def threshold_status(metric: str, value: float) -> str:
    if metric not in THRESHOLDS:
        return ""
    operator, threshold = THRESHOLDS[metric]
    passed = value >= threshold if operator == ">=" else value <= threshold
    return "PASS" if passed else "FAIL"


def overall_pass(metrics: dict[str, float]) -> bool:
    return all(threshold_status(metric, metrics[metric]) == "PASS" for metric in THRESHOLDS)


def compute_summary(
    judgments: list[dict[str, Any]],
    gen_model: str,
    judge_model: str,
    dry_run: bool,
) -> dict[str, Any]:
    categories = sorted({row["category"] for row in judgments})
    by_category = {
        category: _compute_rows([row for row in judgments if row["category"] == category])
        for category in categories
    }
    metrics = _compute_rows(judgments)
    return {
        "dry_run": dry_run,
        "task_count": len(judgments),
        "gen_model": gen_model,
        "judge_model": judge_model,
        "metrics": metrics,
        "thresholds": THRESHOLDS,
        "pass": overall_pass(metrics),
        "by_category": by_category,
    }
