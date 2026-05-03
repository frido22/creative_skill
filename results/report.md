# Creative Benchmark Report

Creative real benchmark result: FAIL

Creative is working as an originality booster, but it is not reliable enough yet. It made answers more original, but too often lost feasibility compared with the baseline.

This report uses real model outputs and automated blind judging.

Short version: this benchmark does not ask whether Creative is weird. It asks whether Creative is better than a normal answer while still being practical.

## Reader Summary

| Plain-English Question | Answer | What The Number Says |
| --- | --- | --- |
| Does Creative make answers more original? | Yes, strongly. | Creative was more original in 90% of tasks. |
| Does Creative reliably produce the better answer? | Not yet. | Valid win rate was 48%; passing needs 50%. |
| Does Creative stay practical? | Needs work. | Feasibility loss was 38%; passing needs 50% or less. |
| Does Creative become too complicated? | No. | Overcomplication was 2%; passing allows up to 50%. |

## Method

The benchmark generates baseline and creative answers for each task, randomizes answer order, and asks an automated judge to compare the pair without seeing labels.

Tasks: 40
Generation model: gpt-5.5
Judge model: gpt-5.5

## Technical Metrics

| Metric | Value | Threshold | Status |
| --- | ---: | --- | --- |
| `creative_valid_win_rate` | 47.50% | >= 50% | FAIL |
| `creative_originality_win_rate` | 90.00% | >= 70% | PASS |
| `creative_feasibility_loss_rate` | 37.50% | <= 50% | PASS |
| `creative_overcomplication_rate` | 2.50% | <= 50% | PASS |

## Pass/Fail

Overall status: FAIL

## Per Category Breakdown

| Category | Valid win rate | Originality win rate | Feasibility loss rate |
| --- | ---: | ---: | ---: |
| agent_workflow | 60.00% | 80.00% | 40.00% |
| code_architecture | 40.00% | 100.00% | 60.00% |
| debugging | 0.00% | 100.00% | 100.00% |
| design | 40.00% | 80.00% | 60.00% |
| naming | 60.00% | 100.00% | 20.00% |
| product_strategy | 80.00% | 100.00% | 20.00% |
| research_framing | 60.00% | 80.00% | 0.00% |
| writing | 40.00% | 80.00% | 0.00% |

## Top 5 Creative Wins

- `writing_001`: B is more distinctive and memorable, though the final meta note is unnecessary. A is clean and usable but relies on familiar SaaS phrasing.
- `naming_002`: Both satisfy the request, but B is more memorable and original while staying concrete and free of AI buzzwords. A is clearer and simpler, but less distinctive.
- `naming_004`: B gives a clear primary workshop name immediately, with a strong tagline and sharper, less bland alternatives. A is also solid, but its top recommendation is slightly more conventional.
- `naming_003`: A gives a sharper, more distinctive recommendation with a strong metaphor and clear positioning. B has several usable options, but the best picks are more generic or harder to own.
- `naming_001`: A is clear and brandable but relies on a familiar metaphor. B is more original, more specific to the actual anti-default mechanism, and feels like a usable coding primitive, though 'refusal' may carry some ambiguity.

## Top 5 Creative Failures

- `naming_005`: A is clearer, simpler, and directly communicates a penalty for pointless quirkiness. B is more evocative and original, but less immediately legible as a benchmark name.
- `writing_004`: B is a cleaner, ready-to-use product update with clear sections and no apology language. A is also solid, but the final meta-comment about the creative move does not belong in the customer-facing update.
- `writing_003`: A is clearer, more directly tied to automated benchmarking, and offers several usable alternatives. B is punchier and original, but slightly more metaphorical and less immediately clear.
- `code_architecture_002`: Both give clear small-boundary architectures, but B is more immediately feasible and simpler by leaning on existing form primitives instead of building a custom lifecycle hook, while still avoiding a giant framework.
- `code_architecture_004`: Both answers propose the right direction: inventory current behavior, extract only retry mechanics, keep policies explicit, test and migrate incrementally. B is slightly better because it is simpler and more directly feasible, while A introduces extra classifier/scheduler structure and sample code with some inconsistencies.

## Limitations

This benchmark uses automated judging, so it is not a replacement for human review. It is a fast first-pass test for whether Creative changes outputs in a useful direction.

## Next Steps

Add harder tasks, run with multiple model pairs, inspect failures, and compare against human ratings.
