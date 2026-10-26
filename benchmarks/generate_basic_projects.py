#!/usr/bin/env python3
"""Materialize the standard-library-only basic synthetic benchmark."""
import argparse
import json
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
MANIFEST = HERE / "basic-environments.yaml"


def safe_output(value):
    path = pathlib.Path(value).expanduser().resolve()
    forbidden = {pathlib.Path("/"), pathlib.Path.home().resolve(), HERE.parent.resolve(), pathlib.Path("/Volumes/intento1/Repos/casamapa").resolve()}
    if path in forbidden or len(path.parts) < 3 or any(base in path.parents for base in (HERE.parent.resolve(), pathlib.Path("/Volumes/intento1/Repos/casamapa").resolve())):
        raise ValueError(f"unsafe output path: {path}")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    output = safe_output(args.output_dir)
    if output.exists() and args.clean:
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    records = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for row in records:
        directory = output / row["id"]
        directory.mkdir()
        context_keys = (
            "id", "product_type", "audience", "surface", "channel", "business_model", "scenario",
            "locale", "risk", "stage", "context", "behavior", "constraints", "invariants",
            "findings", "positive_control", "composition", "rubric_applicability",
        )
        (directory / "context.yaml").write_text(json.dumps({key: row[key] for key in context_keys}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (directory / "copy.txt").write_text(row["current_copy"] + "\n", encoding="utf-8")
        (directory / "prompt.txt").write_text(row["prompt"] + "\n", encoding="utf-8")
        (directory / "expected.yaml").write_text(json.dumps({"findings": row["findings"], "positive_control": row["positive_control"]}, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(records)} projects in {output}")


if __name__ == "__main__":
    main()
