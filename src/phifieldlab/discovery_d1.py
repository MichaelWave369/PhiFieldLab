"""D1 research-mission proposal validation. No experiment execution.

The same limited JSON Schema is imported by Python and the React designer.
This module interprets only: object, array, string, integer, required,
additionalProperties:false, const, enum, pattern, min/max length/count/value.
Unknown schema keywords fail closed (except $schema/$id/title metadata).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from importlib.resources import files
from pathlib import Path

PROTOCOL = "PHIFIELD_DISCOVERY_D1_MISSION_V1"
MAX_BYTES = 128 * 1024
ALLOWED_SCHEMA_KEYS = {
    "type", "additionalProperties", "required", "properties", "items",
    "const", "enum", "pattern", "minLength", "maxLength",
    "minItems", "maxItems", "minimum", "maximum",
}
SCHEMA_METADATA_KEYS = {"$schema", "$id", "title"}


class MissionValidationError(ValueError):
    pass


def _fail(message):
    raise MissionValidationError(message)


def load_schema():
    resource = files("phifieldlab").joinpath("schemas", "d1.schema.json")
    schema = json.loads(resource.read_text(encoding="utf-8"))
    _validate_schema_structure(schema)
    return schema


def _validate_schema_structure(schema):
    if type(schema) is not dict:
        _fail("schema must be an object")
    unknown = set(schema) - ALLOWED_SCHEMA_KEYS - SCHEMA_METADATA_KEYS
    if unknown:
        _fail("unsupported schema keywords: " + ", ".join(sorted(unknown)))
    if schema.get("type") not in ("object", "array", "string", "integer", None):
        _fail("unsupported schema type")
    if schema.get("type") == "object":
        if schema.get("additionalProperties") is not False:
            _fail("all objects must deny additional properties")
        props = schema.get("properties")
        if type(props) is not dict:
            _fail("schema properties missing")
        required = schema.get("required")
        if type(required) is not list or set(required) != set(props) or len(required) != len(props):
            _fail("all declared properties must be required")
        for sub in props.values():
            _validate_schema_structure(sub)
    if schema.get("type") == "array":
        _validate_schema_structure(schema["items"])


def _check(value, spec, path):
    if "const" in spec and (type(value) is not type(spec["const"]) or value != spec["const"]):
        _fail(path + ": fixed value mismatch")
    if "enum" in spec and value not in spec["enum"]:
        _fail(path + ": value not in allowed set")
    kind = spec.get("type")
    if kind == "object":
        if type(value) is not dict:
            _fail(path + ": expected object")
        keys = set(spec["properties"])
        if set(value) != keys:
            _fail(path + ": missing or unexpected properties: " +
                  ", ".join(sorted(set(value) ^ keys)))
        for key, child_spec in spec["properties"].items():
            _check(value[key], child_spec, path + "/" + key)
    elif kind == "array":
        if type(value) is not list:
            _fail(path + ": expected list")
        if len(value) < spec.get("minItems", 0) or len(value) > spec.get("maxItems", 10000):
            _fail(path + ": array length outside bounds")
        for i, item in enumerate(value):
            _check(item, spec["items"], path + "/" + str(i))
    elif kind == "string":
        if type(value) is not str:
            _fail(path + ": expected string")
        if len(value) < spec.get("minLength", 0) or len(value) > spec.get("maxLength", 100000):
            _fail(path + ": text length outside bounds")
        if "pattern" in spec and re.fullmatch(spec["pattern"], value, flags=re.ASCII) is None:
            _fail(path + ": identifier format mismatch")
    elif kind == "integer":
        if type(value) is not int:
            _fail(path + ": expected integer")
        if value < spec.get("minimum", -math.inf) or value > spec.get("maximum", math.inf):
            _fail(path + ": number outside bounds")


def validate_mission(document):
    """Return a small, non-authorizing summary or raise MissionValidationError."""
    _check(document, load_schema(), "mission")
    candidate_ids = [c["id"] for c in document["candidates"]]
    if len(set(candidate_ids)) != len(candidate_ids):
        _fail("mission/candidates: duplicate hypothesis identifiers")
    expected_ids = ["H" + str(i) for i in range(1, len(candidate_ids) + 1)]
    if candidate_ids != expected_ids:
        _fail("mission/candidates: hypotheses must be consecutively numbered")
    if document["evaluation"]["success_criterion"].strip().casefold() == document["evaluation"]["failure_criterion"].strip().casefold():
        _fail("mission/evaluation: success and failure criteria cannot be identical")
    for i, candidate in enumerate(document["candidates"]):
        if candidate["prediction"].strip().casefold() == candidate["falsifier"].strip().casefold():
            _fail(f"mission/candidates/{i}: prediction and falsifier cannot be identical")
    return {
        "ok": True, "protocol": PROTOCOL, "mission_id": document["mission_id"],
        "domain": document["domain"], "status": "PROPOSAL_ONLY",
        "candidates": len(candidate_ids), "origin": "PROPOSED", "authority": "NONE",
        "attested": False, "execution_authorized": False,
        "review": "REQUIRED_BEFORE_ANY_EXECUTION"
    }


def _no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("duplicate JSON property: " + key)
        result[key] = value
    return result


def _no_nonfinite(constant):
    _fail("nonfinite numeric value: " + constant)


def load_mission(path: Path):
    raw = Path(path).read_bytes()
    if len(raw) > MAX_BYTES:
        _fail("mission exceeds 128 KiB file limit")
    try:
        document = json.loads(raw, object_pairs_hook=_no_duplicate_keys,
                              parse_constant=_no_nonfinite)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail("invalid JSON: " + str(exc))
    result = validate_mission(document)
    result["sha256"] = hashlib.sha256(raw).hexdigest()
    result["file_size_bytes"] = len(raw)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a D1 research proposal without executing it")
    parser.add_argument("action", choices=["validate"])
    parser.add_argument("--file", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = load_mission(args.file)
    except (MissionValidationError, OSError) as exc:
        parser.exit(2, "D1 proposal rejected: " + str(exc) + "\n")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
