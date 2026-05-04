# Creative

Creative is an installable Codex skill that pushes an LLM away from default answers while keeping the answer useful, feasible, and simple.

This repo contains Creative, benchmark code, a default task set, and generated benchmark results.

Current result: Creative made answers much more original than baseline and won most overall comparisons in the committed 40-task real run. The default task set now has 80 prompts; rerun the benchmark to refresh results for the current skill and larger task set.

## Current real benchmark result

| Plain-English Question | Answer |
| --- | --- |
| Does Creative make answers more original? | Yes, strongly. |
| Does Creative usually beat the baseline? | Often. |
| Does Creative win without losing feasibility? | Mixed. |
| Does Creative become too complicated? | No. |

The benchmark result is: **Creative changes answers in the intended direction. The strongest evidence is originality; the main caveat is feasibility tradeoff.**

Technical details:

<!-- BENCHMARK_TABLE_START -->
| Metric | Value | 95% CI | Interpretation |
| --- | ---: | ---: | --- |
| Originality win rate | 95.00% | 83.5%-98.6% | Higher means less default. |
| Overall win rate | 70.00% | 54.6%-81.9% | Higher means the judge preferred Creative. |
| Valid win rate | 50.00% | 35.2%-64.8% | Creative won without losing feasibility. |
| Feasibility loss rate | 37.50% | 24.2%-53.0% | Lower means fewer practicality losses. |
| Overcomplication rate | 0.00% | 0.0%-8.8% | Lower means fewer bloated answers. |
<!-- BENCHMARK_TABLE_END -->

## What is CreativeBench?

CreativeBench is an automated benchmark for testing whether Creative changes LLM outputs in a useful direction. It compares normal answers against answers generated with Creative, then judges the pair blindly.

## What is Creative?

Creative asks the model to reject the first clean answer, generate stronger alternatives with specific moves, and keep only the idea that is more useful than the obvious/default answer. The installable file lives at `skills/creative/SKILL.md`.

## Why benchmark this?

Prompts that ask for originality can drift into novelty without utility. CreativeBench tests whether Creative produces less default answers while preserving usefulness, feasibility, specificity, and simplicity.

The benchmark is automated. It uses blind pairwise judging. The headline signals are originality win rate, overall win rate, valid win rate, feasibility loss rate, and overcomplication rate. The benchmark punishes weird but useless answers.

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
It runs API calls in parallel with `MAX_WORKERS=12` by default. Lower this value in `.env` if you hit rate limits.

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

`creative_valid_win_rate` is the strictest "did Creative really win?" metric. It counts cases where the Creative answer wins overall, is not nonsense, and does not lose feasibility. Higher is better.

`creative_overall_win_rate` measures whether the blind judge preferred Creative overall. Higher is better.

`creative_originality_win_rate` measures whether Creative is less default than baseline. Higher is better.

`creative_feasibility_loss_rate` catches cases where Creative becomes less practical than baseline. Lower is better.

`creative_overcomplication_rate` catches answers that become elaborate without earning the complexity. Lower is better.

The report does not use hard pass/fail thresholds. It reports observed rates and 95% confidence intervals so readers can see the effect size and uncertainty.

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

Automated judging can be biased by the judge model. Results may change across model versions. The current committed result has 40 judged pairs, while the default task set now contains 80 prompts for the next run. The benchmark measures a useful signal, not final product quality.
