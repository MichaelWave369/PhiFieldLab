"""D2 orchestrator: one allowlisted toy adapter, explicit approval, receipt replay.

No arbitrary user-supplied commands, imported D1 draft execution, cloud calls,
or production device access. Child process isolation is NOT an OS sandbox.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from importlib.resources import files
from pathlib import Path

from .discovery_d1 import load_mission

PROTOCOL = "PHIFIELD_D2_EXECUTION_RECEIPT_V1"
POLICY_ID = "PHIFIELD_D2_RUN_POLICY_V1"
ADAPTER = "SYNTHETIC_QUEUE_V1"
MAX_RECEIPT_BYTES = 128 * 1024
APPROVAL_LABEL = "OPERATOR_FLAG_AND_MISSION_DIGEST_NOT_IDENTITY_ATTESTATION"


class D2Refusal(ValueError):
    pass


def _deny(message):
    raise D2Refusal(message)


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _canonical(obj):
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def root_path():
    # This first research slice is intentionally run from a source checkout:
    # the reviewed reference mission is not part of the installed wheel.
    return Path(__file__).resolve().parents[2]


def local_artifacts_dir():
    return (root_path() / "artifacts" / "local").resolve()


def _ensure_local_output(path):
    target = Path(path).resolve()
    destination = local_artifacts_dir()
    if destination not in target.parents or target.suffix != ".json":
        _deny("output must be a new JSON file under artifacts/local/")
    return target


def _policy():
    resource = files("phifieldlab").joinpath("schemas", "d2_policy.json")
    raw = resource.read_bytes()
    if len(raw) > 16 * 1024:
        _deny("policy size exceeds limit")
    data = json.loads(raw)
    expected = {
        "protocol": POLICY_ID, "adapter": ADAPTER,
        "mission_id": "network-switch-latency",
        "trusted_d1_path": "missions/d1-examples/network-switch-latency.json",
        "mode": "LOCAL_APPROVAL_REQUIRED",
        "origin": "SIMULATED", "authority": "NONE", "attested": False,
        "seeds": [101, 103, 107, 109, 113],
        "ticks_per_seed": 1200, "queue_capacity_packets": 64,
        "max_wall_seconds": 30,
        "permissions": {
            "internet": False, "production_devices": False, "arbitrary_code": False,
            "repository_writes": False, "publication": False, "external_spend": False
        },
        "disclaimer": "Toy simulation only. A Python child process, timeout, fixed adapter and temporary working directory are NOT an OS-enforced network or filesystem sandbox."
    }
    if type(data) is not dict or data != expected:
        _deny("unrecognized D2 policy: deny all")
    return data, _sha(raw)


def _admit(mission_path):
    policy, policy_digest = _policy()
    info = load_mission(Path(mission_path))
    source = (root_path() / policy["trusted_d1_path"]).resolve()
    try:
        reference = source.read_bytes()
        submitted = Path(mission_path).read_bytes()
    except OSError:
        _deny("approved example mission file unavailable")
    if submitted != reference or info["mission_id"] != policy["mission_id"] or info["domain"] != "networking":
        _deny("only the exact source-controlled network-latency D1 proposal is admissible")
    return info, policy, policy_digest


def plan(mission_path):
    info, policy, policy_sha = _admit(mission_path)
    return {
        "protocol": PROTOCOL, "adapter": ADAPTER,
        "mission_id": info["mission_id"], "mission_sha256": info["sha256"],
        "policy_sha256": policy_sha, "status": "AWAITING_EXPLICIT_LOCAL_APPROVAL",
        "execution_authorized": False,
        "expected_trials": len(policy["seeds"]), "max_wall_seconds": policy["max_wall_seconds"],
        "origin": "SIMULATED", "authority": "NONE", "attested": False,
        "network_or_production_access": False,
        "note": "No experiment executed by plan. D1 denies execution; D2 only admits a reviewed fixed toy adapter with fresh operator consent."
    }


def _check_result(data, policy):
    if type(data) is not dict:
        _deny("worker response must be an object")
    if set(data) != {"protocol", "origin", "authority", "attested", "workload", "rows", "review"}:
        _deny("worker response schema mismatch")
    if (data["protocol"] != "PHIFIELD_D2_SYNTHETIC_QUEUE_V1" or
        data["origin"] != "SIMULATED" or data["authority"] != "NONE" or
        data["attested"] is not False):
        _deny("worker provenance mismatch")
    workload = data["workload"]
    if (type(workload) is not dict or workload.get("ticks_per_seed") != policy["ticks_per_seed"] or
        workload.get("queue_capacity_packets") != policy["queue_capacity_packets"] or
        workload.get("seeds") != policy["seeds"] or workload.get("policies") != ["fifo", "fair"]):
        _deny("worker workload does not match frozen policy")
    rows = data["rows"]
    if type(rows) is not list or len(rows) != len(policy["seeds"]):
        _deny("worker row count mismatch")
    for seed, row in zip(policy["seeds"], rows):
        if type(row) is not dict or set(row) != {
            "seed", "trace_sha256", "baseline", "candidate", "sham_equals_baseline",
            "sensitive_p95_reduction_percent", "loss_not_worse"
        }:
            _deny("worker row schema mismatch")
        if row["seed"] != seed or row["sham_equals_baseline"] is not True:
            _deny("worker matched-control failed")
        for kind, name in (("baseline", "fifo"), ("candidate", "fair")):
            score = row[kind]
            if type(score) is not dict or score.get("policy") != name:
                _deny("worker output policy mismatch")
            if (type(score.get("offered_packets")) is not int or
                type(score.get("dropped_packets")) is not int or
                type(score.get("delivered_packets")) is not int or
                score["offered_packets"] != score["dropped_packets"] + score["delivered_packets"]):
                _deny("worker packet conservation failed")
        if row["candidate"]["offered_packets"] != row["baseline"]["offered_packets"]:
            _deny("worker offered load mismatch")
        if type(row["sensitive_p95_reduction_percent"]) not in (float, int):
            _deny("worker missing p95 reduction")
        expected_loss = row["candidate"]["dropped_packets"] <= row["baseline"]["dropped_packets"]
        if row["loss_not_worse"] is not expected_loss:
            _deny("worker loss assessment mismatch")
    review = data["review"]
    if type(review) is not dict or review.get("scientific_promotion") != "BLOCKED":
        _deny("unsupported scientific promotion")


def _child_batch(timeout):
    # -I discards user PYTHONPATH and disables user site packages; module must
    # be installed. This does not disable sockets or sandbox the OS.
    allowed_environment = ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "HOME", "USERPROFILE")
    env = {key: val for key, val in os.environ.items() if key in allowed_environment}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONHASHSEED"] = "0"
    with tempfile.TemporaryDirectory(prefix="phifield-d2-") as cwd:
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-m", "phifieldlab.d2_network_worker"],
                cwd=cwd, env=env, capture_output=True, text=True,
                timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired:
            _deny("bounded worker timed out")
    if proc.returncode != 0:
        _deny("bounded worker failed with exit code " + str(proc.returncode))
    if len(proc.stdout.encode("utf-8")) > MAX_RECEIPT_BYTES:
        _deny("worker output exceeded 128 KiB")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        _deny("worker did not produce valid JSON")


def _code_hashes():
    folder = Path(__file__).resolve().parent
    return {name: _sha((folder / name).read_bytes()) for name in
            ("discovery_d2.py", "d2_network_worker.py", "d2_network_sim.py")}


def _produce(mission_info, policy, policy_sha):
    results = _child_batch(policy["max_wall_seconds"])
    _check_result(results, policy)
    return {
        "protocol": PROTOCOL, "mission_id": mission_info["mission_id"],
        "mission_sha256": mission_info["sha256"],
        "policy_sha256": policy_sha, "adapter": ADAPTER,
        "origin": "SIMULATED", "authority": "NONE", "attested": False,
        "approval_record": APPROVAL_LABEL,
        "execution_scope": "FIXED_LOCAL_SYNTHETIC_WORKER_ONLY",
        "runtime_gate": {
            "child_python_isolated_mode": True,
            "fresh_temporary_cwd": True,
            "wall_timeout_seconds": policy["max_wall_seconds"],
            "os_network_and_filesystem_sandbox": False,
            "allowed_external_spend_usd": 0
        },
        "code_sha256": _code_hashes(),
        "result": results,
        "claims": "Unattested model output, not real switch benchmarking or verified networking performance."
    }


def run(mission_path, out_path, *, approve_local=False, expect_sha256=None):
    info, policy, policy_sha = _admit(mission_path)
    if approve_local is not True or expect_sha256 != info["sha256"]:
        raise PermissionError("run requires --approve-local and exact --expect-sha256 from plan")
    target = _ensure_local_output(out_path)
    if target.exists():
        raise FileExistsError("receipt already exists")
    receipt = _produce(info, policy, policy_sha)
    raw = _canonical(receipt)
    if len(raw) > MAX_RECEIPT_BYTES:
        _deny("receipt exceeds bounded size")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as fd:
        fd.write(raw)
    return {"ok": True, "file": str(target), "sha256": _sha(raw),
            "status": "SIMULATED_UNATTESTED_REPLAY_REQUIRED"}


def verify(mission_path, receipt_path, *, approve_local=False, expect_sha256=None):
    info, policy, policy_sha = _admit(mission_path)
    if approve_local is not True or expect_sha256 != info["sha256"]:
        raise PermissionError("verification replay requires fresh --approve-local and matching mission digest")
    target = _ensure_local_output(receipt_path)
    raw = target.read_bytes()
    if len(raw) > MAX_RECEIPT_BYTES:
        _deny("receipt exceeds 128 KiB")
    try:
        saved = json.loads(raw)
    except json.JSONDecodeError:
        _deny("invalid receipt JSON")
    if _canonical(saved) != raw:
        _deny("receipt byte format or content modified")
    replay = _produce(info, policy, policy_sha)
    if _canonical(replay) != raw:
        _deny("receipt diverges from fresh worker replay")
    return {"ok": True, "sha256": _sha(raw), "protocol": PROTOCOL,
            "attested": False, "origin": "SIMULATED", "authority": "NONE",
            "replay": "SAME_CODE_NEW_CHILD_PROCESS_NOT_INDEPENDENT_ATTESTATION"}


def main(argv=None):
    parser = argparse.ArgumentParser(description="D2 explicitly approved local synthetic queue research")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("plan")
    r = sub.add_parser("run")
    v = sub.add_parser("verify")
    for cmd in (p, r, v):
        cmd.add_argument("--mission", type=Path, required=True)
    for cmd in (r, v):
        cmd.add_argument("--approve-local", action="store_true")
        cmd.add_argument("--expect-sha256", required=True)
    r.add_argument("--out", type=Path, required=True)
    v.add_argument("--file", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "plan":
            result = plan(args.mission)
        elif args.action == "run":
            result = run(args.mission, args.out, approve_local=args.approve_local,
                         expect_sha256=args.expect_sha256)
        else:
            result = verify(args.mission, args.file, approve_local=args.approve_local,
                            expect_sha256=args.expect_sha256)
    except (ValueError, PermissionError, OSError, TypeError) as exc:
        parser.exit(2, "D2 gate refused: " + str(exc) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
