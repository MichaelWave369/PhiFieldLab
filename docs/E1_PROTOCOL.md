# ΦField E1: Alternate-Route Message Passing (candidate)

**Protocol:** PHIFIELD_E1_ALTERNATE_ROUTE_V1  
**Origin:** SIMULATED  
**Authority:** NONE  
**Independent attestation:** false

## Research question

After withholding one connection from an undirected graph, can a graph neural network trained on some *graph families* predict whether a different route still connects the removed edge's two endpoints on **unseen graph families**?

This is a **synthetic graph benchmark**, not a claim about NBG geometry, physics, particle tracks, the internet, or any real network.

## Model: a real graph message-passing network

- Node inputs: a source marker, a target marker, and a valid-node marker.
- Remaining edges are undirected for reachability, but randomly assigned orientations and noisy scalar transport measurements. Those measurements are auxiliary, not a physical signal.
- In each round, a shared learned message function uses its neighbor's hidden state plus the signed edge value.
- Messages are accumulated at target nodes via \`scatter_add_\`. A GRUCell updates node states.
- After **seven** rounds by default, a learned head reads the marked target state and predicts whether an alternate path exists.
- Parameters are trained from random initialization with binary cross-entropy and AdamW, then exported to safetensors.

**Not** an LLM, a pretrained adapter, a foundation model, a general graph reasoning system, or evidence that NBG mathematics explains neural weights.

## Explicit split / leakage barriers

| Split | Families | Default examples |
| --- | --- | ---: |
| Train | ring_tail, barbell, chord_tail | 960 |
| Validation | ring_tail, barbell, chord_tail | 240 |
| **Held-out test** | **ladder_tail, wheel_tail, double_square** | **360** |

Each family is class-balanced using a deterministic exact-search label after deleting one edge. Random node labels, edge order, orientations, potentials, and noise discourage brittle positional shortcuts. The held-out families are intentionally distinct by construction. **This does not exclude the possibility that local node-degree or topology motifs make the test easy.**

Train/validation/test use separate PRNG seeds derived from the run seed; hashes bind the generated tensor data and family sequence. The model's best state is selected using **validation loss only**. Held-out test labels are not used in gradient updates or checkpoint selection.

## Baselines (never hide the exact answer)

1. **One-hop graph search:** a deliberately limited connectivity check.
2. **Two-hop graph search:** a stronger local search limit.
3. **Exact breadth-first search:** fully solves this *constructed* target task and should score 100%.

E1 is a useful system exercise even when the model loses to exact BFS. Do not present an improved score over a one- or two-hop cutoff as a breakthrough over mathematics.

## Operator workflow (Windows / CPU)

Prerequisites: Python 3.10+, a supported PyTorch installation, NumPy and safetensors (already declared in the root package).

\`\`\`powershell
py -m pip install -e .
python -m unittest discover -s tests -v
python -m phifieldlab.e1 train --out artifacts/local/e1-trial-001 --device cpu
python -m phifieldlab.e1 verify --out artifacts/local/e1-trial-001 --device cpu
\`\`\`

CUDA must be explicitly requested by passing \`--device cuda\` to \`train\`. A missing CUDA installation raises an error; there is no silent CPU fallback for an explicit CUDA request. The local RTX 5070 path is **not** verified by GitHub Actions.

A short smoke run:

\`\`\`powershell
python -m phifieldlab.e1 train --out artifacts/local/e1-smoke --epochs 3 --train-count 96 --validation-count 48 --test-count 60 --width 12 --rounds 3 --device cpu
python -m phifieldlab.e1 verify --out artifacts/local/e1-smoke --device cpu
\`\`\`

The output directory must not exist beforehand. Training never replaces existing model files. It creates four files:

- \`model.safetensors\`: original trained parameters, saved without pickle.
- \`config.json\`: frozen settings and split-family definitions.
- \`report.json\`: score confusion matrices, per-family scores, epoch losses and promotion decision.
- \`manifest.json\`: SHA-256 hashes for the three other files.

The verifier checks hashes, deterministically regenerates every split, reloads weights, replays training/validation/test **classification** metrics and reruns every baseline. Hashes detect inconsistency, not falsified original observations or independently witnessed training. Numerical replay on other hardware/software versions may differ; pinned same-environment runs are the supported reproducibility target.

## Declared E1 performance gate

Report \`PASS\` only when all three are true on withheld families:

- At least 80% overall learned-model test accuracy;
- At least five percentage points above the two-hop baseline;
- At least 70% learned-model accuracy in **each** held-out family.

A passing performance gate **does not** supersede the 100% exact BFS baseline or demonstrate NBG validity. A failing gate remains visible in the report and does not stop artifacts from being saved.

## Local development observation (unattested)

A local CPU trial with seed 369, 30 epochs, 960/240/360 examples, 32 hidden units and seven message rounds produced **360/360 accuracy on the withheld test**, versus 360/360 exact BFS, with a passing *internal* research gate. The result was replayed and manifest hashes checked locally. The local trial is *not* independent attestation and is not offered as a verified checkpoint from GitHub. CI retrains from scratch; its generated artifact and receipt should be inspected separately before citing numbers.

## Falsifiers and future work

E2 should add topology perturbations, counterfactual edge-feature controls, degree-matched cases, alternate-family benchmarks, multiple seeds, and empirical data candidates with appropriate licensing and provenance. Only then investigate any possible link to NBG's Keyholes, closure or transport. E1 itself establishes no such link.

**Ledger Above Ego. Report failures and exact baselines.**
