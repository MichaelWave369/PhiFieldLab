# Discovery D3 · Research Cleanroom pilot

**Status:** opt-in Linux-container isolation for the **existing fixed synthetic queue simulator only**.  
**Protocol:** `PHIFIELD_D3_CLEANROOM_V1`  
**Receipt:** `PHIFIELD_D3_CLEANROOM_RECEIPT_V1`  
**Claims:** `SIMULATED / AUTHORITY NONE / UNATTESTED`.

D3 adds a separate Docker-container path, **not a silent upgrade to D2**. D0/QP5, D1 research designs and D2's existing process runner remain unchanged. It does not accept arbitrary experiments, scripts, user-authored commands, plugins or production-network access.

## What is actually isolated

An operator builds the image defined by `cleanroom/Dockerfile` from a reviewed, locally available Python base. The root `.dockerignore` sends only three reviewed Python files to the Docker build context. The entrypoint is fixed to `python -I -m phifieldlab.d2_network_worker`, and the image's configured user is 65534:65534.

Before execution, the host runner verifies:
- The operator provided an exact immutable **image ID** (`sha256:...`), not a mutable tag.
- Docker uses a **local** Unix socket or Windows named-pipe context, has a Linux backend, and reports support for seccomp, memory, CPU and process limits.
- Docker image metadata has the expected contract labels, nonroot user, working directory, and fixed entrypoint. **Labels are not cryptographic proof of image authenticity.**
- The mission is a byte-exact match for the source-controlled D1 network-latency toy and the frozen D3 policy has not changed.
- The operator passes **both** `--approve-local` and the exact mission digest from `plan`.

The launched container uses `--network none`, `--read-only`, `--cap-drop ALL`, `--security-opt no-new-privileges:true`, a nonroot UID/GID, `--pids-limit 32`, 128 MiB memory+swap, one CPU, `--ipc none`, a small `/tmp` tmpfs with `noexec,nosuid,nodev`, `--pull never`, no binds, no volumes, no devices, and no ports. An outer 35-second deadline requests forced container removal on timeout. The worker's results are checked by the pre-existing D2 result validator and saved as a create-only JSON receipt under ignored `artifacts/local/`.

These controls depend on Docker and the Linux kernel. They are a meaningful isolation improvement over D2's plain subprocess, **not a guarantee against kernel exploits, Docker-daemon compromise, resource side channels, malicious base images, or other attacks**. No untrusted code is permitted. Docker commands still require operator access to a highly privileged daemon; do not run this against a shared or untrusted Docker context.

## Windows / Docker Desktop (Linux containers)

Docker Desktop must be configured to use a **local Linux-container backend**. On Windows, WSL 2 / Docker Desktop supplies the container runtime; this design does not use Windows Sandbox or Hyper-V directly. Docker is optional and **is not installed or configured by this PR**. D3 rejects unsupported or unavailable runtimes and **never falls back to D2**.

From a source checkout, install this repository's Python package:

```powershell
python -m pip install -e .
python -m unittest discover -s tests -p test_discovery_d3.py -v
```

Inspect and choose a trustworthy Python 3.11 Alpine base image. Fetch it only with deliberate operator approval:

```powershell
docker pull python:3.11-alpine
```

Build with external network disabled and without pulling during the build:

```powershell
docker build --network none --pull=false -f cleanroom/Dockerfile -t phifieldlab-d3:local .
$image = docker image inspect --format '{{.Id}}' phifieldlab-d3:local
python -m phifieldlab.discovery_d3 preflight --image $image
```

**The build step itself is not hermetic**: the Python base may change between pulls. Record the upstream base-image digest and review source changes before accepting the final image ID. Use signed images/attestations in future releases if stronger supply-chain guarantees are needed.

Review the mission and approval plan:

```powershell
$mission = "missions/d1-examples/network-switch-latency.json"
$plan = python -m phifieldlab.discovery_d3 plan --mission $mission | ConvertFrom-Json
$plan
```

Run only after approval:

```powershell
python -m phifieldlab.discovery_d3 run --mission $mission --image $image --approve-local --expect-sha256 $plan.mission_sha256 --out artifacts/local/d3-network-001.json
```

Replay the same model in a **new container from the same pinned image**:

```powershell
python -m phifieldlab.discovery_d3 verify --mission $mission --image $image --approve-local --expect-sha256 $plan.mission_sha256 --file artifacts/local/d3-network-001.json
```

Never overwrite old receipts. Use a new filename for each run. The stored `code_sha256` and `image_id` establish consistent inputs under this checkout, **not operator identity, independent scientific validation or true image provenance**. Verification is the *same implementation* executed a second time in another container.

## Tests and refusal expectations

GitHub's main CI runs deterministic unit tests for denied permissions, image IDs, impossible image metadata, external/remote Docker contexts, missing seccomp, unsupported capabilities, unapproved missions, path escapes, and receipt tampering. The separate `D3 Cleanroom Isolation Smoke` workflow **actually builds a fixed image and launches Docker** on GitHub-hosted Linux, then replays its receipt. CI pulling a base is a setup action for the test job only, not an ability granted to the experiment container.

This smoke test validates that the prescribed image and invocation function on a Linux Docker runner. It **does not certify resistance to hostile code or escape attempts**.

## D4 work only after review

If we ever enable generated experiments, we will need properly audited VM/microVM isolation, authenticated approval, trusted images pinned from a verified supply chain, independent scientific reviewers, provenance-backed datasets, richer resource metering, and deliberately limited adapter manifests. No automatic Vessie/NBG/Anti-M/FutureArchive connections are present.

**Ledger Above Ego.**
