# D1 · Research Mission Designer

**Protocol:** `PHIFIELD_DISCOVERY_D1_MISSION_V1`  
**State:** `PROPOSAL_ONLY`  
**Provenance:** `PROPOSED / authority NONE / attested false`  
**Execution:** **DENIED**. This is a research **design** tool, not an autonomous experiment runner.

## What D1 adds

The D0 experiment remains exactly as frozen: a QP5-specific simulator with explicit local approval. D1 sits *before* any scientific computation, and makes the proposal format portable across **science, software, networking, engineering, environment, creative work, and mathematics**.

From the public React page, open **Designer** and select a domain. Fill out a bounded mission:

1. **Question and scope:** one research question, clearly in/out of scope.
2. **Competing hypotheses:** 2–4 candidate claims, each with a prediction and a separate falsifier.
3. **Evidence and tests:** *claimed* source kind, source description, replay plan, baseline, negative control, metric, method, success/failure criteria and uncertainty.
4. **Risks and budgets:** anticipated harms, a stop condition, runtime cap and abstract compute-unit cap.
5. **Permission firewall:** execution, network access, repository writes, publication and spending are forbidden; human approval will be required *by a future execution protocol*.

The UI validates locally, previews the JSON, imports existing D1 JSON under a 128 KiB limit and exports a valid proposal as a browser-local download. **Neither import nor export performs a server request or starts research.** No API keys, network services, AI inference, unattended actions or tracking are involved in this component.

Examples are source-controlled in `missions/d1-examples/` and include networking, creative feedback and simulated spin-chain research. Additional domain choices generate editable *proposal templates*, **not** tested domain adapters.

## Offline CLI validation

Use an existing local checkout of ΦField Lab:

```powershell
python -m pip install -e .
python -m phifieldlab.discovery_d1 validate --file missions/d1-examples/network-switch-latency.json
python -m phifieldlab.discovery_d1 validate --file missions/d1-examples/music-arrangement-listener-study.json
python -m unittest discover -s tests -p test_discovery_d1.py -v
```

The validator is pure Python (stdlib) and reads the exact same JSON Schema bundled in `src/phifieldlab/schemas/d1.schema.json` that the browser uses. The supported schema subset is intentionally restricted. A valid response includes the file's SHA-256 digest, `execution_authorized: false` and `review: REQUIRED_BEFORE_ANY_EXECUTION`. A digest only identifies bytes; it does not establish independent provenance, correctness or operator identity.

## Security and epistemic boundaries

- **All new fields are untrusted text, never executable commands.** No dynamic code evaluation, remote endpoints, shell instructions, side effects or passive approval.
- Root and nested schema objects forbid extra keys; each permitted key is required. Typed budget values and bounded input sizes prevent silent escalation.
- Proposals cannot claim `VERIFIED`, `APPROVED`, `OBSERVED` as their governing origin, or independent attestation. The *evidence.source_kind* is a user's **unverified description** of potential evidence, not a verified provenance upgrade.
- Candidate IDs must be unique and ordered H1–H4. Every hypothesis needs a separately stated testable prediction and falsifier. Success/failure criteria must differ.
- The browser runs the same validation rules as the Python CLI, but CLI validation is the authoritative import gate for any future backend. Browser JSON parsing cannot detect duplicate source keys; the Python parser explicitly rejects duplicate keys, oversized content and nonfinite numbers.
- Source-control examples and templates do **not** constitute observations, results, proof, or scientific validation.
- The D0 frozen mission is **not** accepted by D1; D1 drafts are **not** accepted by the D0 execution engine.
- Runtime and compute limits are *proposed budgets*, never grants. Any future D2 runner must define explicit capability allowlists, trusted provenance, sandboxing, fresh operator approval and a separate independently testable execution contract.

## Explicitly out of scope

Automatic literature retrieval, AI-generated hypotheses, live experiments, running scripts, submitting pull requests, analyzing uploaded private evidence, orchestration through Vessie or Crane Fly, making medical/financial decisions, model promotion, and publishing results. No future connections should be implied to exist.

## Acceptance checklist

- Python and Node tests validate all 3 fixtures and verify fail-closed refusals for bogus authority, extra keys, escalated permissions and invalid candidates.
- Browser builds and exports only typed, proposal-only missions.
- No edits to D0, E0, E1 or QP0–QP5 results, datasets, frozen protocols or solver implementations.
- CI and Pages builds both green before merge.

**Ledger Above Ego.**
