"""D3 opt-in Linux-container cleanroom for the fixed D2 synthetic queue worker.

Do not pass user code, host paths, Docker socket, network or volumes into the
container. Docker isolation is a kernel boundary, not a VM or safe adversarial
multi-tenant sandbox. The operator must separately review/build the image.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
from importlib.resources import files
from pathlib import Path

from .discovery_d2 import (
    _admit, _canonical, _check_result, _ensure_local_output,
    _policy as d2_policy, _sha, MAX_RECEIPT_BYTES
)

PROTOCOL = "PHIFIELD_D3_CLEANROOM_RECEIPT_V1"
CONTRACT = "PHIFIELD_D3_CLEANROOM_V1"
POLICY_RESOURCE = "d3_policy.json"
IMAGE_ID_PATTERN = re.compile(r"sha256:[a-f0-9]{64}\Z")
ENTRYPOINT = ["python", "-I", "-m", "phifieldlab.d2_network_worker"]
COMMAND_TIMEOUT = 10


class CleanroomRefusal(ValueError):
    pass


def refuse(message):
    raise CleanroomRefusal(message)


def repo_root():
    return Path(__file__).resolve().parents[2]


def policy():
    raw = files("phifieldlab").joinpath("schemas", POLICY_RESOURCE).read_bytes()
    if len(raw) > 16384:
        refuse("D3 policy too large")
    data = json.loads(raw)
    expected = {
        "protocol": CONTRACT, "mission_id": "network-switch-latency",
        "adapter": "SYNTHETIC_QUEUE_V1",
        "image_contract": CONTRACT, "image_adapter_label": "SYNTHETIC_QUEUE_V1",
        "origin": "SIMULATED", "authority": "NONE", "attested": False,
        "isolated_backend": "DOCKER_LINUX_CONTAINER",
        "controls": {
            "network": "none", "read_only_rootfs": True,
            "rootless_container_user": "65534:65534",
            "drop_capabilities": "ALL", "no_new_privileges": True,
            "pids_limit": 32, "memory": "128m", "memory_swap": "128m",
            "cpus": "1.0", "ipc": "none",
            "tmpfs": "/tmp:rw,nosuid,nodev,noexec,size=8m"
        },
        "max_wall_seconds": 35,
        "permission": {
            "local_approval_required": True, "arbitrary_commands": False,
            "host_mounts": False, "network_access": False,
            "publication": False, "external_spend": False
        },
        "limits": "Linux container isolation reduces risk but is not a VM, hardware boundary, or safe multi-tenant untrusted-code sandbox; a compromised daemon or kernel bypasses restrictions."
    }
    if type(data) is not dict or data != expected:
        refuse("D3 policy modified: fail closed")
    return data, _sha(raw)


def _checked_image(image_id):
    if type(image_id) is not str or IMAGE_ID_PATTERN.fullmatch(image_id) is None:
        refuse("image must be the exact sha256:... image ID, never a mutable tag")
    return image_id


def _docker_binary():
    # A remote Docker daemon may see credentials or access a nonlocal host.
    if os.environ.get("DOCKER_HOST"):
        refuse("explicit DOCKER_HOST is denied")
    docker = shutil.which("docker")
    if not docker:
        refuse("Docker executable unavailable; no fallback to D2")
    return docker


def _json_command(argv, *, timeout=COMMAND_TIMEOUT):
    try:
        result = subprocess.run(argv, capture_output=True, text=True,
                                timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        refuse("Docker command unavailable or timed out: " + type(exc).__name__)
    if result.returncode != 0:
        refuse("Docker preflight failed (exit " + str(result.returncode) + ")")
    if len(result.stdout.encode("utf-8")) > 65536:
        refuse("oversized Docker inspection response")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        refuse("Docker inspection response is not JSON")


def preflight(image_id):
    image_id = _checked_image(image_id)
    docker = _docker_binary()
    context = _json_command([docker, "context", "inspect", "--format", "{{json .}}"])
    host = context.get("Endpoints", {}).get("docker", {}).get("Host", "")
    if not isinstance(host, str) or not host.startswith(("unix://", "npipe://")):
        refuse("only a local Unix socket or local Windows Docker pipe is allowed")
    info = _json_command([docker, "info", "--format", "{{json .}}"])
    if (info.get("OSType") != "linux" or info.get("MemoryLimit") is not True or
        info.get("PidsLimit") is not True or info.get("CpuCfsQuota") is not True):
        refuse("Linux engine with working memory, pids and CPU quotas required")
    if not any("seccomp" in str(x).lower() for x in info.get("SecurityOptions", [])):
        refuse("seccomp must be enabled on the container engine")
    image = _json_command([docker, "image", "inspect", "--format", "{{json .}}", image_id])
    cfg = image.get("Config")
    if type(cfg) is not dict or image.get("Id") != image_id:
        refuse("image ID does not match immutable operator-selected digest")
    labels = cfg.get("Labels") or {}
    if (labels.get("org.phifieldlab.contract") != CONTRACT or
        labels.get("org.phifieldlab.adapter") != "SYNTHETIC_QUEUE_V1" or
        cfg.get("Entrypoint") != ENTRYPOINT or cfg.get("User") != "65534:65534" or
        cfg.get("WorkingDir") != "/tmp"):
        refuse("image metadata or fixed entrypoint is not the reviewed configuration")
    return {
        "backend": "DOCKER_LINUX_CONTAINER", "image_id": image_id,
        "local_docker_endpoint": True, "linux_engine": True,
        "seccomp_enabled": True, "quotas_supported": True,
        "warning": "Image provenance and host hardening require independent operator review. No VM-level boundary."
    }


def plan(mission_path):
    mission, _, _ = _admit(mission_path)
    d3, sha = policy()
    return {
        "protocol": PROTOCOL, "mission_id": mission["mission_id"],
        "mission_sha256": mission["sha256"], "policy_sha256": sha,
        "adapter": d3["adapter"],
        "status": "AWAITING_LOCAL_OPERATOR_APPROVAL_AND_CONTAINER_PREFLIGHT",
        "execution_authorized": False, "runtime_checked": False,
        "required_image_form": "sha256:<64 hex characters>",
        "origin": "SIMULATED", "authority": "NONE", "attested": False
    }


def command(image_id, *, name):
    _checked_image(image_id)
    if re.fullmatch(r"phifield-d3-[0-9a-f]{16}", name) is None:
        refuse("invalid generated container identifier")
    p, _ = policy()
    c = p["controls"]
    return [
        "run", "--rm", "--pull", "never",
        "--name", name, "--network", c["network"],
        "--ipc", c["ipc"], "--read-only",
        "--cap-drop", c["drop_capabilities"],
        "--security-opt", "no-new-privileges:true",
        "--pids-limit", str(c["pids_limit"]),
        "--memory", c["memory"], "--memory-swap", c["memory_swap"],
        "--cpus", c["cpus"], "--user", c["rootless_container_user"],
        "--tmpfs", c["tmpfs"], image_id
    ]


def _run_container(image_id):
    checked = preflight(image_id)
    docker = _docker_binary()
    name = "phifield-d3-" + secrets.token_hex(8)
    args = [docker] + command(image_id, name=name)
    timeout = policy()[0]["max_wall_seconds"]
    try:
        proc = subprocess.run(args, capture_output=True, text=True,
                              timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        # Docker CLI timeout does not necessarily stop its daemon-side container.
        # Explicitly force removal; if cleanup cannot be confirmed, fail closed.
        try:
            cleanup = subprocess.run([docker, "rm", "-f", name], capture_output=True,
                                     text=True, timeout=COMMAND_TIMEOUT, check=False)
        except (OSError, subprocess.TimeoutExpired):
            refuse("worker failed/timed out; container cleanup could not be confirmed")
        if cleanup.returncode != 0 and "No such container" not in cleanup.stderr:
            refuse("worker failed/timed out; container removal failed")
        refuse("worker failed or exceeded wall deadline: " + type(exc).__name__)
    if proc.returncode != 0:
        refuse("isolated worker failed with exit code " + str(proc.returncode))
    if len(proc.stdout.encode("utf-8")) > MAX_RECEIPT_BYTES:
        refuse("isolated worker stdout exceeded size limit")
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        refuse("isolated worker response is not JSON")
    _check_result(result, d2_policy()[0])
    return result, checked


def _files_digest():
    root = repo_root()
    paths = [
        "cleanroom/Dockerfile", ".dockerignore",
        "src/phifieldlab/discovery_d3.py",
        "src/phifieldlab/d2_network_sim.py",
        "src/phifieldlab/d2_network_worker.py"
    ]
    return {p: _sha((root / p).read_bytes()) for p in paths}


def _receipt(mission, policy_digest, image_id):
    result, gate = _run_container(image_id)
    return {
        "protocol": PROTOCOL, "mission_id": mission["mission_id"],
        "mission_sha256": mission["sha256"], "policy_sha256": policy_digest,
        "image_id": image_id, "backend": "DOCKER_LINUX_CONTAINER",
        "origin": "SIMULATED", "authority": "NONE", "attested": False,
        "approval": "LOCAL_FLAG_PLUS_PINNED_MISSION_AND_IMAGE_NOT_AUTHENTICATED",
        "gates": gate, "controls": policy()[0]["controls"],
        "code_sha256": _files_digest(), "result": result,
        "scientific_promotion": "BLOCKED",
        "claims": "Toy comparison only. No evidence of real-world network benefit or host-independent secure isolation."
    }


def _authorization(mission, approve_local, expect_sha256, image_id):
    if approve_local is not True or expect_sha256 != mission["sha256"]:
        raise PermissionError("D3 requires explicit --approve-local and exact mission SHA-256")
    return _checked_image(image_id)


def run(mission_path, out, *, approve_local=False, expect_sha256=None, image_id=None):
    mission, _, digest = _admit(mission_path)
    policy()
    _authorization(mission, approve_local, expect_sha256, image_id)
    target = _ensure_local_output(out)
    if target.exists():
        raise FileExistsError("receipt already exists")
    receipt = _receipt(mission, policy()[1], image_id)
    payload = _canonical(receipt)
    if len(payload) > MAX_RECEIPT_BYTES:
        refuse("receipt too large")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(payload)
    return {"ok": True, "file": str(target), "sha256": _sha(payload),
            "status": "SIMULATED_UNATTESTED_REPLAY_REQUIRED"}


def verify(mission_path, file_path, *, approve_local=False, expect_sha256=None, image_id=None):
    mission, _, digest = _admit(mission_path)
    policy()
    _authorization(mission, approve_local, expect_sha256, image_id)
    target = _ensure_local_output(file_path)
    raw = target.read_bytes()
    if len(raw) > MAX_RECEIPT_BYTES:
        refuse("receipt too large")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        refuse("receipt invalid JSON")
    if _canonical(payload) != raw:
        refuse("receipt canonical encoding mismatch")
    if payload.get("image_id") != image_id:
        refuse("receipt not pinned to specified image")
    replay = _receipt(mission, policy()[1], image_id)
    if _canonical(replay) != raw:
        refuse("fresh isolated replay differs from saved receipt")
    return {
        "ok": True, "protocol": PROTOCOL, "sha256": _sha(raw),
        "attested": False, "origin": "SIMULATED", "authority": "NONE",
        "replay": "SAME_IMAGE_SAME_ENGINE_NOT_INDEPENDENT_ATTESTATION"
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="D3 opt-in Docker cleanroom pilot")
    subs = parser.add_subparsers(dest="action", required=True)
    p = subs.add_parser("plan")
    f = subs.add_parser("preflight")
    r = subs.add_parser("run")
    v = subs.add_parser("verify")
    for a in (p, r, v):
        a.add_argument("--mission", type=Path, required=True)
    for a in (f, r, v):
        a.add_argument("--image", required=True)
    for a in (r, v):
        a.add_argument("--approve-local", action="store_true")
        a.add_argument("--expect-sha256", required=True)
    r.add_argument("--out", type=Path, required=True)
    v.add_argument("--file", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "plan":
            result = plan(args.mission)
        elif args.action == "preflight":
            result = preflight(args.image)
        elif args.action == "run":
            result = run(args.mission, args.out, approve_local=args.approve_local,
                         expect_sha256=args.expect_sha256, image_id=args.image)
        else:
            result = verify(args.mission, args.file, approve_local=args.approve_local,
                            expect_sha256=args.expect_sha256, image_id=args.image)
    except (CleanroomRefusal, ValueError, PermissionError, OSError, TypeError) as exc:
        parser.exit(2, "D3 cleanroom refused: " + str(exc) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
