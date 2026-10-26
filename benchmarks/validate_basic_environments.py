#!/usr/bin/env python3
"""Validate the standard-library-only basic benchmark manifest and materialized projects."""
import argparse
import json
import pathlib
import sys

REQUIRED = {
    "id", "product_type", "audience", "surface", "channel", "business_model",
    "scenario", "locale", "risk", "stage", "current_copy", "context", "behavior",
    "prompt", "constraints", "invariants", "findings", "expected_findings",
    "positive_control", "composition", "rubric_applicability",
}
SCENARIOS = {
    "cta", "empty-state", "error-recovery", "auth", "onboarding", "form", "password",
    "upload", "search", "filters", "marketplace", "checkout", "pricing", "paywall",
    "promo", "success", "loading", "permissions", "privacy", "notifications", "support",
    "help", "localization", "mixed-language", "terminology-drift", "unsupported-claim",
    "contradictory-flow", "audit", "remediation", "settings",
}
LOCALES = {"es-419", "en-US"}
RISKS = {"low", "medium", "high"}
RUBRIC_DIMENSIONS = {'completeness', 'context_fit', 'specificity', 'coherence', 'naturalness_non_robotic_rhythm', 'commercial_congruence', 'cta_clarity', 'locale_quality', 'claims_boundary'}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(rows):
    errors = []
    if len(rows) != 30:
        errors.append(f"expected exactly 30 records, got {len(rows)}")
    ids = [r.get("id") for r in rows]
    if len(set(ids)) != len(ids):
        errors.append("duplicate IDs")
    for row in rows:
        rid = row.get("id", "<missing-id>")
        missing = REQUIRED - set(row)
        errors.extend(f"{rid}: missing {key}" for key in sorted(missing))
        for key in ("product_type", "audience", "surface", "channel", "business_model", "context", "behavior", "prompt", "current_copy"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                errors.append(f"{rid}: {key} must be a non-empty string")
        if row.get("scenario") not in SCENARIOS:
            errors.append(f"{rid}: unknown scenario {row.get('scenario')!r}")
        if row.get("locale") not in LOCALES:
            errors.append(f"{rid}: unsupported locale {row.get('locale')!r}")
        if row.get("risk") not in RISKS:
            errors.append(f"{rid}: unsupported risk {row.get('risk')!r}")
        for key in ("constraints", "invariants", "findings", "expected_findings"):
            if not isinstance(row.get(key), list) or any(not isinstance(x, str) or not x.strip() for x in row[key]):
                errors.append(f"{rid}: {key} must be a list of non-empty strings")
        if row.get("findings") != row.get("expected_findings"):
            errors.append(f"{rid}: findings and expected_findings must match")
        positive = row.get("positive_control")
        if not isinstance(positive, bool):
            errors.append(f"{rid}: positive_control must be boolean")
        elif positive and row.get("findings"):
            errors.append(f"{rid}: positive control must have no findings")
        elif not positive and not row.get("findings"):
            errors.append(f"{rid}: non-positive fixture needs at least one expected finding")
        composition = row.get("composition")
        if composition is not None:
            if not isinstance(composition, dict) or not composition.get("kind") or not composition.get("elements") or not composition.get("states"):
                errors.append(f"{rid}: composition needs kind, elements, and states")
            elif not all(isinstance(x, str) and x.strip() for x in composition["elements"] + composition["states"]):
                errors.append(f"{rid}: composition elements/states must be non-empty strings")
        applicability = row.get("rubric_applicability")
        if not isinstance(applicability, dict) or set(applicability) != RUBRIC_DIMENSIONS or not all(isinstance(value, bool) for value in applicability.values()):
            errors.append(f"{rid}: rubric_applicability must declare every rubric dimension as boolean")
        elif not any(applicability.values()):
            errors.append(f"{rid}: at least one rubric dimension must apply")
    if {r.get("locale") for r in rows} != LOCALES:
        errors.append("locale coverage incomplete")
    if {r.get("scenario") for r in rows} != SCENARIOS:
        errors.append("scenario coverage incomplete")
    if len({r.get("product_type") for r in rows}) < 20:
        errors.append("product diversity incomplete: need at least 20 product types")
    if sum(1 for r in rows if r.get("composition")) < 8:
        errors.append("UI composition coverage incomplete: need at least 8 composed fixtures")
    if sum(1 for r in rows if r.get("positive_control")) < 3:
        errors.append("positive-control coverage incomplete: need at least 3 controls")
    return errors


def validate_projects(rows, projects):
    errors = []
    for row in rows:
        directory = projects / row["id"]
        for name in ("context.yaml", "copy.txt", "prompt.txt", "expected.yaml"):
            if not (directory / name).is_file():
                errors.append(f"{row['id']}: missing generated {name}")
        context_path = directory / "context.yaml"
        if context_path.is_file():
            try:
                context = load(context_path)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{row['id']}: invalid generated context: {exc}")
            else:
                for key in ("context", "audience", "surface", "locale", "risk", "behavior", "constraints", "invariants", "findings", "rubric_applicability"):
                    if key not in context:
                        errors.append(f"{row['id']}: generated context missing {key}")
        expected_path = directory / "expected.yaml"
        if expected_path.is_file():
            try:
                expected = load(expected_path)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{row['id']}: invalid generated expected fixture: {exc}")
            else:
                if expected.get("findings") != row["findings"]:
                    errors.append(f"{row['id']}: generated findings mismatch")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(pathlib.Path(__file__).with_name("basic-environments.yaml")))
    parser.add_argument("--projects", required=True)
    args = parser.parse_args()
    try:
        rows = load(pathlib.Path(args.manifest))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"manifest unreadable: {exc}", file=sys.stderr)
        return 1
    errors = validate_manifest(rows)
    errors.extend(validate_projects(rows, pathlib.Path(args.projects)))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"valid: {len(rows)} records, {sum(bool(r['composition']) for r in rows)} UI compositions, {sum(r['positive_control'] for r in rows)} positive controls, and generated projects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
