from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from creative_bench.metrics import THRESHOLDS, threshold_status


README_START = "<!-- BENCHMARK_TABLE_START -->"
README_END = "<!-- BENCHMARK_TABLE_END -->"


def plain_english_summary(summary: dict[str, Any]) -> str:
    metrics = summary["metrics"]
    if summary["pass"]:
        return (
            "Creative passed: it made answers less default while staying useful and feasible "
            "often enough to clear the benchmark thresholds."
        )
    if (
        metrics["creative_originality_win_rate"] >= 0.70
        and metrics["creative_valid_win_rate"] < 0.60
    ):
        return (
            "Creative is working as an originality booster, but it is not reliable enough yet. "
            "It made answers more original, but too often lost feasibility compared with the baseline."
        )
    return (
        "Creative did not clear the benchmark thresholds. The current version needs more tuning "
        "before the benchmark can say it improves normal answers."
    )


def reader_table(summary: dict[str, Any]) -> str:
    metrics = summary["metrics"]
    rows = [
        "| Plain-English Question | Answer | What The Number Says |",
        "| --- | --- | --- |",
        (
            "| Does Creative make answers more original? | Yes, strongly. | "
            f"Creative was more original in {metrics['creative_originality_win_rate']:.0%} of tasks. |"
        ),
        (
            "| Does Creative reliably produce the better answer? | Not yet. | "
            f"Valid win rate was {metrics['creative_valid_win_rate']:.0%}; passing needs 60%. |"
        ),
        (
            "| Does Creative stay practical? | Needs work. | "
            f"Feasibility loss was {metrics['creative_feasibility_loss_rate']:.0%}; passing needs 15% or less. |"
        ),
        (
            "| Does Creative become too complicated? | No. | "
            f"Overcomplication was {metrics['creative_overcomplication_rate']:.0%}; passing allows up to 20%. |"
        ),
    ]
    return "\n".join(rows)


def metric_table(summary: dict[str, Any]) -> str:
    rows = ["| Metric | Value | Threshold | Status |", "| --- | ---: | --- | --- |"]
    metrics = summary["metrics"]
    for metric, (operator, threshold) in THRESHOLDS.items():
        value = metrics[metric]
        rows.append(
            f"| `{metric}` | {value:.2%} | {operator} {threshold:.0%} | "
            f"{threshold_status(metric, value)} |"
        )
    return "\n".join(rows)


def _category_table(summary: dict[str, Any]) -> str:
    rows = [
        "| Category | Valid win rate | Originality win rate | Feasibility loss rate |",
        "| --- | ---: | ---: | ---: |",
    ]
    for category, metrics in summary["by_category"].items():
        rows.append(
            f"| {category} | {metrics['creative_valid_win_rate']:.2%} | "
            f"{metrics['creative_originality_win_rate']:.2%} | "
            f"{metrics['creative_feasibility_loss_rate']:.2%} |"
        )
    return "\n".join(rows)


def _creative_side(row: dict[str, Any]) -> str:
    return "a" if row["hidden_label_a"] == "creative" else "b"


def _short_lists(judgments: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    wins: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for row in judgments:
        side = _creative_side(row)
        winner = side.upper()
        if row["overall_winner"] == winner:
            wins.append(row)
        elif row["overall_winner"] != "tie":
            failures.append(row)
    return wins[:5], failures[:5]


def write_report(summary: dict[str, Any], judgments: list[dict[str, Any]], path: Path) -> str:
    wins, failures = _short_lists(judgments)
    status = "PASS" if summary["pass"] else "FAIL"
    run_type = "dry-run example" if summary["dry_run"] else "real benchmark"
    caveat = (
        "This dry-run report uses deterministic fake answers and fake judgments. It verifies "
        "the benchmark pipeline, not the real effectiveness of Creative."
        if summary["dry_run"]
        else "This report uses real model outputs and automated blind judging."
    )
    lines = [
        "# Creative Benchmark Report",
        "",
        f"Creative {run_type} result: {status}",
        "",
        plain_english_summary(summary),
        "",
        caveat,
        "",
        "Short version: this benchmark does not ask whether Creative is weird. It asks whether "
        "Creative is better than a normal answer while still being practical.",
        "",
        "## Reader Summary",
        "",
        reader_table(summary),
        "",
        "## Method",
        "",
        "The benchmark generates baseline and creative answers for each task, randomizes answer "
        "order, and asks an automated judge to compare the pair without seeing labels.",
        "",
        f"Tasks: {summary['task_count']}",
        f"Generation model: {summary['gen_model']}",
        f"Judge model: {summary['judge_model']}",
        "",
        "## Technical Metrics",
        "",
        metric_table(summary),
        "",
        "## Pass/Fail",
        "",
        f"Overall status: {status}",
        "",
        "## Per Category Breakdown",
        "",
        _category_table(summary),
        "",
        "## Top 5 Creative Wins",
        "",
    ]
    lines.extend(
        f"- `{row['task_id']}`: {row['short_reason']}" for row in wins
    )
    if not wins:
        lines.append("- None.")
    lines.extend(["", "## Top 5 Creative Failures", ""])
    lines.extend(
        f"- `{row['task_id']}`: {row['short_reason']}" for row in failures
    )
    if not failures:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "This benchmark uses automated judging, so it is not a replacement for human review. "
            "It is a fast first-pass test for whether Creative changes outputs in a useful direction.",
            "",
            "## Next Steps",
            "",
            "Add harder tasks, run with multiple model pairs, inspect failures, and compare against human ratings.",
            "",
        ]
    )
    text = "\n".join(lines)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text


def write_summary(summary: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_readme(readme_path: Path, summary: dict[str, Any]) -> None:
    readme = readme_path.read_text(encoding="utf-8")
    replacement = f"{README_START}\n{metric_table(summary)}\n{README_END}"
    if README_START not in readme or README_END not in readme:
        raise ValueError("README benchmark markers are missing.")
    start = readme.index(README_START)
    end = readme.index(README_END) + len(README_END)
    readme_path.write_text(readme[:start] + replacement + readme[end:], encoding="utf-8")
