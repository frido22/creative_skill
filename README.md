# Creative

Creative is an installable Codex skill that pushes an LLM away from default answers while keeping the answer useful, feasible, and simple.

This repo contains Creative, benchmark code, a default task set, and generated example results that make the benchmark pipeline visible.

Important: the committed numbers below are dry-run example results. They prove the benchmark code works without API keys. They do not prove Creative beats the baseline on real model outputs yet. To test that claim, run the real benchmark with `OPENAI_API_KEY`.

## Example dry-run benchmark result

<!-- BENCHMARK_TABLE_START -->
| Metric | Value | Threshold | Status |
| --- | ---: | --- | --- |
| `creative_valid_win_rate` | 75.00% | >= 60% | PASS |
| `creative_originality_win_rate` | 90.00% | >= 70% | PASS |
| `creative_feasibility_loss_rate` | 10.00% | <= 15% | PASS |
| `creative_overcomplication_rate` | 10.00% | <= 20% | PASS |
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

## Run dry benchmark

Dry run mode does not call the OpenAI API. It uses deterministic fake answers and fake judgments so CI can verify the benchmark pipeline.

```bash
python -m creative_bench.cli run --dry-run
```

Dry run outputs:

- `results/example_summary.json`
- `results/example_report.md`

## Run real benchmark

Real runs require `OPENAI_API_KEY`. This is the run that tests whether Creative actually changes model outputs compared with baseline.

```bash
cp .env.example .env
# Add your API key to .env
python -m creative_bench.cli run
```

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

`creative_valid_win_rate` is the main metric. It counts cases where the creative answer wins overall, is not nonsense, and does not lose feasibility.

`creative_originality_win_rate` measures whether the creative answer is more original than baseline.

`creative_feasibility_loss_rate` catches cases where creativity makes the answer less practical.

`creative_overcomplication_rate` catches answers that become elaborate without earning the complexity.

The report says PASS only if all success thresholds pass.

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
  results/example_summary.json
  results/example_report.md
  tests/
```

## Limitations

Automated judging can be biased by the judge model. The task set is intentionally small. Results may change across model versions. The benchmark measures a useful signal, not final product quality.

## Future work

Add human-rated calibration sets, multiple judge models, adversarial tasks, confidence intervals, and richer failure analysis.
