# D0 · Discovery Protocol: QP5 matched-controls audit

**Frozen identifier:** `PHIFIELD_DISCOVERY_D0_V1`  
**Mission:** `missions/qp5-d0-matched-controls.json`  
**Provenance:** `SIMULATED / authority NONE / attested false`  
**Scope:** One bounded, deterministic, local-only adapter to the existing frozen QP5 model. Not an autonomous scientist or a validated physical discovery.

## Purpose

Reuse the *structure* of a skeptical research workflow without importing any trading system or external agent code. A human supplies a question and approves a bounded experiment. D0 inspects competing, predeclared candidates, executes QP5 calculations, challenges a null control, checks an independent numerical implementation of the same energy, and saves a replayable report.

```text
QUESTION → FROZEN MISSION → PLAN (no computation)
      → EXPLICIT LOCAL APPROVAL
      → QP5 COMPUTATION → MATCHED CONTROLS
      → QP4 ENERGY CROSS-CHECK + ADVERSARIAL NULL
      → REPLAYABLE REPORT → OPERATOR REVIEW
```

This D0 release **does not** generate scientific hypotheses with an LLM, schedule experiments continuously, publish, spend money, change code, contact Vessie, or invoke any other repo. It is the first independently testable *mechanism* for the later, broader discovery protocol.

## First mission

Question: Does high positive anisotropy D/J=12 lower finite bipartite entropy relative to D/J=0 when chain length, boundary and cut are held fixed?

- **C1:** D12 has lower entropy than D0 for *every* matched geometry. One counterexample falsifies this strictly universal finite-grid statement.
- **C2:** Entropy is invariant under D0 versus D12 (negative/null candidate). A difference above `1e-7` in even one matched case falsifies this null.
- **Grid:** Frozen QP5 N=4,6,8; D/J=0,1,4,12; open/periodic; cut=1 or N/2. Exactly 48 rows and 12 matched comparisons.
- **Independent numerical control:** For each QP5 row, recompute its finite M=0 ground energy using the pre-existing QP4 `spectrum` path. Tolerance `1e-7`. These are two implementations inside one project, **not independent scientific attestation**.
- **Interpretation:** “SUPPORTED_IN_SIMULATION” means all of this candidate's declared finite-model comparisons passed. It **never** means proof of a physical phase, empirical discovery, or generally valid scientific theory.

The exact QP5 protocol, solver code and prior experimental artifacts remain untouched.

## Running on a local checkout

Install the existing numerical-physics dependency once:

```powershell
python -m pip install -e ".[spinchain]"
python -m unittest discover -s tests -p "test_discovery.py" -v
```

Review the declared mission, permissions, and candidates without running QP5:

```powershell
python -m phifieldlab.discovery plan --mission missions/qp5-d0-matched-controls.json
```

Run the bounded simulation **only after inspecting the plan**:

```powershell
python -m phifieldlab.discovery run --mission missions/qp5-d0-matched-controls.json --out artifacts/local/discovery-d0-001.json --approve-local
```

Recompute the model and compare the saved report's full structure and results:

```powershell
python -m phifieldlab.discovery verify --mission missions/qp5-d0-matched-controls.json --file artifacts/local/discovery-d0-001.json
```

Refusal by default: omitting `--approve-local` prevents a run. Output is opened with exclusive file creation: a completed report cannot be overwritten. The flag is **only** an operator's local consent declaration; it does not verify identity, authorize external work, or generate an authentic signature.

## Fail-closed contract

- Whitelisted adapter and candidate test IDs; no arbitrary Python or shell commands in mission JSON.
- Schema, row grid, bounds, origin, authority, and permissions checked before experiment execution.
- Exactly two candidates; no unknown network, repository mutation, publication, or other active abilities.
- No network client calls; no background tasks; no external API credentials.
- Report includes both candidate verdicts and the counterexamples that falsify them.
- Numerical and schema replay checks reject modifications; report receipts use SHA-256 for **consistency**, not authorship or independent verification.
- A data-feed failure, an incomplete or duplicate grid, a solver mismatch, or an unsupported mission **fails closed** instead of claiming success.
- Same-environment replay can check byte fingerprints. Floating-point differences on other CPU/BLAS stacks may change the full QP5 reference SHA even where numbers match to tolerance; record the computational environment before treating a cross-platform digest mismatch as tampering.
- Generated reports stay under ignored `artifacts/local/` and are not automatically committed or published.

## How this could evolve, after review

**D1:** Domain-neutral schema for *proposed* hypotheses, falsifiers, reference datasets, budgets and review plans. Still human-approved.

**D2:** Sandboxed multiple-candidate evaluation with separated plan/execution/review code, held-out controls, independent baselines and explicit stopping conditions.

**D3:** Optional operator-approved adapters to NBG's frozen evidence protocols and Anti-M's completion gates. Interface compatibility must be tested rather than presumed.

**D4:** Optional Vessie/Crane Fly task proposals and monitored orchestration. No standing permissions, automatic external calls, or publication by default.

Archive only with provenance and publication approval. “Better than an impressive backtest” here means **better at finding our own mistakes**.

**Ledger Above Ego.**
