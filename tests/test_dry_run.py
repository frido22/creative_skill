import json

from creative_bench.cli import command_run
from creative_bench.config import RESULTS_DIR


def test_dry_run_command_generates_example_outputs() -> None:
    command_run(dry_run=True)
    summary_path = RESULTS_DIR / "example_summary.json"
    report_path = RESULTS_DIR / "example_report.md"
    assert summary_path.exists()
    assert report_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["dry_run"] is True
    assert summary["task_count"] == 40
    assert "creative_valid_win_rate" in summary["metrics"]


def test_report_generation_contains_required_sections() -> None:
    command_run(dry_run=True)
    report = (RESULTS_DIR / "example_report.md").read_text(encoding="utf-8")
    assert "# Creative Benchmark Report" in report
    assert "## Per Category Breakdown" in report
    assert "## Top 5 Creative Wins" in report
