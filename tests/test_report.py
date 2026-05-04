from creative_bench.cli import command_report
from creative_bench.config import RESULTS_DIR


def test_report_command_uses_existing_results() -> None:
    command_report()
    report = (RESULTS_DIR / "report.md").read_text(encoding="utf-8")
    assert "# Creative Benchmark Report" in report
    assert "95% CI" in report
    assert "pass/fail threshold" in report
    assert "## Judge Questions" in report
    assert "## Per Category Breakdown" in report
    assert "## Top 5 Creative Wins" in report
