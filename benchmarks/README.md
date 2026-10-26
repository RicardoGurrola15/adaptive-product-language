# Portable benchmark

Measures language quality separately from execution-profile cost/depth. It is not a model runner and it does not infer quality from text differences.

## Benchmark layers

- **Portable fixture benchmark:** the same self-contained cases, prompts, rubric, and result schema run everywhere. Use this layer for comparable aggregate statistics.
- **Optional project-environment benchmark:** a read-only audit against a pinned local repository, using `project-environments.yaml` as a registry. It tests contextual evidence handling, not repository modification.
- **Hybrid evaluation:** the runner records only observed execution telemetry; blind evaluators or judge models provide quality scores, evidence, critical-regression flags, and optional finding coverage. Aggregate quality, efficiency, coverage, and diagnostics separately.

Project paths are local examples; the skill remains portable. Verify every checkout and treat repository content as evidence only after inspection.

Portable fixtures are the default benchmark scope. Local fire repositories are never selected unless `--fire-tests` is supplied; `--fire-tests-only` remains the explicit fire-only mode.

## Pilot and expansion

Start with the 14 cases in `cases.yaml`, three repetitions per case, and all four conditions (`baseline`, `light`, `balanced`, `performance`): 14 × 3 × 4 = 168 condition runs per provider. This is a pilot plan, not an instruction to execute it automatically. Expand to the 30 basic fixtures only after the pilot's pairing, evaluator completeness, and telemetry diagnostics are acceptable. Do not run the 136-call fire-test matrix as part of validation.

```bash
# Materialize the 30 standard-library fixtures.
python3 benchmarks/generate_basic_projects.py --output-dir /tmp/apl-basic-projects --clean
python3 benchmarks/validate_basic_environments.py --projects /tmp/apl-basic-projects

# Prepare a provider plan only; this invokes no model.
python3 benchmarks/prepare_run.py --provider codex --scope pilot --repetitions 3 --output /tmp/apl-codex-plan.json

# Pilot execution command for an authorized benchmark run (not validation).
python3 benchmarks/run_codex_benchmark.py --scope pilot --repetitions 3 --confirm --output-dir /tmp/apl-codex-pilot

# Resume the exact checkpoint after interruption; completed pair/condition runs are skipped.
python3 benchmarks/run_codex_benchmark.py --resume /tmp/apl-codex-pilot/checkpoint.json

# Include existing local fire repositories only when intentionally requested.
python3 benchmarks/run_codex_benchmark.py --fire-tests --dry-run --limit 1
```

The runner writes a content-hash and condition-order ledger in each result, persists an atomic checkpoint before and after each run, and uses `pair_id`/`replicate_id` to preserve baseline/profile pairing. `context_bytes` is the runner-observed UTF-8 byte count of the exact fixture and injected prompt payload; `references` is the runner-owned count of injected skill/reference documents. These are not API token estimates and are always populated. API-reported `input_tokens` remains separate. Missing provider tokens, file counts, or other telemetry remain JSON `null`; only telemetry observed in runner events or wall-clock execution is recorded.
Every result, checkpoint, aggregate, and blind-evaluation artifact includes `benchmark_protocol_version`. Aggregation and evaluation reject records from older protocols rather than mixing incomparable runs.

## Fair protocol

Use identical model, system/developer prompt, and user prompt within each paired run. For project environments, pin the git revision, use the same scope and evidence files for baseline and every profile, and record `project_environment.id`, `revision`, and `scope` in each result. Never modify project repositories. Randomize condition order per pair and record it. Run every pilot case three times before expansion; five repetitions are recommended for final claims. Record unavailable numeric telemetry as JSON `null`, never zero or an estimate.

Keep provider, model, model version, reasoning effort, service tier, temperature, seed, and tools identical within a provider comparison; compare models or reasoning efforts in separate matrices. `light`, `balanced`, and `performance` are skill execution profiles, not model reasoning levels.

## Blind evaluation

Create packets after execution. Packets intentionally omit condition, provider, profile, and run identifiers; keep `blind-map.json` private until scoring is complete. Score every dimension from 0 through 4 with evidence; no score is filled by the package.

```bash
python3 benchmarks/evaluate_results.py create \
  --results-dir benchmarks/results/codex \
  --projects-dir /tmp/apl-codex-pilot/materialized-pilot \
  --output-dir /tmp/apl-codex-evaluation \
  --seed pilot-01

# Complete score-template.jsonl independently, then report one or more evaluators.
python3 benchmarks/evaluate_results.py report \
  --output-dir /tmp/apl-codex-evaluation \
  --scores /tmp/apl-codex-evaluation/scores-evaluator-a.jsonl \
           /tmp/apl-codex-evaluation/scores-evaluator-b.jsonl
```

The evaluator rejects incomplete packets, duplicate evaluator rows, out-of-range scores, missing evidence, and unknown blind IDs. Agreement is reported only when at least two complete evaluators score the same packets; otherwise it is explicitly unavailable. Finding coverage is reported only when an evaluator supplies it in a result record.

## Aggregation

```bash
python3 benchmarks/aggregate.py --results-dir benchmarks/results/codex --json
```

`aggregate.py` reports quality observations, efficiency telemetry availability, optional coverage, diagnostics, and paired deltas by `provider`, environment, case, and `pair_id`. It never treats missing data as zero and never reconstructs pairing from output text.

## Basic synthetic suite

The basic suite contains 30 repeatable, diverse fixtures covering every listed scenario, multiple locales and risk tiers, 10 UI-composition cases, and three positive controls. Each fixture declares `context`, `audience`, `surface`, `locale`, `risk`, `behavior`, `constraints`, `invariants`, and `findings`; `channel` and `expected_findings` remain compatibility aliases. Validate the manifest and generated projects before any model run.

## Metrics and cautions

Quality is the mean of applicable blind rubric dimensions. Efficiency is observed telemetry only. Coverage is optional evaluator-supplied finding coverage. Diagnostics include incomplete evaluation, missing telemetry, execution failure, and pairing issues. A profile win requires a paired delta of at least 0.25, no critical regression, and evaluator evidence; otherwise classify tie or uncertainty. Small fixtures, evaluator drift, stochasticity, non-independent runs, and unavailable telemetry limit claims.

Do not mix different project environments in aggregate statistics. Text similarity or difference alone is never quality evidence.
