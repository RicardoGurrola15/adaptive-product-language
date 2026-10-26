#!/usr/bin/env python3
"""Create a deterministic provider run plan; never invokes a model."""
import argparse
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("codex", "gemini"), required=True)
    parser.add_argument("--scope", choices=("pilot", "full"), default="pilot")
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--seed", default="apl-pilot")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1")
    matrix = json.loads((HERE / "provider-matrix.yaml").read_text(encoding="utf-8"))
    cases = matrix["pilot_cases"] if args.scope == "pilot" else ["all-basic-environments"]
    rows = []
    for case in cases:
        for replicate_id in range(1, args.repetitions + 1):
            pair_id = f"{case}-rep-{replicate_id:02d}"
            for condition in matrix["conditions"]:
                token = hashlib.sha256(f"{args.seed}:{pair_id}:{condition}".encode()).hexdigest()[:8]
                rows.append({
                    "run_id": f"{pair_id}-{condition}-{token}",
                    "pair_id": pair_id,
                    "replicate_id": replicate_id,
                    "provider": args.provider,
                    "case_id": case,
                    "condition": condition,
                    "controls": matrix["controls"]["keep_fixed_within_provider"],
                })
    pathlib.Path(args.output).write_text(json.dumps({"provider": args.provider, "scope": args.scope, "repetitions": args.repetitions, "seed": args.seed, "runs": rows}, indent=2) + "\n", encoding="utf-8")
    print(f"prepared {len(rows)} runs for {args.provider} ({args.scope}, {args.repetitions} repetitions)")


if __name__ == "__main__":
    main()
