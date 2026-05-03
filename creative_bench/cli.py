from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from creative_bench.config import RESULTS_DIR, load_settings
from creative_bench.generate import generate_answers
from creative_bench.judge import judge_pairs, make_pairs
from creative_bench.metrics import compute_summary
from creative_bench.report import update_readme, write_report, write_summary
from creative_bench.tasks import load_tasks, read_jsonl


console = Console()


def _paths() -> dict[str, Path]:
    return {
        "baseline": RESULTS_DIR / "baseline.jsonl",
        "creative": RESULTS_DIR / "creative.jsonl",
        "pairs": RESULTS_DIR / "pairs.jsonl",
        "judgments": RESULTS_DIR / "judgments.jsonl",
        "summary": RESULTS_DIR / "summary.json",
        "report": RESULTS_DIR / "report.md",
    }


def command_generate() -> None:
    settings = load_settings()
    tasks = load_tasks()
    paths = _paths()
    generate_answers(tasks, settings, "baseline", output_path=paths["baseline"])
    generate_answers(tasks, settings, "creative", output_path=paths["creative"])
    console.print(f"Generated answers for {len(tasks)} tasks.")


def command_judge() -> None:
    settings = load_settings()
    tasks = load_tasks()
    paths = _paths()
    baseline = read_jsonl(paths["baseline"])
    creative = read_jsonl(paths["creative"])
    pairs = make_pairs(tasks, baseline, creative, settings.seed, output_path=paths["pairs"])
    judgments = judge_pairs(pairs, settings, output_path=paths["judgments"])
    summary = compute_summary(judgments, settings.gen_model, settings.judge_model)
    write_summary(summary, paths["summary"])
    write_report(summary, judgments, paths["report"])
    update_readme(settings.readme_path, summary)
    console.print(f"Judged {len(judgments)} pairs.")


def command_report() -> None:
    settings = load_settings()
    paths = _paths()
    summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
    judgments = read_jsonl(paths["judgments"])
    write_report(summary, judgments, paths["report"])
    update_readme(settings.readme_path, summary)
    console.print(f"Wrote {paths['report']}.")


def command_run() -> None:
    settings = load_settings()
    tasks = load_tasks()
    paths = _paths()
    baseline = generate_answers(tasks, settings, "baseline", output_path=paths["baseline"])
    creative = generate_answers(tasks, settings, "creative", output_path=paths["creative"])
    pairs = make_pairs(tasks, baseline, creative, settings.seed, output_path=paths["pairs"])
    judgments = judge_pairs(pairs, settings, output_path=paths["judgments"])
    summary = compute_summary(judgments, settings.gen_model, settings.judge_model)
    write_summary(summary, paths["summary"])
    write_report(summary, judgments, paths["report"])
    update_readme(settings.readme_path, summary)
    console.print(f"Benchmark complete: {'PASS' if summary['pass'] else 'FAIL'}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="creative_bench")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ["run", "generate", "judge"]:
        subparsers.add_parser(name)
    subparsers.add_parser("report")
    args = parser.parse_args()

    if args.command == "run":
        command_run()
    elif args.command == "generate":
        command_generate()
    elif args.command == "judge":
        command_judge()
    elif args.command == "report":
        command_report()


if __name__ == "__main__":
    main()
