from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from creative_bench.config import RESULTS_DIR, load_settings
from creative_bench.generate import generate_answers
from creative_bench.judge import judge_pairs, make_pairs
from creative_bench.metrics import compute_summary
from creative_bench.report import update_readme, write_report, write_summary
from creative_bench.tasks import load_tasks, read_jsonl


console = Console()


def _paths(dry_run: bool) -> dict[str, Path]:
    if dry_run:
        return {
            "summary": RESULTS_DIR / "example_summary.json",
            "report": RESULTS_DIR / "example_report.md",
        }
    return {
        "baseline": RESULTS_DIR / "baseline.jsonl",
        "creative": RESULTS_DIR / "creative.jsonl",
        "pairs": RESULTS_DIR / "pairs.jsonl",
        "judgments": RESULTS_DIR / "judgments.jsonl",
        "summary": RESULTS_DIR / "summary.json",
        "report": RESULTS_DIR / "report.md",
    }


def command_generate(dry_run: bool) -> None:
    settings = load_settings()
    tasks = load_tasks()
    paths = _paths(dry_run)
    baseline_path = paths.get("baseline")
    creative_path = paths.get("creative")
    if dry_run:
        baseline_path = None
        creative_path = None
    generate_answers(tasks, settings, "baseline", dry_run=dry_run, output_path=baseline_path)
    generate_answers(tasks, settings, "creative", dry_run=dry_run, output_path=creative_path)
    console.print(f"Generated answers for {len(tasks)} tasks.")


def command_judge(dry_run: bool) -> None:
    settings = load_settings()
    tasks = load_tasks()
    paths = _paths(dry_run)
    if dry_run:
        baseline = generate_answers(tasks, settings, "baseline", dry_run=True)
        creative = generate_answers(tasks, settings, "creative", dry_run=True)
        pairs = make_pairs(tasks, baseline, creative, settings.seed)
        judgments = judge_pairs(pairs, settings, dry_run=True)
    else:
        baseline = read_jsonl(RESULTS_DIR / "baseline.jsonl")
        creative = read_jsonl(RESULTS_DIR / "creative.jsonl")
        pairs = make_pairs(tasks, baseline, creative, settings.seed, output_path=paths["pairs"])
        judgments = judge_pairs(pairs, settings, dry_run=False, output_path=paths["judgments"])
    summary = compute_summary(judgments, settings.gen_model, settings.judge_model, dry_run)
    write_summary(summary, paths["summary"])
    write_report(summary, judgments, paths["report"])
    update_readme(settings.readme_path, summary)
    console.print(f"Judged {len(judgments)} pairs.")


def command_report() -> None:
    settings = load_settings()
    summary_path = RESULTS_DIR / "summary.json"
    judgments_path = RESULTS_DIR / "judgments.jsonl"
    if not summary_path.exists():
        summary_path = RESULTS_DIR / "example_summary.json"
        judgments = judge_pairs(
            make_pairs(
                load_tasks(),
                generate_answers(load_tasks(), settings, "baseline", dry_run=True),
                generate_answers(load_tasks(), settings, "creative", dry_run=True),
                settings.seed,
            ),
            settings,
            dry_run=True,
        )
    else:
        judgments = read_jsonl(judgments_path)
    import json

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    report_path = RESULTS_DIR / ("report.md" if summary_path.name == "summary.json" else "example_report.md")
    write_report(summary, judgments, report_path)
    update_readme(settings.readme_path, summary)
    console.print(f"Wrote {report_path}.")


def command_run(dry_run: bool) -> None:
    settings = load_settings()
    tasks = load_tasks()
    paths = _paths(dry_run)
    baseline = generate_answers(
        tasks,
        settings,
        "baseline",
        dry_run=dry_run,
        output_path=None if dry_run else paths["baseline"],
    )
    creative = generate_answers(
        tasks,
        settings,
        "creative",
        dry_run=dry_run,
        output_path=None if dry_run else paths["creative"],
    )
    pairs = make_pairs(
        tasks,
        baseline,
        creative,
        settings.seed,
        output_path=None if dry_run else paths["pairs"],
    )
    judgments = judge_pairs(
        pairs,
        settings,
        dry_run=dry_run,
        output_path=None if dry_run else paths["judgments"],
    )
    summary = compute_summary(judgments, settings.gen_model, settings.judge_model, dry_run)
    write_summary(summary, paths["summary"])
    write_report(summary, judgments, paths["report"])
    update_readme(settings.readme_path, summary)
    console.print(f"Benchmark complete: {'PASS' if summary['pass'] else 'FAIL'}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="creative_bench")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ["run", "generate", "judge"]:
        subparser = subparsers.add_parser(name)
        subparser.add_argument("--dry-run", action="store_true")
    subparsers.add_parser("report")
    args = parser.parse_args()

    if args.command == "run":
        command_run(args.dry_run)
    elif args.command == "generate":
        command_generate(args.dry_run)
    elif args.command == "judge":
        command_judge(args.dry_run)
    elif args.command == "report":
        command_report()


if __name__ == "__main__":
    main()
