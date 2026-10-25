# Portable benchmark

Measures quality separately from execution-profile cost/depth. It is not a model runner.

## Exact protocol

Use identical model, system/developer prompt, user prompt, and self-contained context for paired runs. Baseline has no skill; light, balanced, and performance use the same skill. Randomize condition order per run and record it. Run every case at least 3 times (5 recommended), keeping model settings, tools, seed, and temperature fixed when supported. Record unavailable numeric telemetry as JSON null, never zero or an estimate.

Blind human or judge evaluators to condition labels and score with rubric.yaml. Compare baseline to each profile on paired quality scores; separately compare profiles on tokens, elapsed time, tool calls, files read, and depth evidence. Text similarity or difference alone is never quality evidence.

## Metrics and cautions

aggregate.py reports n, mean/median/stdev quality, paired deltas, win/tie/loss, and telemetry averages. Missing rubric dimensions are excluded from a case score. Recommended win threshold is 0.25 points with no critical regression. Small fixtures, evaluator drift, stochasticity, non-independent runs, and unavailable telemetry limit claims; use a paired test or confidence interval externally when appropriate.

## Recording

Copy result-template.json for one case/condition/run into results/, fill required fields, preserve nulls, and record evaluator blinding metadata. Run: python3 aggregate.py --results-dir results, optionally with --json.
