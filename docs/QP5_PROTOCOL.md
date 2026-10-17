# QP5 · Finite spin-1 Schmidt-spectrum audit

**Frozen protocol:** PHIFIELD_QP5_FINITE_SCHMIDT_AUDIT_V1  
**Provenance:** SIMULATED / authority NONE / independent attestation false  
**Status:** pure-state finite-size numerical entanglement; **not experimental quantum tomography or topological certification**.

## Research question

QP1–QP4 compute low-energy spin multiplets, edge-site magnetizations, finite string correlators, anisotropy controls and finite many-body spectral gaps. QP5 adds a mathematically different observable: **the spectrum of a reduced density matrix** after dividing the chain into contiguous blocks. Do finite entanglement statistics differ between the original D=0 Heisenberg case and the high-positive-D product-favoring case, and between open and periodic geometry?

Background: F. Pollmann, E. Berg, A. M. Turner & M. Oshikawa, *Entanglement spectrum of a topological phase in one dimension*, Phys. Rev. B 81, 064439 (2010), https://doi.org/10.1103/PhysRevB.81.064439. Also S. Miyakoshi et al., *Entanglement properties of the Haldane phases: A finite system-size approach*, https://arxiv.org/abs/1612.04686.

Those references concern protected symmetry and boundary-sensitive entanglement structure. **This small-system experiment does not implement their full topological diagnostics or independently reproduce their critical claims.** An apparent pair in a Schmidt spectrum is not sufficient evidence of protected degeneracy.

## Frozen model

The model is **exactly QP3/QP4's spin-1 finite Hamiltonian**:

```text
H = +1 Σ(nearest neighbors) S_i · S_j + D Σ_i (Sz_i)^2
D/J ∈ {0,1,4,12}
N ∈ {4,6,8}
boundary ∈ {open, periodic}
```

Take the numerically lowest normalized eigenstate of the total M=0 sector. Assert eigensolver residual norm <1e−7. QP4 already checked these even-N grid ground states against all other M sectors. QP5 independently recomputes the eigenvector, then verifies its ground energy against QP4.

Choose **two cuts** per N: after the first site, and after site N/2. For each cut, reconstruct the coefficient matrix A whose physical entries correspond to the spin product basis (-1,0,+1) at each site. Compute singular values s_k by numerical SVD; the eigenvalues of the reduced density matrix are **Schmidt probabilities** λ_k = s_k², sorted descending and normalized.

Report:
- Six largest λ_k, zero-padded only when the smaller subsystem dimension has fewer than six possibilities;
- Von Neumann entropy **S = −Σ λ_k ln λ_k**, in natural units (nats);
- Reduced-state purity Tr(ρ²)=Σ λ_k²;
- Split of the first two Schmidt probabilities λ₁−λ₂;
- First Schmidt probability, eigensolver residual, numerical trace, cut/boundary metadata, and lowest M=0 energy.

These are **not** excitation energies or experimental entanglement eigenvalues. The number of bonds cut by the partition differs: for an open chain a contiguous block splits **one** bond, for a periodic ring the same partition splits **two**.

## Acceptance gates

1. Produce **48 rows**: 3 chain lengths × 4 anisotropies × 2 boundaries × 2 cut positions.
2. Schmidt probabilities nonnegative to numerical tolerance and sum to 1. For a first-site cut, the complete Schmidt distribution has at most 3 nonzero values; its entropy must not exceed ln 3.
3. Each row reports a normalized M=0 eigenstate, positive purity ≤1, nonnegative entropy and λ₁−λ₂≥0.
4. At D/J=12, the **entropy decreases** and the **leading Schmidt probability increases** relative to D=0 under the same N/boundary/cut for all tested cases. A mismatch fails the declared benchmark; do not hide counterexamples.
5. Independently confirm energies against QP4 at exactly the same N, D and geometry within 1e−7.
6. A source-controlled claim firewall explicitly forbids claiming a thermodynamic Haldane phase, protected Schmidt-level degeneracy, superconducting signature, fractional-spin measurement or any training of AI weights.
7. Python tests and clean GitHub Actions must regenerate the artifact, validate the result, run all existing tests, then generate browser data again before Node tests/Vite build.
8. Refuse to overwrite output files; verify recursively checks JSON schema/metadata and numerical replay within 1e−7.

## Running locally

Install the optional physics dependencies first:

```bash
python -m pip install -e ".[spinchain]"
python -m phifieldlab.qp5 show
python -m phifieldlab.qp5 write --out artifacts/local/qp5-run.json
python -m phifieldlab.qp5 verify --file artifacts/local/qp5-run.json
python -m unittest discover -s tests -p test_qp5.py -v
```

The React viewer consumes **build-generated**, uncommitted `web/src/data/qp5-reference.json`. For local frontend development, from repository root:

```bash
PYTHONPATH=src python -m phifieldlab.qp3 write --out web/src/data/qp3-reference.json
PYTHONPATH=src python -m phifieldlab.qp4 write --out web/src/data/qp4-reference.json
PYTHONPATH=src python -m phifieldlab.qp5 write --out web/src/data/qp5-reference.json
cd web && npm install && npm test && npm run build
```

On Windows PowerShell, prefix the generation commands with `$env:PYTHONPATH = "src"` on its own line; then use `python -m phifieldlab.qp5 write --out ...`. Existing outputs are intentionally immutable; use a new path or explicitly remove **only your generated build copy** to regenerate.

## Interpretation limits and future research

Finite entanglement signatures can strongly depend on n, cut location, chosen M-sector eigenvector, and whether the partition crosses one or two bonds. No quantified thermodynamic finite-size extrapolation, symmetries' projective representations, twist-boundary invariant, physical noise modeling, quantum-device preparation or raw experimental spectra are present here. The high-D regime favors a product-like ground state but is not by itself a certified distinct phase in this finite dataset.

After QP5: pursue symmetry-resolved Schmidt sectors and matched twisted boundary controls, then larger-N/DMRG benchmarks, with explicit independent scientific review.

**Ledger Above Ego.**
