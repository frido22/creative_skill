# Creative Benchmark Report

Creative benchmark result: measured effect

Creative made answers much less default and won most overall comparisons. The main caveat is feasibility: some creative answers were judged less practical than baseline.

This report uses real model outputs and automated blind judging.

Short version: this benchmark does not ask whether Creative is weird. It asks whether Creative is better than a normal answer while still being practical.

## Reader Summary

| Plain-English Question | Answer | What The Number Says |
| --- | --- | --- |
| Does Creative make answers more original? | Yes, strongly. | Creative was more original in 88% of tasks. |
| Does Creative usually beat the baseline? | Often. | Creative won the overall judgment in 79% of tasks. |
| Does Creative win without losing feasibility? | Mixed. | Valid win rate was 52%. |
| Does Creative become too complicated? | No. | Overcomplication was flagged in 2% of tasks. |

## Method

The benchmark generates baseline and creative answers for each task, randomizes answer order, and asks an automated judge to compare the pair without seeing labels.

## Judge Questions

The judge uses five plain-English questions, then chooses the better answer overall.

| Judge Question | What It Measures |
| --- | --- |
| Which answer is less default and brings a better non-obvious angle? | Originality |
| Which answer gives the user a better next move? | Usefulness |
| Which answer is more realistic to execute as written? | Feasibility |
| Which answer gives more concrete details, tradeoffs, or next actions? | Specificity |
| Which answer avoids unnecessary complexity, ceremony, or bloat? | Simplicity |

Tasks: 80
Generation model: gpt-5.5
Judge model: gpt-5.5

## Headline Metrics

| Metric | Value | 95% CI | Interpretation |
| --- | ---: | ---: | --- |
| Originality win rate | 87.50% | 78.5%-93.1% | Higher means less default. |
| Overall win rate | 78.75% | 68.6%-86.3% | Higher means the judge preferred Creative. |
| Valid win rate | 52.50% | 41.7%-63.1% | Creative won without losing feasibility. |
| Feasibility loss rate | 40.00% | 30.0%-51.0% | Lower means fewer practicality losses. |
| Overcomplication rate | 2.50% | 0.7%-8.7% | Lower means fewer bloated answers. |

## How To Read This

This benchmark does not use a hard pass/fail threshold. The rates describe observed behavior on the committed task run, and the confidence intervals show uncertainty from the sample size.

## Per Category Breakdown

| Category | Valid win rate | Originality win rate | Feasibility loss rate |
| --- | ---: | ---: | ---: |
| agent_workflow | 50.00% | 90.00% | 40.00% |
| code_architecture | 60.00% | 90.00% | 40.00% |
| debugging | 50.00% | 90.00% | 40.00% |
| design | 50.00% | 90.00% | 50.00% |
| naming | 60.00% | 90.00% | 30.00% |
| product_strategy | 40.00% | 90.00% | 60.00% |
| research_framing | 70.00% | 90.00% | 30.00% |
| writing | 40.00% | 70.00% | 30.00% |

## Top 5 Creative Wins

- `writing_003`: B gives a stronger primary subheading with a more concrete mechanism and payoff, plus sharper alternatives. A is clear and usable but more generic and expected.
- `naming_002`: Both answer the request well, but B has the sharper, more memorable name and a slightly more non-obvious framing while staying concrete and buzzword-free. A is simpler, but less distinctive.
- `writing_005`: B is more persuasive and grounded, with a sharper framing of settings as deferred product decisions and practical alternatives. A is clear and useful, but more conventional. B’s final meta line is unnecessary, but the memo itself is stronger.
- `naming_004`: B offers sharper, less default names and gives a clearer recommended choice with usable subtitles and rationale. A is solid and simple, but its options are more conventional and less decisive.
- `naming_003`: A is more curated and gives a sharper strategic angle with 'Unritual,' naming the enemy as dead rituals rather than generic productivity. B has some strong options, especially Redact, but it leans more on broad lists and includes more generic or less ownable names.

## Top 5 Creative Failures

- `writing_004`: B is a cleaner, more ready-to-use product update with a concrete feature, clear customer impact, exact change details, and a practical replacement path. A has a good framing idea but is more templated, full of placeholders, and includes a meta note that should not appear in the update.
- `naming_005`: A is clearer and more directly names the benchmark's purpose: penalizing quirkiness without value. B is more vivid and original, but the flytrap metaphor is slightly less immediately precise.
- `naming_001`: A is more specific and useful: it gives a sharper coding-adjacent concept, a clear definition, and an actionable method. B is simpler and memorable, but slightly more metaphorical and less concrete as a skill.
- `writing_002`: A is more concrete and better satisfies the need for non-generic personalization by referencing specific PRs, patterns, and a clear audit-style offer. B is feasible and simple, but its personalization is more placeholder-like and the added meta note weakens it as a ready-to-send email.
- `writing_001`: B has the more distinctive headline, but the extra meta explanation makes it less directly usable as a concise launch note. A is clean, ready to publish, and still avoids generic SaaS changelog language.

## Limitations

This benchmark uses automated judging, so it is not a replacement for human review. It is a fast first-pass test for whether Creative changes outputs in a useful direction.

## Next Steps

Add harder tasks, run with multiple model pairs, inspect failures, and compare against human ratings.
