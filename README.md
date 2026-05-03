# Creative

Creative is an installable Codex skill that pushes an LLM away from default answers while keeping the answer useful, feasible, and simple.

This repo contains Creative, benchmark code, a default task set, and generated benchmark results.

Current result: Creative passes the current benchmark thresholds. It is much more original than baseline, wins valid comparisons at the pass line, and stays within the current feasibility and overcomplication limits.

## Current real benchmark result

| Plain-English Question | Answer |
| --- | --- |
| Does Creative make answers more original? | Yes, strongly. |
| Does Creative reliably produce the better answer? | Yes, at the current threshold. |
| Does Creative stay practical? | Yes, at the current threshold. |
| Does Creative become too complicated? | No. |

The benchmark result is: **Creative changes answers in the intended direction and passes the current usefulness guardrails, but it is close to the valid-win threshold.**

Technical details:

<!-- BENCHMARK_TABLE_START -->
| Metric | Value | Threshold | Status |
| --- | ---: | --- | --- |
| `creative_originality_win_rate` | 95.00% | >= 70% | PASS |
| `creative_valid_win_rate` | 50.00% | >= 50% | PASS |
| `creative_feasibility_loss_rate` | 37.50% | <= 50% | PASS |
| `creative_overcomplication_rate` | 0.00% | <= 50% | PASS |
<!-- BENCHMARK_TABLE_END -->

## What is CreativeBench?

CreativeBench is an automated benchmark for testing whether Creative changes LLM outputs in a useful direction. It compares normal answers against answers generated with Creative, then judges the pair blindly.

## What is Creative?

Creative asks the model to reject the first clean answer, generate stronger alternatives with specific moves, and keep only the idea that is more useful than the obvious/default answer. The installable file lives at `skills/creative/SKILL.md`.

## Why benchmark this?

Prompts that ask for originality can drift into novelty without utility. CreativeBench tests whether Creative produces less default answers while preserving usefulness, feasibility, specificity, and simplicity.

The benchmark is automated. It uses blind pairwise judging. The main metric is `creative_valid_win_rate`. The benchmark punishes weird but useless answers.

CreativeBench is not a replacement for human evaluation, but it is a fast first-pass test.

## Benchmark method

For each task, CreativeBench generates two answers:

1. Baseline mode: answer normally.
2. Creative mode: answer using Creative.

It randomizes whether the baseline or creative answer appears as answer A. The judge does not see the labels. The judge scores originality, usefulness, feasibility, specificity, and simplicity, then chooses an overall winner or tie.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Install Creative

Use `skills/creative/SKILL.md` as the installable Creative skill file. In this repo, the benchmark code reads that exact file when it runs Creative mode.

## Run real benchmark

Real runs require `OPENAI_API_KEY`. This is the run that tests whether Creative actually changes model outputs compared with baseline.

```bash
cp .env.example .env
# Add your API key to .env
python -m creative_bench.cli run
```

By default the real benchmark uses `gpt-5.5` for both generation and judging with medium reasoning effort.

Real run outputs:

- `results/baseline.jsonl`
- `results/creative.jsonl`
- `results/pairs.jsonl`
- `results/judgments.jsonl`
- `results/summary.json`
- `results/report.md`

## Add new tasks

Edit `data/tasks.jsonl`. Each row must include:

- `task_id`
- `category`
- `prompt`

Prompts should describe situations where the obvious/default answer is likely too generic, too safe, or failing.

## Interpret metrics

`creative_valid_win_rate` is the main "did Creative really win?" metric. It counts cases where the Creative answer wins overall, is not nonsense, and does not lose feasibility. Higher is better.

`creative_originality_win_rate` measures whether Creative is less default than baseline. Higher is better.

`creative_feasibility_loss_rate` catches cases where Creative becomes less practical than baseline. Lower is better.

`creative_overcomplication_rate` catches answers that become elaborate without earning the complexity. Lower is better.

The report says PASS only if all success thresholds pass. A FAIL can still be useful: it shows exactly what needs tuning.

## Repository structure

```text
creative_bench/
  README.md
  LICENSE
  pyproject.toml
  .gitignore
  .env.example
  CODEX.md
  .github/workflows/ci.yml
  skills/creative/SKILL.md
  creative_bench/
  data/tasks.jsonl
  results/summary.json
  results/report.md
  tests/
```

## Limitations

Automated judging can be biased by the judge model. The task set is intentionally small. Results may change across model versions. The benchmark measures a useful signal, not final product quality.

## Future work

Add human-rated calibration sets, multiple judge models, adversarial tasks, confidence intervals, and richer failure analysis.
