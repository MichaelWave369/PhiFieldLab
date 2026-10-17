"""D0: bounded, read-only discovery audit of the existing frozen QP5 simulation.

No LLM calls, networking, publishing, external writes, strategy selection,
or autonomous experiment execution. A CLI flag records local operator consent;
it is not a cryptographic signature or independent attestation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

PROTOCOL = "PHIFIELD_DISCOVERY_D0_V1"
ADAPTER = "QP5_FROZEN_READ_ONLY"
RULES = {
    "C1_HIGH_D_REDUCES_ENTROPY": "D12_LT_D0",
    "C2_D_INVARIANT_NULL": "D12_EQ_D0",
}
MAX_JSON = 128 * 1024
TOLERANCE = 1e-7


def canonical_bytes(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _require(test: bool, error: str):
    if not test:
        raise ValueError(error)


def _read_json(path: Path):
    raw = Path(path).read_bytes()
    _require(len(raw) <= MAX_JSON, "JSON exceeds 128 KiB limit")
    return json.loads(raw), raw


def load_mission(path: Path):
    """Fail closed on unknown adapters, permissions, budgets or candidate tests."""
    data, raw = _read_json(path)
    _require(type(data) is dict, "mission must be an object")
    _require(set(data) == {
        "protocol", "mission_id", "adapter", "reference_protocol",
        "question", "origin", "authority", "attested", "approval",
        "limits", "candidates", "caveats"
    }, "mission schema mismatch")
    _require(data["protocol"] == PROTOCOL, "unknown discovery protocol")
    _require(data["mission_id"] == "QP5-D0-MATCHED-CONTROLS", "unsupported mission")
    _require(data["adapter"] == ADAPTER, "unsupported adapter")
    _require(data["reference_protocol"] == "PHIFIELD_QP5_FINITE_SCHMIDT_AUDIT_V1",
             "frozen QP5 protocol mismatch")
    _require(data["origin"] == "SIMULATED" and data["authority"] == "NONE"
             and data["attested"] is False, "untrusted provenance claim")
    _require(type(data["question"]) is str and len(data["question"]) >= 30,
             "research question missing")
    _require(type(data["approval"]) is dict and data["approval"] == {
        "operator_required": True, "network": False,
        "external_writes": False, "publication": False, "code_changes": False
    }, "unsupported action permission")
    _require(type(data["limits"]) is dict and data["limits"] == {
        "maximum_rows": 48, "maximum_candidates": 2
    }, "unsupported research budget")
    _require(type(data["candidates"]) is list
             and len(data["candidates"]) == len(RULES), "candidate count mismatch")
    seen = set()
    for candidate in data["candidates"]:
        _require(type(candidate) is dict
                 and set(candidate) == {"id", "statement", "test", "falsifier"},
                 "candidate schema mismatch")
        cid = candidate["id"]
        _require(type(cid) is str and cid in RULES and cid not in seen,
                 "unknown or duplicate candidate")
        seen.add(cid)
        _require(candidate["test"] == RULES[cid], "candidate test changed")
        for field in ("statement", "falsifier"):
            _require(type(candidate[field]) is str and len(candidate[field]) >= 15,
                     "missing candidate explanation")
    _require(type(data["caveats"]) is list and len(data["caveats"]) >= 3
             and all(type(c) is str and len(c) >= 25 for c in data["caveats"]),
             "claim-limit caveats missing")
    return data, hashlib.sha256(raw).hexdigest()


def plan(mission_path: Path):
    mission, digest = load_mission(mission_path)
    return {
        "protocol": PROTOCOL, "mission": mission["mission_id"],
        "mission_sha256": digest, "status": "AWAITING_EXPLICIT_LOCAL_APPROVAL",
        "adapter": ADAPTER, "candidate_tests": [c["test"] for c in mission["candidates"]],
        "maximum_rows": 48,
        "actions": {"network": False, "external_writes": False,
                    "publication": False, "code_changes": False},
        "origin": "SIMULATED", "authority": "NONE", "attested": False
    }


def build_report(mission: dict, digest: str) -> dict:
    """Recompute all QP5 cases and cross-check energies via the QP4 solver."""
    from . import qp5
    from .qp4 import spectrum

    data = qp5.reference()
    _require(data["protocol"] == mission["reference_protocol"]
             and data["origin"] == "SIMULATED" and data["authority"] == "NONE"
             and data["attested"] is False, "QP5 provenance mismatch")
    rows = data["rows"]
    _require(type(rows) is list and len(rows) == 48, "QP5 row count mismatch")
    expected = {
        (n, d, bound, cut)
        for n in (4, 6, 8)
        for d in (0, 1, 4, 12)
        for bound in ("open", "periodic")
        for cut in (1, n // 2)
    }
    keyed = {}
    for row in rows:
        key = (row["n"], row["d_over_j"], row["boundary"], row["cut_after_site"])
        _require(key in expected and key not in keyed, "missing/duplicate QP5 geometry")
        entropy = row["entropy_von_neumann_nats"]
        energy = row["ground_energy_m0"]
        _require(type(entropy) in (float, int) and math.isfinite(entropy)
                 and entropy >= 0 and type(energy) in (float, int)
                 and math.isfinite(energy), "invalid QP5 observables")
        keyed[key] = row
    _require(set(keyed) == expected, "incomplete QP5 geometry grid")

    errors = []
    for n in (4, 6, 8):
        for d in (0, 1, 4, 12):
            for bound in ("open", "periodic"):
                energy = spectrum(n, d, bound)["lowest_m0_energy"]
                for cut in (1, n // 2):
                    diff = abs(keyed[(n, d, bound, cut)]["ground_energy_m0"] - energy)
                    _require(math.isfinite(diff) and diff <= TOLERANCE,
                             "QP4 energy cross-check failed")
                    errors.append(diff)

    comparisons = []
    for n in (4, 6, 8):
        for bound in ("open", "periodic"):
            for cut in (1, n // 2):
                low = keyed[(n, 0, bound, cut)]["entropy_von_neumann_nats"]
                high = keyed[(n, 12, bound, cut)]["entropy_von_neumann_nats"]
                comparisons.append({"n": n, "boundary": bound, "cut": cut,
                                    "d0_entropy": low, "d12_entropy": high,
                                    "difference_d12_minus_d0": round(high - low, 9)})
    results = []
    for candidate in mission["candidates"]:
        test = candidate["test"]
        failures = []
        for case in comparisons:
            delta = case["difference_d12_minus_d0"]
            passed = delta < 0 if test == "D12_LT_D0" else abs(delta) <= TOLERANCE
            if not passed:
                failures.append({"n": case["n"], "boundary": case["boundary"],
                                 "cut": case["cut"], "difference": delta})
        results.append({
            "candidate_id": candidate["id"], "test": test,
            "tested_comparisons": len(comparisons),
            "passing_comparisons": len(comparisons) - len(failures),
            "verdict": "SUPPORTED_IN_SIMULATION" if not failures else "FALSIFIED_IN_SIMULATION",
            "counterexamples": failures
        })

    return {
        "protocol": PROTOCOL,
        "mission_id": mission["mission_id"], "mission_sha256": digest,
        "source_protocol": qp5.PROTOCOL, "adapter": ADAPTER,
        "origin": "SIMULATED", "authority": "NONE", "attested": False,
        "evidence": {
            "rows_audited": len(rows), "matched_comparisons": len(comparisons),
            "qp4_independent_solver_energy_checks": len(errors),
            "maximum_energy_difference": max(errors),
            "reference_sha256": hashlib.sha256(qp5.canonical_bytes(data)).hexdigest()
        },
        "candidates": results,
        "adversarial_review": {
            "null_candidate_falsified": next(r for r in results
                                             if r["candidate_id"] == "C2_D_INVARIANT_NULL"
                                            )["verdict"] == "FALSIFIED_IN_SIMULATION",
            "matched_controls": True,
            "cross_solver_energy_checks": True,
            "limitations": mission["caveats"],
            "reviewer": "DETERMINISTIC_RULES_NOT_INDEPENDENT_SCIENTIFIC_REVIEW"
        },
        "governance": {
            "approval": "LOCAL_CLI_FLAG_ONLY_NOT_AUTHENTICATED",
            "network": False, "external_writes": False, "publication": False,
            "scientific_promotion": "BLOCKED"
        },
        "interpretation": "Finite simulated-model comparisons only; no experimental result, new physical law, or autonomous AI discovery."
    }


def run_mission(mission_path: Path, out: Path, *, approve_local: bool = False):
    if not approve_local:
        raise PermissionError("local run requires explicit --approve-local")
    mission, digest = load_mission(mission_path)
    report = build_report(mission, digest)
    raw = canonical_bytes(report)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("xb") as fp:
        fp.write(raw)
    return {"file": str(out), "sha256": hashlib.sha256(raw).hexdigest(),
            "status": "SIMULATED_REPLAYABLE_NOT_ATTESTED"}


def _compare(expected, actual, path="report"):
    _require(type(expected) is type(actual), "type mismatch at " + path)
    if isinstance(expected, dict):
        _require(set(expected) == set(actual), "schema mismatch at " + path)
        for k, value in expected.items():
            _compare(value, actual[k], path + "/" + str(k))
    elif isinstance(expected, list):
        _require(len(expected) == len(actual), "list mismatch at " + path)
        for index, (e, a) in enumerate(zip(expected, actual)):
            _compare(e, a, path + "/" + str(index))
    elif isinstance(expected, float):
        _require(math.isfinite(actual) and abs(expected - actual) <= TOLERANCE,
                 "numeric mismatch at " + path)
    else:
        _require(expected == actual, "value mismatch at " + path)


def verify_report(mission_path: Path, report_path: Path):
    mission, digest = load_mission(mission_path)
    observed, raw = _read_json(report_path)
    expected = build_report(mission, digest)
    _compare(expected, observed)
    return {"ok": True, "protocol": PROTOCOL, "origin": "SIMULATED",
            "authority": "NONE", "attested": False,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "scope": "SAME_IMPLEMENTATION_REPLAY_NOT_INDEPENDENT_ATTESTATION"}


def main(argv=None):
    parser = argparse.ArgumentParser(description="D0 bounded QP5 discovery protocol (offline)")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("plan", help="validate mission and inspect permissions (no calculations)")
    p.add_argument("--mission", type=Path, required=True)
    r = sub.add_parser("run", help="run explicitly approved local simulation audit")
    r.add_argument("--mission", type=Path, required=True)
    r.add_argument("--out", type=Path, required=True)
    r.add_argument("--approve-local", action="store_true")
    v = sub.add_parser("verify", help="recompute and compare a saved receipt")
    v.add_argument("--mission", type=Path, required=True)
    v.add_argument("--file", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "plan":
            result = plan(args.mission)
        elif args.action == "run":
            result = run_mission(args.mission, args.out, approve_local=args.approve_local)
        else:
            result = verify_report(args.mission, args.file)
    except (ValueError, PermissionError, FileExistsError, OSError) as exc:
        parser.exit(2, "discovery gate refused: " + str(exc) + "\n")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
