#!/usr/bin/env python3
"""Aggregate completed benchmark records without inventing scores or telemetry."""
import argparse
import json
import statistics
from pathlib import Path

from benchmark_protocol import BENCHMARK_PROTOCOL_VERSION, require_current_protocol

REQUIRED = {"benchmark_protocol_version", "case_id", "condition", "run_id", "model", "output", "quality_scores", "expected_findings_found", "telemetry", "evaluator"}
CONDITIONS = ("baseline", "light", "balanced", "performance")
ENV_KEYS = {"id", "revision", "scope"}
TELEMETRY_KEYS = (
    "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens",
    "elapsed_ms", "tool_calls", "stage_timings",
    "candidate_files", "files_read", "references", "searches", "context_bytes",
    "escalations", "cache_hit", "cache_miss", "profile", "stop_reason",
    "interruptions", "changed_text_count", "preserved_text_count",
)
QUALITY_KEYS = (
    'completeness', 'context_fit', 'specificity', 'coherence', 'naturalness_non_robotic_rhythm', 'commercial_congruence', 'cta_clarity', 'locale_quality', 'claims_boundary',
)


def average(values):
    return round(statistics.mean(values), 4) if values else None


def quality(record):
    applicable = record.get("rubric_applicability", {key: True for key in QUALITY_KEYS})
    values = [record.get("quality_scores", {}).get(key) for key in QUALITY_KEYS if applicable.get(key, True)]
    values = [value for value in values if isinstance(value, (int, float))]
    return statistics.mean(values) if values else None


def environment(record, filename):
    value = record.get("project_environment")
    if value is None:
        return {"id": "standalone", "revision": None, "scope": "portable fixture"}
    if not isinstance(value, dict) or set(value) != ENV_KEYS or not all(isinstance(value[key], str) and value[key].strip() for key in ENV_KEYS):
        raise SystemExit(f"{filename}: project_environment must contain non-empty string id, revision, scope")
    return value


def provider(record):
    model = record.get("model")
    value = model.get("provider") if isinstance(model, dict) else None
    value = value or record.get("provider")
    return value.strip() if isinstance(value, str) and value.strip() else "unknown"


def pair_id(record):
    value = record.get("pair_id") or record.get("replicate_id")
    if value is not None:
        return str(value)
    # Backward-compatible fallback for old records. It will not manufacture a
    # pair across conditions; diagnostics make the missing pairing explicit.
    return str(record["run_id"])


def numeric_telemetry(records, key):
    return [record.get("telemetry", {}).get(key) for record in records if type(record.get("telemetry", {}).get(key)) in (int, float)]


def observed_telemetry(records, key):
    return [record.get("telemetry", {}).get(key) for record in records if record.get("telemetry", {}).get(key) is not None]


def coverage_values(records):
    values = []
    for record in records:
        value = record.get("coverage")
        if isinstance(value, (int, float)) and 0 <= value <= 1:
            values.append(value)
        elif isinstance(value, dict) and isinstance(value.get("score"), (int, float)) and 0 <= value["score"] <= 1:
            values.append(value["score"])
    return values


def diagnostics(records):
    counts = {}
    for record in records:
        for item in record.get("diagnostics", []):
            key = str(item)
            counts[key] = counts.get(key, 0) + 1
    return {"records_with_diagnostics": sum(bool(record.get("diagnostics")) for record in records), "counts": counts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    records = []
    for filename in sorted(Path(args.results_dir).glob("*.json")):
        if filename.name in {"checkpoint.json", "aggregate.json"}:
            continue
        try:
            record = json.loads(filename.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{filename}: invalid JSON: {exc}")
        require_current_protocol(record, filename)
        missing = REQUIRED - set(record)
        if missing:
            raise SystemExit(f"{filename}: missing {sorted(missing)}")
        if record["condition"] not in CONDITIONS:
            raise SystemExit(f"{filename}: invalid condition")
        if not isinstance(record.get("quality_scores"), dict):
            raise SystemExit(f"{filename}: quality_scores must be an object")
        for key, value in record.get("quality_scores", {}).items():
            if value is not None and (not isinstance(value, (int, float)) or not 0 <= value <= 4):
                raise SystemExit(f"{filename}: quality score {key} must be null or 0..4")
        record["_environment"] = environment(record, filename)
        record["_provider"] = provider(record)
        record["_pair_id"] = pair_id(record)
        if "pair_id" not in record:
            record.setdefault("diagnostics", []).append("pair_id missing; no inferred cross-condition pairing")
        records.append(record)

    grouped = {}
    for record in records:
        key = (record["_provider"], record["_environment"]["id"], record["case_id"], record["condition"])
        grouped.setdefault(key, []).append(record)

    summaries = []
    for (provider_id, environment_id, case_id, condition), items in sorted(grouped.items()):
        scores = [quality(record) for record in items if quality(record) is not None]
        telemetry = {key: average(numeric_telemetry(items, key)) for key in TELEMETRY_KEYS}
        observed = {key: len(observed_telemetry(items, key)) for key in TELEMETRY_KEYS}
        values = {key: observed_telemetry(items, key) or None for key in TELEMETRY_KEYS}
        coverage = coverage_values(items)
        summaries.append({
            "provider": provider_id,
            "environment_id": environment_id,
            "case_id": case_id,
            "condition": condition,
            "n": len(items),
            "quality_mean": average(scores),
            "quality_median": round(statistics.median(scores), 4) if scores else None,
            "quality_stdev": round(statistics.stdev(scores), 4) if len(scores) > 1 else None,
            "quality_observed": len(scores),
            "coverage_mean": average(coverage),
            "coverage_observed": len(coverage),
            "telemetry_mean": telemetry,
            "telemetry_observed": observed,
            "telemetry_values": values,
            "diagnostics": diagnostics(items),
        })

    paired = []
    pair_groups = {}
    for record in records:
        key = (record["_provider"], record["_environment"]["id"], record["case_id"], record["_pair_id"])
        pair_groups.setdefault(key, {})[record["condition"]] = record
    for (provider_id, environment_id, case_id, pair), conditions in sorted(pair_groups.items()):
        baseline = quality(conditions["baseline"]) if "baseline" in conditions else None
        if baseline is None:
            continue
        for condition in CONDITIONS[1:]:
            current = quality(conditions[condition]) if condition in conditions else None
            if current is None:
                continue
            critical = bool(conditions[condition].get("evaluator", {}).get("critical_regression", False))
            paired.append({
                "provider": provider_id, "environment_id": environment_id, "case_id": case_id,
                "pair_id": pair, "condition": condition, "pairs": 1,
                "mean_delta": round(current - baseline, 4),
                "critical_regression": critical,
                "wins": int(current - baseline >= 0.25 and not critical),
                "ties": int(abs(current - baseline) <= 0.25),
                "losses": int(current - baseline < -0.25),
            })

    # Retain the existing summaries/paired_deltas names while adding explicit
    # quality, efficiency, coverage, and diagnostics sections.
    result = {
        "benchmark_protocol_version": BENCHMARK_PROTOCOL_VERSION,
        "aggregate_version": 2,
        "records": len(records),
        "summaries": summaries,
        "paired_deltas": paired,
        "quality": {"observed_scores": sum(quality(record) is not None for record in records), "unobserved_scores": sum(quality(record) is None for record in records)},
        "efficiency": {
            "telemetry_is_observed_only": True,
            "fields": list(TELEMETRY_KEYS),
            "telemetry_mean": {key: average(numeric_telemetry(records, key)) for key in TELEMETRY_KEYS},
            "telemetry_observed": {key: len(observed_telemetry(records, key)) for key in TELEMETRY_KEYS},
            "telemetry_values": {key: observed_telemetry(records, key) or None for key in TELEMETRY_KEYS},
        },
        "coverage": {"observed_records": sum(bool(coverage_values([record])) for record in records), "unobserved_records": sum(not coverage_values([record]) for record in records)},
        "diagnostics": diagnostics(records),
    }
    print(json.dumps(result, indent=2 if args.json else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
