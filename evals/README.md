# Evaluation fixtures

These declarative acceptance cases validate the skill contract; they are not a model runner.

## Files

- `generation-fixtures.yaml` — point generation, composition, and review prompts.
- `audit-fixtures.yaml` — project-audit behavior.
- `context-fixtures.yaml` — Context Gate, evidence, stage, and remediation cases.
- `expected-invariants.yaml` — response-wide invariants and benchmark coverage requirements.

## How to validate

1. Run the skill with each fixture prompt.
2. Confirm the exact 14-key top-level output contract, including `project_context`.
3. Confirm findings retain exactly the 12 fields in [decision-system.md](../references/decision-system.md); fixture IDs are not finding scenarios.
4. Confirm context evidence states, precedence, confidence, risk gate, cache ledger, and no-invention behavior.
5. Confirm high-risk requests stop without declared or verified context; confirm remediation changes only explicitly authorized copy.
6. Run `python3 -m unittest discover -s skills/adaptive-product-language/benchmarks -p 'test_*.py'` to validate all 30 standard-library fixture scenarios, required context fields, UI composition coverage, positive controls, and materialized fixtures.

## Declarative evals versus benchmark

These are declarative contract fixtures, not repeated model measurements. The paired benchmark is documented in [../benchmarks/README.md](../benchmarks/README.md). Benchmark execution telemetry is optional and observed-only; blind quality evaluation is a separate step.
