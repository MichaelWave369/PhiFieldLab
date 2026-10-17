# D2 · Approved Synthetic Network Queue Research (first execution adapter)

**Protocol:** `PHIFIELD_D2_EXECUTION_RECEIPT_V1`  
**Worker:** `PHIFIELD_D2_SYNTHETIC_QUEUE_V1`  
**Registered mission:** `missions/d1-examples/network-switch-latency.json`  
**Status:** `SIMULATED / AUTHORITY NONE / ATTESTED FALSE`  
**New ability:** A **single allowlisted deterministic toy computation**, only after a separate, explicit local operator command.

## What this is

D0 demonstrated a frozen QP5 test. D1 defined portable, **non-executable** research proposals. D2 is the first tightly bounded local experiment **executor** for exactly one reviewed proposal. It does not execute imported JSON, arbitrary scripts, user-generated Python, prompts, agents or changes to real networks. In particular, D1's `local_execution: false` is preserved. D2's separate CLI approval is limited to the fixed built-in simulator, not a general permission upgrade.

### Frozen question and evaluation

The networking proposal asks whether queue scheduling reduces p95 latency without worsening packet loss. This D2 **toy** concretizes that question to **latency-sensitive flow** p95 under a synthetic two-flow queue. The original D1 proposal did not precisely select the packet class; the D2 protocol explicitly adds that restriction and **must not be mistaken for general switch p95**.

- Five predetermined random seeds: 101, 103, 107, 109, 113.
- Each seed generates 1,200 one-millisecond *model time slots*, two synthetic traffic classes, and a maximum queue of 64 packets.
- Compute FIFO baseline and simplified two-flow fair scheduling against the same packet trace.
- Repeat FIFO on the same trace as a **sham / negative control**; require exact equality.
- Measure latency-class p95 as nearest-rank percentile and packet loss as a fraction of generated packets. Also report bulk and overall p95 for context.
- **Strict exploratory toy threshold:** Each of five seeds must show at least 10% latency-class p95 reduction without increasing total packet drops. A failure is reported as a failure, never corrected by changing the criterion after observing outcomes.
- No device, interface, IP address, packet capture, firmware, live switch, DNS call, cloud model, or telemetry endpoint is consulted.

No real-world performance conclusions follow from this toy, regardless of its verdict. There is no external validation of the traffic model.

## Local Windows PowerShell run

Requires a **source checkout of PhiFieldLab** and an installed editable Python package:

```powershell
python -m pip install -e .
$mission = "missions/d1-examples/network-switch-latency.json"
$plan = python -m phifieldlab.discovery_d2 plan --mission $mission | ConvertFrom-Json
$plan
```

Inspect the plan, the recognized mission, the frozen `src/phifieldlab/schemas/d2_policy.json` and this document before approving it. `plan` parses the proposal and policy, **without running simulation**.

To explicitly run this specific approved mission and save a new immutable receipt:

```powershell
python -m phifieldlab.discovery_d2 run --mission $mission --approve-local --expect-sha256 $plan.mission_sha256 --out artifacts/local/d2-network-001.json
```

To independently **replay in a new child process using the same code**:

```powershell
python -m phifieldlab.discovery_d2 verify --mission $mission --approve-local --expect-sha256 $plan.mission_sha256 --file artifacts/local/d2-network-001.json
```

Both `run` and `verify` require a fresh `--approve-local` flag and matching mission digest. Verification recomputes the full simulation, compares every receipt field and checks source-code SHA-256 fingerprints. It does **not** establish independent implementation, identity, authenticity or empirical validation. The digest consent confirms the selected proposal bytes, not who the human operator is.

Receipt output is create-only under ignored `artifacts/local/`, and never overwrites a previous run. Change the receipt basename for new runs. No automatic publication or external upload is performed.

## Execution limitations (do not call this a sandbox)

The subprocess uses Python's `-I` mode, a temporary working directory, a reduced environment, a fixed module path and a 30-second parent-enforced timeout. **These protections are not OS-enforced isolation.** Python `-I` does not disable socket access or block filesystem reads/writes. A malicious modified worker could bypass restrictions. This release is safe to characterize as a **fixed, bounded, no-network-by-design simulator under human control**, *not* a hardened container or secure multi-tenant runner.

The process requires an installed `phifieldlab` package accessible to `python -I` (the editable install above works in project CI). CPU and memory are not independently OS-capped; only fixed model size and time are bounded. The 30-second subprocess timeout only applies to the worker and does not cap external operational steps. The worker never receives commands, source files, environment secrets or network addresses.

The `--out` path must resolve below the repository's `artifacts/local/` and end in `.json`; other writes are denied by the CLI. A malicious process with the same OS user identity might still write elsewhere; this is not a filesystem access-control boundary.

## Security, evidence and negative controls

- Only byte-for-byte copies of the **source-controlled** D1 networking example are admitted. Other D1 proposal files are rejected, including creative/science examples. Edited source-controlled mission text cannot be granted runtime authority without modifying that checked-in fixture.
- Every worker result is checked for provenance, expected seed set, size, packet accounting, paired offered-load equality, sham control and a blocked scientific-promotion status.
- The receipt binds the D1 mission digest, frozen policy digest and implementation-file digests, with `SIMULATED / AUTHORITY NONE / ATTESTED FALSE` everywhere.
- The local React exhibit is a **read-only structural inspector**. Uploading a receipt there remains browser-local, and passing its checks **does not prove** a real local run occurred. CLI replay is needed for consistency checks.
- CI runs the fixed synthetic runner as a test with explicit approvals **inside the test code**, never on actual networks, and does not publish generated receipts.
- Negative test cases: missing approval, wrong digest, other D1 mission, modified D1 bytes, output path escape, immutable output collision, receipt tampering, unsupported scientific promotion, repeated seed/sham corruption and invalid scheduling policy.

## Future D3 gate

Before enabling additional adapters or untrusted inputs: OS-level filesystem/network isolation, user identity and authorization, independent review of accepted missions, signed provenance, dataset versioning, proper experimental uncertainty and real-world benchmarking plans. Do not silently upgrade D2 claims.

**Ledger Above Ego.**
