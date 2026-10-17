# ΦField Lab public research dashboard

Live site target: https://michaelwave369.github.io/PhiFieldLab/ (only after the Pages workflow deploys successfully).

## Development

Requires Node 22+.

```sh
cd web
npm install
npm run dev
npm run build
```

Local dev URL uses the repository prefix: http://127.0.0.1:5173/PhiFieldLab/

## What is implemented

- An original responsive React interface, with the E0 sample report/config/manifest imported from the **existing committed scientific artifacts** at build time.
- A separate, synthetic **exact arithmetic** directed-cycle explorer with interactive controls. It never performs neural inference.
- Real sample E0 learned, exact-rule and negative-control scores. The header KPIs always describe the bundled sample.
- Read-only SHA-256 values from the committed manifest, with copy actions (no in-browser verification of the weight bytes).
- Local-only JSON report import for E0-formatted simulated results; allowed shape and size checked; displayed outcomes are always unverified operator claims. No backend, file uploads, telemetry or data storage.
- Explicit research status: **SIMULATED / authority NONE / independent attestation false**.

## Limitations

No independent physics finding, no production inference server, no GPU training on the site, no model weights loaded by JavaScript, and no authority beyond the frozen E0 evidence. There is no claim that the model beats the exact mathematical baseline.

## GitHub Pages

The root `.github/workflows/pages.yml` builds the Vite app on pull requests and deploys its static `web/dist` output only after a change merges to `main`. In repository **Settings → Pages**, choose **GitHub Actions** as the build/deployment source if not already selected. Inspect the deploy job status and the actual Pages URL after merge.

The site's base URL is set to `/PhiFieldLab/`, not `/`. All scientific Python training and model files remain separate and unmodified.

## QP0 Quantum Parity Lab

A second, independent experimental surface lives at `#quantum-parity`: an original two-spin analytic parity toy, a live molecule-count/decay control, a parity-blind negative-control comparison, and JSON exports that declare `SIMULATED / authority NONE`. The Python package has a separate matrix-diagonalized calculation and unit tests. No paper measurements or YSR spectra are imported or synthesized. See [QP0 protocol](../docs/QP0_PROTOCOL.md).

Check the client toy locally using `npm test` before `npm run build`; the Pages workflow also runs it on PRs. The existing E0 weights and results are not modified.

## QP1 finite spin-1 chain

The dashboard section `#spin-chain` reads an original, committed, numerically replay-tested **finite Heisenberg model** snapshot. It compares open versus periodic boundaries and renders calculated multiplets/gaps, without JavaScript eigensolvers or any laboratory observations. See [QP1 protocol](../docs/QP1_PROTOCOL.md). Local scientific toolchain: `pip install -e ".[spinchain]"`, then `python -m phifieldlab spinchain`.

## QP2 Finite Edge-State Fingerprints

The QP2 viewer displays **precomputed** open-chain M=1 site magnetization profiles (N=3,5,7), and M=0 finite longitudinal string-vs-two-point correlations (N=4,6,8), with periodic geometry comparisons. Its JSON is recomputed and checked by Python CI. The browser never solves a Hamiltonian. A nonzero finite string signal is not proof of a Haldane phase, and a periodic ring is not a null control. See [QP2 protocol](../docs/QP2_PROTOCOL.md).

## QP3 anisotropy controls

The QP3 React panel displays matched finite spin-1 Hamiltonian results generated **from Python at build time**. It holds chain length and geometry fixed while selecting D/J=0,1,4,12. It compares string and ordinary correlations, mean local (Sz)^2, and |0...0> product overlap. The Python-generated JSON is intentionally *not committed* and no browser inference occurs. To build locally from repository root, install `numpy` and `scipy`, then run `PYTHONPATH=src python -m phifieldlab.qp3 write --out web/src/data/qp3-reference.json` before `cd web && npm install && npm test && npm run build`. Python refuses to overwrite that file; delete only this generated build artifact manually if you intend to regenerate it. See [QP3 protocol](../docs/QP3_PROTOCOL.md).
