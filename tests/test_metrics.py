from creative_bench.metrics import compute_summary


def _row(task_id: str, winner: str = "A", creative_side: str = "a") -> dict:
    return {
        "task_id": task_id,
        "category": "naming",
        "hidden_label_a": "creative" if creative_side == "a" else "baseline",
        "hidden_label_b": "baseline" if creative_side == "a" else "creative",
        "scores_a": {
            "originality": 5 if creative_side == "a" else 3,
            "usefulness": 4 if creative_side == "a" else 3,
            "feasibility": 4,
            "specificity": 4 if creative_side == "a" else 3,
            "simplicity": 4,
        },
        "scores_b": {
            "originality": 3 if creative_side == "a" else 5,
            "usefulness": 3 if creative_side == "a" else 4,
            "feasibility": 4,
            "specificity": 3 if creative_side == "a" else 4,
            "simplicity": 4,
        },
        "overall_winner": winner,
        "nonsense_a": False,
        "nonsense_b": False,
        "overcomplicated_a": False,
        "overcomplicated_b": False,
        "short_reason": "test",
    }


def test_metric_calculation() -> None:
    summary = compute_summary([_row("one"), _row("two", winner="tie")], "gen", "judge")
    metrics = summary["metrics"]
    assert metrics["creative_valid_win_rate"] == 0.5
    assert metrics["creative_originality_win_rate"] == 1.0
    assert metrics["creative_feasibility_loss_rate"] == 0.0
    assert metrics["tie_rate"] == 0.5
    assert "pass" not in summary
    assert "thresholds" not in summary
    assert summary["confidence_level"] == 0.95
    assert summary["confidence_intervals"]["creative_originality_win_rate"][0] > 0.3


def test_confidence_intervals_are_reported_for_rate_metrics() -> None:
    summary = compute_summary([_row("one"), _row("two", winner="tie")], "gen", "judge")
    lower, upper = summary["confidence_intervals"]["creative_valid_win_rate"]
    assert 0 <= lower <= upper <= 1
