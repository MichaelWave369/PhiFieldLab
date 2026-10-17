# ΦField Lab (PhiFieldLab) · v0.1 / E0

**Train original numerical weights. Keep the receipts. Separate simulation from observation.**

This repo-ready starter provides an **actual train-from-random-init** scientific ML toy experiment. It learns signed transport residuals from synthetic directed cycles, exports its learned **safetensors weights**, compares results with exact mathematics and a weak negative control, and verifies SHA-256 file digests and held-out-score replay. It needs no cloud provider, external dataset download, API keys, or other MichaelWave369 repositories.

> **Scientific status: SIMULATED / authority NONE.** This is *not* a validated law of physics, an NBG proof, a general graph neural network, or a CERN-style foundation model. It is the training pipeline's first measurable acceptance test.

## Windows / local quick start

Python 3.10+, CPU works; CUDA requires a separately installed CUDA-enabled PyTorch build supported by your GPU and drivers.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
python -m phifieldlab train --out artifacts/local/trial-001 --device cpu
python -m phifieldlab verify --out artifacts/local/trial-001 --device cpu
```

To request a locally configured CUDA device, replace `--device cpu` with `--device cuda` on **train**. Explicit CUDA requests fail if PyTorch cannot see CUDA. Use a new, empty run directory on each training run. The output checkpoint is `model.safetensors`, plus `config.json`, `report.json`, and SHA-256 `manifest.json`.

For a lightweight smoke run:

```bash
python -m phifieldlab train --out artifacts/local/smoke --device cpu --epochs 15 --train-count 512 --val-count 128 --test-count 128
python -m phifieldlab verify --out artifacts/local/smoke
```

## Experiment scope

1. Simulate oriented edge values from hidden scalar potential differences with optional additive residue.
2. Train a compact permutation-invariant edge-set model (not a general message-passing GNN).
3. Hold out larger cycle lengths: training lengths 3–6, testing 7–10.
4. Score numerical transport residual and injected-defect classification.
5. Always report exact-arithmetic baseline: it is deliberately a strong and typically perfect baseline.
6. Hash model/config/report artifacts; independently replay scores from the saved checkpoint.

Read [the frozen E0 protocol](docs/E0_PROTOCOL.md) and [proposed integration boundaries](docs/INTEGRATION_CONTRACT.md).

To replay the bundled CPU example: `python -m phifieldlab verify --out artifacts/sample-e0 --device cpu`.

## Artifact custody and model weights

Model parameters really are updated during training and exported to safetensors. Repository code is MIT. Each training output is local and ignored by Git to prevent accidental large artifacts or claims of independently verified training. The included `artifacts/sample-e0/` checkpoint is an **operator-unverified synthetic demonstration** produced on a CPU. Its receipt reports 384/384 classifications correct on held-out cycle **sizes**, matching an exact arithmetic baseline. That result does not demonstrate novel scientific knowledge or model superiority. SHA-256 protects consistency, not authenticity. No third-party model weights are included or copied.

## Next gated steps

- E1: masked/missing-edge learning and actual graph-message-passing baselines, with held-out graph **topologies**, not just sizes.
- E2: connect only to an independently reviewed, frozen NBG task definition with leakage controls.
- E3: research real scientific data candidates and licensing, after useful external benchmarks.
- E4: optional adapters to PhiStream, NBGPocketMesh and Vessie, gated by real compatibility and permissions.

**Ledger Above Ego.** Report the negative controls, even when they're annoying.

## QP0: Quantum Parity Laboratory (new independent toy)

The public React site now includes an interactive **QP0 edge-exchange toy**, inspired by a 2026 *Nature* demonstration of parity-dependent superconducting coupling in triangulene Haldane chains ([DOI](https://doi.org/10.1038/s41586-026-11117-y)). It visualizes the *assumed* alternation of the effective two-edge-spin exchange sign, spin-0/singlet versus spin-1/triplet toy ground states, and an explicit **parity-blind negative control**. This is **SIMULATED / authority NONE**: no paper spectra, superconducting bath, YSR energies, or independently validated NBG relationships are claimed.

Run the independent 4×4 Python spin solver and its null control:

```bash
python -m phifieldlab parity --start 3 --stop 16 --amplitude 1 --decay-length 4
```

Read [QP0 assumptions, acceptance checks, and next gates](docs/QP0_PROTOCOL.md). E0 experiment and artifacts remain unchanged.

## QP1: finite spin-1 chain (computed, not measured)

A new independently written sparse-matrix Heisenberg spin-1 solver computes low-energy multiplets for **N = 3–8**. It discovers odd/even ground-spin behavior for open boundaries *without* QP0's imposed alternating exchange sign, and tests periodic rings as a boundary negative control. The public React site can inspect a frozen, replay-tested computational JSON snapshot. No superconducting substrate, YSR spectrum, or Haldane-phase invariant is implemented.

Optional local dependency and commands:

```bash
python -m pip install -e ".[spinchain]"
python -m phifieldlab spinchain --start 3 --stop 8
python -m unittest discover -s tests -v
```

See [QP1 protocol](docs/QP1_PROTOCOL.md) and the [read-only reference snapshot](web/src/data/qp1-reference.json). **Scientific status: SIMULATED / authority NONE.** E0 training and QP0 exchange results remain untouched.

## Public React research dashboard

[**ΦField Lab Research Dashboard**](https://michaelwave369.github.io/PhiFieldLab/) shows the committed E0 results, artifact provenance, and an interactive **exact-arithmetic** cycle demonstration. The public site does not run neural inference, train models, or claim physical validation. See [web/README.md](web/README.md) for setup and publishing instructions.

## QP2: finite edge-state fingerprints (computed, not observed)

QP2 adds new state-vector observables to the frozen QP1 spin-1 chain model without assuming QP0's parity rule. It computes **site-resolved M=1 spin expectations** for odd open N=3,5,7 and **longitudinal string-vs-two-point correlations** for even open/ring N=4,6,8, exposing a subtle full-endpoint string-operator false-positive trap. CI independently recomputes the browser JSON from the Python solver. This is finite synthetic Hamiltonian research, **SIMULATED / authority NONE**, not an empirical Haldane-phase or superconductivity finding.

```bash
python -m phifieldlab.qp2 show
python -m phifieldlab.qp2 verify --file web/src/data/qp2-reference.json
```

Read the [QP2 predeclared protocol](docs/QP2_PROTOCOL.md). The [React lab](https://michaelwave369.github.io/PhiFieldLab/#edge-fingerprints) presents only source-controlled calculated values.

## QP3: matched spin-chain Hamiltonian controls

The QP3 laboratory holds a finite open spin-1 Heisenberg chain and its probe sites fixed, then changes only the single-ion anisotropy **D Σ(Sz)²** at **D/J = 0, 1, 4, 12** for N = 4, 6, 8. It calculates the same nonlocal string, ordinary two-point, local spin fluctuation and all-zero-product overlap observables across every condition. **D=0 must reproduce QP2**. D=12 is a high-anisotropy reference, not an independently established phase or empirical measurement.

The React viewer uses JSON **generated by the actual Python solver during the GitHub Pages build**, not copied numerical claims. Install the spin-chain extras for local use:

```bash
python -m pip install -e ".[spinchain]"
python -m phifieldlab.qp3 write --out artifacts/local/qp3-run.json
python -m phifieldlab.qp3 verify --file artifacts/local/qp3-run.json
```

See [QP3's frozen matched-control protocol](docs/QP3_PROTOCOL.md). **SIMULATED / authority NONE / unattested**. QP0–QP2 and E0/E1 remain separate and unchanged.

## QP4: finite spectral gap cross-examination

QP4 holds the QP1/QP3 spin-1 Hamiltonian fixed and examines its actual **finite many-body excitation spectrum** across D/J=0,1,4,12, N=4,6,8, and both open/periodic boundaries. It computes every nonnegative M-sector minimum, the second M=0 energy level, and separate neutral/magnetization-changing gaps. At D=0 it must reproduce QP1; at all open D grid points the M=0 ground energy must reproduce QP3. The React data is **computed during the Pages build** and is not hand-authored or checked into the repo.

```bash
python -m pip install -e ".[spinchain]"
python -m phifieldlab.qp4 write --out artifacts/local/qp4-run.json
python -m phifieldlab.qp4 verify --file artifacts/local/qp4-run.json
```

Read the [QP4 frozen protocol](docs/QP4_PROTOCOL.md) and visit the [live research exhibit](https://michaelwave369.github.io/PhiFieldLab/#spectral-gaps) after its deployment. **SIMULATED / authority NONE / unattested**: no measured gap, critical-point estimate or physical Haldane phase inferred.
