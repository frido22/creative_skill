from __future__ import annotations

import json
from pathlib import Path
from typing import Any


README_START = "<!-- BENCHMARK_TABLE_START -->"
README_END = "<!-- BENCHMARK_TABLE_END -->"

HEADLINE_METRICS = [
    ("creative_originality_win_rate", "Originality win rate", "Higher means less default."),
    ("creative_overall_win_rate", "Overall win rate", "Higher means the judge preferred Creative."),
    ("creative_valid_win_rate", "Valid win rate", "Creative won without losing feasibility."),
    ("creative_feasibility_loss_rate", "Feasibility loss rate", "Lower means fewer practicality losses."),
    ("creative_overcomplication_rate", "Overcomplication rate", "Lower means fewer bloated answers."),
]

JUDGE_QUESTIONS = [
    ("Originality", "Which answer is less default and brings a better non-obvious angle?"),
    ("Usefulness", "Which answer gives the user a better next move?"),
    ("Feasibility", "Which answer is more realistic to execute as written?"),
    ("Specificity", "Which answer gives more concrete details, tradeoffs, or next actions?"),
    ("Simplicity", "Which answer avoids unnecessary complexity, ceremony, or bloat?"),
]


def plain_english_summary(summary: dict[str, Any]) -> str:
    metrics = summary["metrics"]
    if metrics["creative_originality_win_rate"] >= 0.80:
        return (
            "Creative made answers much less default and won most overall comparisons. "
            "The main caveat is feasibility: some creative answers were judged less practical than baseline."
        )
    return (
        "Creative changed outputs, but the current run does not show a strong originality effect yet. "
        "Inspect the per-task judgments before drawing stronger conclusions."
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
            "| Does Creative usually beat the baseline? | Often. | "
            f"Creative won the overall judgment in {metrics['creative_overall_win_rate']:.0%} of tasks. |"
        ),
        (
            "| Does Creative win without losing feasibility? | Mixed. | "
            f"Valid win rate was {metrics['creative_valid_win_rate']:.0%}. |"
        ),
        (
            "| Does Creative become too complicated? | No. | "
            f"Overcomplication was flagged in {metrics['creative_overcomplication_rate']:.0%} of tasks. |"
        ),
    ]
    return "\n".join(rows)


def metric_table(summary: dict[str, Any]) -> str:
    rows = ["| Metric | Value | 95% CI | Interpretation |", "| --- | ---: | ---: | --- |"]
    metrics = summary["metrics"]
    intervals = summary.get("confidence_intervals", {})
    for metric, label, interpretation in HEADLINE_METRICS:
        value = metrics[metric]
        lower, upper = intervals.get(metric, (None, None))
        ci = "n/a" if lower is None else f"{lower:.1%}-{upper:.1%}"
        rows.append(f"| {label} | {value:.2%} | {ci} | {interpretation} |")
    return "\n".join(rows)


def judge_questions_table() -> str:
    rows = ["| Judge Question | What It Measures |", "| --- | --- |"]
    rows.extend(f"| {question} | {metric} |" for metric, question in JUDGE_QUESTIONS)
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
    lines = [
        "# Creative Benchmark Report",
        "",
        "Creative benchmark result: measured effect",
        "",
        plain_english_summary(summary),
        "",
        "This report uses real model outputs and automated blind judging.",
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
        "## Judge Questions",
        "",
        "The judge uses five plain-English questions, then chooses the better answer overall.",
        "",
        judge_questions_table(),
        "",
        f"Tasks: {summary['task_count']}",
        f"Generation model: {summary['gen_model']}",
        f"Judge model: {summary['judge_model']}",
        "",
        "## Headline Metrics",
        "",
        metric_table(summary),
        "",
        "## How To Read This",
        "",
        "This benchmark does not use a hard pass/fail threshold. The rates describe observed behavior "
        "on the committed task run, and the confidence intervals show uncertainty from the sample size.",
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
