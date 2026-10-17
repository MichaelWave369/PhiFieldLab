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

## Public React research dashboard

[**ΦField Lab Research Dashboard**](https://michaelwave369.github.io/PhiFieldLab/) shows the committed E0 results, artifact provenance, and an interactive **exact-arithmetic** cycle demonstration. The public site does not run neural inference, train models, or claim physical validation. See [web/README.md](web/README.md) for setup and publishing instructions.

## E1 graph message-passing candidate

E1 introduces an independently trained graph-neural-network experiment for detecting whether an alternative route remains after one graph edge is withheld. Training families (rings with tails, barbells, chorded rings) are distinct from held-out test families (ladders, wheels, connected squares). The E1 workflow retrains and saves original synthetic-model weights as a short-lived GitHub Actions artifact, then checks manifest integrity and classification replay. **Exact BFS remains the perfect 100% mathematical baseline.**

\`\`\`powershell
python -m phifieldlab.e1 train --out artifacts/local/e1-trial-001 --device cpu
python -m phifieldlab.e1 verify --out artifacts/local/e1-trial-001 --device cpu
\`\`\`

Read [E1's frozen protocol and evaluation limits](docs/E1_PROTOCOL.md). E1 is **SIMULATED / authority NONE**, not physical validation or an NBG proof. The React Pages dashboard continues to show frozen E0 evidence until an explicitly reviewed E1-site integration is merged.
