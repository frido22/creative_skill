# Creative Benchmark Report

Creative dry-run example result: PASS

Creative passed: it made answers less default while staying useful and feasible often enough to clear the benchmark thresholds.

This dry-run report uses deterministic fake answers and fake judgments. It verifies the benchmark pipeline, not the real effectiveness of Creative.

Short version: this benchmark does not ask whether Creative is weird. It asks whether Creative is better than a normal answer while still being practical.

## Reader Summary

| Plain-English Question | Answer | What The Number Says |
| --- | --- | --- |
| Does Creative make answers more original? | Yes, strongly. | Creative was more original in 90% of tasks. |
| Does Creative reliably produce the better answer? | Not yet. | Valid win rate was 75%; passing needs 50%. |
| Does Creative stay practical? | Needs work. | Feasibility loss was 10%; passing needs 50% or less. |
| Does Creative become too complicated? | No. | Overcomplication was 10%; passing allows up to 50%. |

## Method

The benchmark generates baseline and creative answers for each task, randomizes answer order, and asks an automated judge to compare the pair without seeing labels.

Tasks: 40
Generation model: gpt-5.5
Judge model: gpt-5.5

## Technical Metrics

| Metric | Value | Threshold | Status |
| --- | ---: | --- | --- |
| `creative_valid_win_rate` | 75.00% | >= 50% | PASS |
| `creative_originality_win_rate` | 90.00% | >= 70% | PASS |
| `creative_feasibility_loss_rate` | 10.00% | <= 50% | PASS |
| `creative_overcomplication_rate` | 10.00% | <= 50% | PASS |

## Pass/Fail

Overall status: PASS

## Per Category Breakdown

| Category | Valid win rate | Originality win rate | Feasibility loss rate |
| --- | ---: | ---: | ---: |
| agent_workflow | 60.00% | 80.00% | 20.00% |
| code_architecture | 80.00% | 80.00% | 20.00% |
| debugging | 80.00% | 100.00% | 0.00% |
| design | 60.00% | 80.00% | 20.00% |
| naming | 100.00% | 100.00% | 0.00% |
| product_strategy | 60.00% | 100.00% | 0.00% |
| research_framing | 80.00% | 100.00% | 0.00% |
| writing | 80.00% | 80.00% | 20.00% |

## Top 5 Creative Wins

- `naming_001`: Dry run judgment favors the answer that is more concrete and less generic.
- `naming_002`: Dry run judgment favors the answer that is more concrete and less generic.
- `naming_003`: Dry run judgment favors the answer that is more concrete and less generic.
- `naming_004`: Dry run judgment favors the answer that is more concrete and less generic.
- `naming_005`: Dry run judgment favors the answer that is more concrete and less generic.

## Top 5 Creative Failures

- `product_strategy_001`: Dry run judgment favors the answer that is more concrete and less generic.
- `debugging_002`: Dry run judgment favors the answer that is more concrete and less generic.
- `research_framing_003`: Dry run judgment favors the answer that is more concrete and less generic.

## Limitations

This benchmark uses automated judging, so it is not a replacement for human review. It is a fast first-pass test for whether Creative changes outputs in a useful direction.

## Next Steps

Add harder tasks, run with multiple model pairs, inspect failures, and compare against human ratings.
