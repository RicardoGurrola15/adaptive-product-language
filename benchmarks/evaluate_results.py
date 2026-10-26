#!/usr/bin/env python3
"""Create blind rubric packets and report completed evaluator scores.

The tool never invents quality scores. `create` emits null templates; `report`
requires complete 0..4 scores and preserves condition pairing through pair_id.
"""
import argparse
import hashlib
import itertools
import json
import pathlib
import random
import re
import statistics
import uuid

from benchmark_protocol import BENCHMARK_PROTOCOL_VERSION, require_current_protocol

DIMENSIONS = (
    'completeness', 'context_fit', 'specificity', 'coherence', 'naturalness_non_robotic_rhythm', 'commercial_congruence', 'cta_clarity', 'locale_quality', 'claims_boundary',
)
TELEMETRY_FIELDS = (
    "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens",
    "elapsed_ms", "tool_calls", "stage_timings",
    "candidate_files", "files_read", "references", "searches", "context_bytes",
    "escalations", "cache_hit", "cache_miss", "profile", "stop_reason",
    "interruptions", "changed_text_count", "preserved_text_count",
)
META = {"checkpoint.json", "aggregate.json", "scored-report.json"}
BLIND_CONTEXT_KEYS = {
    "product_type", "audience", "surface", "channel", "business_model", "scenario",
    "locale", "risk", "stage", "context", "behavior", "constraints", "invariants",
}
BLIND_METADATA_KEYS = {
    "executionprofile", "profile", "condition", "provider", "model", "runid",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def result_files(results_dir):
    rows = []
    for path in sorted(pathlib.Path(results_dir).glob("*.json")):
        if path.name in META:
            continue
        value = read_json(path)
        if {"case_id", "condition", "run_id", "output"} <= set(value):
            require_current_protocol(value, path)
            rows.append((path, value))
    return rows


def fixture_context(case_id, projects_dir):
    path = pathlib.Path(projects_dir) / case_id
    context = {}
    context_file = path / "context.yaml"
    if context_file.exists():
        value = read_json(context_file)
        # Allow only evaluator-facing task context. IDs, conditions, composition,
        # and answer-key metadata stay in the private blind map/source fixture.
        context["context.yaml"] = {key: value[key] for key in BLIND_CONTEXT_KEYS if key in value}
    for name in ("copy.txt", "prompt.txt"):
        file = path / name
        if file.exists():
            context[name] = file.read_text(encoding="utf-8")
    return context


def stable_label(seed, run_id):
    return "sample-" + hashlib.sha256(f"{seed}:{run_id}".encode()).hexdigest()[:12]


def _metadata_key(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def _remove_blind_metadata(value):
    if isinstance(value, dict):
        return {
            key: _remove_blind_metadata(item)
            for key, item in value.items()
            if _metadata_key(key) not in BLIND_METADATA_KEYS
        }
    if isinstance(value, list):
        return [_remove_blind_metadata(item) for item in value]
    return value


def redact_blind_task_output(output):
    """Remove structured execution metadata without touching product evidence."""
    if not isinstance(output, str):
        return _remove_blind_metadata(output)
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        parsed = None
    if parsed is not None:
        return json.dumps(_remove_blind_metadata(parsed), ensure_ascii=False)

    metadata_line = re.compile(
        r"^(?P<indent>\s*(?:[-*]\s+)?)(?:['\"]?)(?:execution[_ -]?profile|profile|condition|provider|model|run[_ -]?id)(?:['\"]?)\s*:.*$",
        re.IGNORECASE,
    )
    return "\n".join(line for line in output.splitlines() if not metadata_line.match(line))


def create(args):
    rows = result_files(args.results_dir)
    if not rows:
        raise SystemExit("No benchmark result JSON files found")
    output = pathlib.Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    seed = args.seed or uuid.uuid4().hex
    packets, templates, mapping = [], [], {}
    for path, row in rows:
        label = stable_label(seed, row["run_id"])
        mapping[label] = {
            "run_id": row["run_id"],
            "case_id": row["case_id"],
            "condition": row["condition"],
            "pair_id": str(row.get("pair_id") or row.get("replicate_id") or row["run_id"]),
            "source": str(path),
            "rubric_applicability": row.get("rubric_applicability", {}),
        }
        # Do not expose case, provider, condition, or profile in the packet.
        packets.append({
            "blind_id": label,
            "task_output": redact_blind_task_output(row["output"]),
            "evaluation_instructions": "Score only the output against the supplied context and rubric. Do not infer condition, provider, profile, or skill usage. Record evidence for every dimension and state why an accurate positive control needs no change.",
            "context": fixture_context(row["case_id"], args.projects_dir),
            "rubric_dimensions": {dimension: {"score": None, "evidence": ""} for dimension in DIMENSIONS},
            "critical_regression": None,
            "notes": "",
        })
        templates.append({
            "blind_id": label,
            "evaluator_id": "",
            "applicable_dimensions": [dimension for dimension in DIMENSIONS if mapping[label]["rubric_applicability"].get(dimension, True)],
            **{dimension: None for dimension in DIMENSIONS},
            "critical_regression": None,
            "evidence": "",
            "notes": "",
        })
    random.Random(seed).shuffle(packets)
    (output / "blind-packets.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in packets) + "\n", encoding="utf-8")
    (output / "score-template.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in templates) + "\n", encoding="utf-8")
    (output / "blind-map.json").write_text(json.dumps({"benchmark_protocol_version": BENCHMARK_PROTOCOL_VERSION, "seed": seed, "mapping": mapping}, indent=2) + "\n", encoding="utf-8")
    print(f"created {len(packets)} blind packets in {output}")
    print(f"Score one completed copy per evaluator: {output / 'score-template.jsonl'}")
    print(f"Keep private until scoring is complete: {output / 'blind-map.json'}")


def applicable_dimensions(row, expected=None):
    dimensions = row.get("applicable_dimensions")
    if not isinstance(dimensions, list) or set(dimensions) - set(DIMENSIONS):
        raise SystemExit(f"{row.get('blind_id')}: applicable_dimensions must be a subset of rubric dimensions")
    if not dimensions:
        raise SystemExit(f"{row.get('blind_id')}: at least one rubric dimension must apply")
    if expected is not None and set(dimensions) != set(expected):
        raise SystemExit(f"{row.get('blind_id')}: applicability differs from the fixture")
    return tuple(dimensions)


def parse_scores(paths, expected_ids, applicability_by_id=None, allow_partial=False):
    rows = []
    seen = set()
    for path in paths:
        for line_number, line in enumerate(pathlib.Path(path).read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid JSON: {exc}")
            blind_id = value.get("blind_id")
            evaluator_id = value.get("evaluator_id")
            if blind_id not in expected_ids:
                raise SystemExit(f"{path}:{line_number}: unknown blind_id {blind_id!r}")
            if not isinstance(evaluator_id, str) or not evaluator_id.strip():
                raise SystemExit(f"{path}:{line_number}: evaluator_id is required")
            key = (blind_id, evaluator_id)
            if key in seen:
                raise SystemExit(f"duplicate score for {blind_id} by {evaluator_id}")
            seen.add(key)
            expected = applicability_by_id.get(blind_id) if applicability_by_id else None
            applicable = applicable_dimensions(value, expected)
            for dimension in DIMENSIONS:
                score = value.get(dimension)
                if dimension not in applicable and score is not None:
                    raise SystemExit(f"{blind_id}: {dimension} must be null when not applicable")
                if dimension in applicable and (isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 4):
                    raise SystemExit(f"{blind_id}: {dimension} must be a number from 0 to 4")
            if not isinstance(value.get("critical_regression"), bool):
                raise SystemExit(f"{blind_id}: critical_regression must be boolean")
            if not isinstance(value.get("evidence"), str) or not value["evidence"].strip():
                raise SystemExit(f"{blind_id}: evidence is required; scores without evidence are incomplete")
            rows.append(value)
    if not rows:
        raise SystemExit("No completed scores found")
    evaluator_ids = {row["evaluator_id"] for row in rows}
    if allow_partial:
        covered = {row["blind_id"] for row in rows}
        if covered != expected_ids:
            raise SystemExit(f"partial evaluation is incomplete; missing={sorted(expected_ids - covered)}, extra={sorted(covered - expected_ids)}")
    else:
        for evaluator_id in evaluator_ids:
            ids = {row["blind_id"] for row in rows if row["evaluator_id"] == evaluator_id}
            if ids != expected_ids:
                missing = sorted(expected_ids - ids)
                extra = sorted(ids - expected_ids)
                raise SystemExit(f"{evaluator_id}: incomplete score set; missing={missing}, extra={extra}")
    return rows, sorted(evaluator_ids)


def row_quality(row):
    return statistics.mean(row[dimension] for dimension in applicable_dimensions(row))


def agreement(rows):
    by_packet = {}
    for row in rows:
        by_packet.setdefault(row["blind_id"], []).append(row)
    judges = sorted({row["evaluator_id"] for row in rows})
    if len(judges) < 2:
        return None
    differences, exact = [], []
    for values in by_packet.values():
        for left, right in itertools.combinations(values, 2):
            differences.append(abs(row_quality(left) - row_quality(right)))
            exact.append(row_quality(left) == row_quality(right))
    return {
        "available": True,
        "judges": len(judges),
        "packets": len(by_packet),
        "overlap_packets": sum(len(values) >= 2 for values in by_packet.values()),
        "mean_absolute_difference": round(statistics.mean(differences), 4) if differences else None,
        "exact_agreement_rate": round(sum(exact) / len(exact), 4) if exact else None,
    }


def source_records(mapping):
    records = []
    for meta in mapping.values():
        path = pathlib.Path(meta["source"])
        if not path.exists():
            continue
        try:
            value = read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value.get("telemetry"), dict):
            records.append((meta, value))
    return records


def efficiency_report(mapping):
    rows = source_records(mapping)
    grouped = {}
    for meta, record in rows:
        grouped.setdefault((meta["case_id"], meta["condition"]), []).append(record)
    summaries = []
    observed = {key: 0 for key in TELEMETRY_FIELDS}
    means = {key: None for key in TELEMETRY_FIELDS}
    values = {key: [] for key in TELEMETRY_FIELDS}
    for (case_id, condition), items in sorted(grouped.items()):
        telemetry_mean = {}
        telemetry_observed = {}
        telemetry_values = {}
        for key in TELEMETRY_FIELDS:
            present = [item["telemetry"].get(key) for item in items if item["telemetry"].get(key) is not None]
            numeric = [value for value in present if type(value) in (int, float)]
            telemetry_mean[key] = round(statistics.mean(numeric), 4) if numeric else None
            telemetry_observed[key] = len(present)
            telemetry_values[key] = present or None
            observed[key] += len(present)
            values[key].extend(present)
        summaries.append({
            "case_id": case_id,
            "condition": condition,
            "n": len(items),
            "telemetry_mean": telemetry_mean,
            "telemetry_observed": telemetry_observed,
            "telemetry_values": telemetry_values,
        })
    for key in TELEMETRY_FIELDS:
        numeric = [value for value in values[key] if type(value) in (int, float)]
        means[key] = round(statistics.mean(numeric), 4) if numeric else None
        values[key] = values[key] or None
    return {
        "telemetry_is_observed_only": True,
        "fields": list(TELEMETRY_FIELDS),
        "summaries": summaries,
        "telemetry_mean": means,
        "telemetry_observed": observed,
        "telemetry_values": values,
    }


def report(args):
    output = pathlib.Path(args.output_dir)
    blind_map = read_json(output / "blind-map.json")
    require_current_protocol(blind_map, output / "blind-map.json")
    mapping = blind_map["mapping"]
    applicability = {
        blind_id: tuple(dimension for dimension in DIMENSIONS if meta.get("rubric_applicability", {}).get(dimension, True))
        for blind_id, meta in mapping.items()
    }
    scores, evaluators = parse_scores(args.scores, set(mapping), applicability, args.allow_partial)
    # Average only completed evaluator scores for each blind packet; no missing
    # score is substituted and agreement is reported separately.
    packet_scores = {}
    for row in scores:
        packet_scores.setdefault(row["blind_id"], []).append(row_quality(row))
    packet_quality = {blind_id: statistics.mean(values) for blind_id, values in packet_scores.items()}
    grouped = {}
    for blind_id, value in packet_quality.items():
        meta = mapping[blind_id]
        grouped.setdefault((meta["case_id"], meta["pair_id"]), {})[meta["condition"]] = {
            "quality": value,
            "critical_regression": any(row["critical_regression"] for row in scores if row["blind_id"] == blind_id),
        }

    summaries = []
    for case_id in sorted({meta["case_id"] for meta in mapping.values()}):
        for condition in sorted({meta["condition"] for meta in mapping.values() if meta["case_id"] == case_id}):
            values = [quality for blind_id, quality in packet_quality.items() if mapping[blind_id]["case_id"] == case_id and mapping[blind_id]["condition"] == condition]
            summaries.append({"case_id": case_id, "condition": condition, "n": len(values), "quality_mean": round(statistics.mean(values), 4) if values else None})

    pairs = []
    for (case_id, pair_id), conditions in sorted(grouped.items()):
        baseline = conditions.get("baseline")
        if baseline is None:
            continue
        for condition in ("light", "balanced", "performance"):
            if condition in conditions:
                current = conditions[condition]
                delta = current["quality"] - baseline["quality"]
                critical = current["critical_regression"]
                pairs.append({
                    "case_id": case_id, "pair_id": pair_id, "condition": condition, "pairs": 1,
                    "mean_delta": round(delta, 4), "critical_regression": critical,
                    "wins": int(delta >= .25 and not critical),
                    "ties": int(abs(delta) <= .25), "losses": int(delta < -.25),
                })

    evaluator_coverage = {
        evaluator: sum(row["evaluator_id"] == evaluator for row in scores)
        for evaluator in evaluators
    }
    validation = {
        "completeness": len(packet_scores) == len(mapping),
        "allow_partial": args.allow_partial,
        "evaluator_coverage": evaluator_coverage,
        "range_valid": True,
        "evaluators": evaluators,
        "score_rows": len(scores),
        "blind_packets": len(mapping),
    }
    result = {
        "benchmark_protocol_version": BENCHMARK_PROTOCOL_VERSION,
        "records": len(scores),
        "summaries": summaries,
        "paired_deltas": pairs,
        "method": "blind rubric scoring; no heuristic or invented scores",
        "validation": validation,
        "agreement": agreement(scores),
        "quality": {
            "dimensions": list(DIMENSIONS),
            "summaries": summaries,
            "paired_deltas": pairs,
            "score_rows": len(scores),
            "method": "completed flat rubric scores only",
        },
        "efficiency": efficiency_report(mapping),
    }
    (output / "scored-report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    agreement_text = json.dumps(result["agreement"], sort_keys=True) if result["agreement"] is not None else "unavailable (requires overlapping packets scored by at least two evaluators)"
    lines = ["# Blind rubric report", "", "This report uses completed blind scores and does not infer quality from text differences.", "", f"- Score rows: {len(scores)}", f"- Blind packets: {len(mapping)}", f"- Evaluators: {', '.join(evaluators)}", f"- Agreement: {agreement_text}", "", "## Quality", "", "| Case | Condition | N | Mean score |", "|---|---|---:|---:|"]
    lines += [f"| {item['case_id']} | {item['condition']} | {item['n']} | {item['quality_mean']:.2f}/4 |" for item in summaries]
    lines += ["", "## Paired deltas", "", "| Case | Pair | Condition | Delta | Wins | Ties | Losses |", "|---|---|---|---:|---:|---:|---:|"]
    lines += [f"| {item['case_id']} | {item['pair_id']} | {item['condition']} | {item['mean_delta']:.2f} | {item['wins']} | {item['ties']} | {item['losses']} |" for item in pairs]
    lines += ["", "## Efficiency", "", "Observed source telemetry only; missing values remain unavailable.", "", "| Field | Observed | Mean |", "|---|---:|---:|"]
    lines += [f"| {key} | {result['efficiency']['telemetry_observed'][key]} | {result['efficiency']['telemetry_mean'][key]} |" for key in TELEMETRY_FIELDS]
    (output / "scored-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"report: {output / 'scored-report.md'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create_parser = sub.add_parser("create")
    create_parser.add_argument("--results-dir", required=True)
    create_parser.add_argument("--projects-dir", default="/tmp/apl-basic-projects")
    create_parser.add_argument("--output-dir", required=True)
    create_parser.add_argument("--seed")
    create_parser.set_defaults(func=create)
    report_parser = sub.add_parser("report")
    report_parser.add_argument("--output-dir", required=True)
    report_parser.add_argument("--scores", nargs="+", required=True)
    report_parser.add_argument("--allow-partial", action="store_true", help="allow complementary evaluator subsets; their union must cover every blind packet")
    report_parser.set_defaults(func=report)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
