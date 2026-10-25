# Evaluation fixtures

These declarative acceptance cases validate the skill contract; they are not a test runner.

## Files

- `generation-fixtures.yaml` — point generation and review prompts.
- `audit-fixtures.yaml` — project-audit behavior.
- `context-fixtures.yaml` — Context Gate, evidence, stage, and remediation cases.
- `expected-invariants.yaml` — response-wide invariants.

## How to validate

1. Run the skill with each fixture prompt.
2. Confirm the 14-key top-level output contract, including `project_context`.
3. Confirm findings retain exactly the 12 fields in [decision-system.md](../references/decision-system.md); fixture IDs are not finding scenarios.
4. Confirm context evidence states, precedence, confidence, risk gate, and no-invention behavior.
5. Confirm high-risk requests stop without declared or verified context; confirm remediation changes only explicitly authorized copy.

A host may automate these checks with any YAML parser and model-evaluation harness; the package requires neither.
