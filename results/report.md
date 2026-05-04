# Creative Benchmark Report

Creative benchmark result: measured effect

Creative made answers much less default and won most overall comparisons. The main caveat is feasibility: some creative answers were judged less practical than baseline.

This report uses real model outputs and automated blind judging.

Short version: this benchmark does not ask whether Creative is weird. It asks whether Creative is better than a normal answer while still being practical.

## Reader Summary

| Plain-English Question | Answer | What The Number Says |
| --- | --- | --- |
| Does Creative make answers more original? | Yes, strongly. | Creative was more original in 95% of tasks. |
| Does Creative usually beat the baseline? | Often. | Creative won the overall judgment in 70% of tasks. |
| Does Creative win without losing feasibility? | Mixed. | Valid win rate was 50%. |
| Does Creative become too complicated? | No. | Overcomplication was flagged in 0% of tasks. |

## Method

The benchmark generates baseline and creative answers for each task, randomizes answer order, and asks an automated judge to compare the pair without seeing labels.

## Judge Questions

The judge uses five plain-English questions, then chooses the better answer overall.

| Judge Question | What It Measures |
| --- | --- |
| Which answer is less default and brings a better non-obvious angle? | Originality |
| Which answer helps the user make more progress on the actual request? | Usefulness |
| Which answer could more realistically work without hidden assumptions? | Feasibility |
| Which answer gives more concrete details, tradeoffs, or next actions? | Specificity |
| Which answer avoids unnecessary complexity, ceremony, or bloat? | Simplicity |

Tasks: 40
Generation model: gpt-5.5
Judge model: gpt-5.5

## Headline Metrics

| Metric | Value | 95% CI | Interpretation |
| --- | ---: | ---: | --- |
| Originality win rate | 95.00% | 83.5%-98.6% | Higher means less default. |
| Overall win rate | 70.00% | 54.6%-81.9% | Higher means the judge preferred Creative. |
| Valid win rate | 50.00% | 35.2%-64.8% | Creative won without losing feasibility. |
| Feasibility loss rate | 37.50% | 24.2%-53.0% | Lower means fewer practicality losses. |
| Overcomplication rate | 0.00% | 0.0%-8.8% | Lower means fewer bloated answers. |

## How To Read This

This benchmark does not use a hard pass/fail threshold. The rates describe observed behavior on the committed task run, and the confidence intervals show uncertainty from the sample size.

## Per Category Breakdown

| Category | Valid win rate | Originality win rate | Feasibility loss rate |
| --- | ---: | ---: | ---: |
| agent_workflow | 40.00% | 100.00% | 60.00% |
| code_architecture | 20.00% | 100.00% | 60.00% |
| debugging | 20.00% | 100.00% | 80.00% |
| design | 40.00% | 80.00% | 60.00% |
| naming | 60.00% | 100.00% | 40.00% |
| product_strategy | 100.00% | 100.00% | 0.00% |
| research_framing | 80.00% | 100.00% | 0.00% |
| writing | 40.00% | 80.00% | 0.00% |

## Top 5 Creative Wins

- `naming_002`: Both satisfy the request, but B offers a more memorable and original tool name while staying clear and free of buzzwords.
- `writing_001`: B is more distinctive and memorable, with a stronger voice. A is polished and usable but closer to familiar SaaS phrasing.
- `naming_003`: A gives a sharper, more distinctive single recommendation with strong rationale and usable taglines. B has several decent options but is more list-like and includes more generic or less ownable names.
- `naming_004`: Both are strong, but B offers a sharper primary name, a usable tagline, and several memorable alternatives with clearer positioning for engineering audiences.
- `naming_001`: B is more distinctive and specific: it names a concrete mechanism for escaping default answers rather than using a broader metaphor. A is clear and usable, but 'Escape Velocity' is a more familiar metaphor and less precise.

## Top 5 Creative Failures

- `naming_005`: A is clearer, simpler, and directly communicates the benchmark’s purpose. B is more original but less immediately understandable as a benchmark name.
- `writing_003`: A is clearer, more directly usable as a homepage subheading, and offers several strong alternatives. B is punchier and original, but slightly less clear with phrases like “quality moves.”
- `writing_004`: B is more directly usable as a product update, with clearer structure, customer impact, alternatives, and rationale. A is good but includes an out-of-place meta note at the end.
- `code_architecture_002`: Both answers give clear small-boundary architectures, but B is slightly more feasible and simpler because it builds on proven form libraries while keeping schemas, hooks, UI fields, and layout feature-owned rather than inventing a custom lifecycle layer.
- `code_architecture_004`: Both are strong and recommend sharing only retry mechanics while keeping policies explicit. B is slightly clearer and more feasible, with practical migration, hooks for special cases, observability, and fewer abstraction/code inconsistencies than A.

## Limitations

This benchmark uses automated judging, so it is not a replacement for human review. It is a fast first-pass test for whether Creative changes outputs in a useful direction.

## Next Steps

Add harder tasks, run with multiple model pairs, inspect failures, and compare against human ratings.
