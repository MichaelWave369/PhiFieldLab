# QP1 · Frozen finite spin-1 chain protocol

**Scientific authority: NONE. Provenance: SIMULATED.** This is an original numerical many-body model, not a physical experiment or a reproduction of superconducting tunnelling measurements. It extends QP0 but *does not reuse QP0's alternating edge-exchange assumption*.

## Sources and scope

Motivating paper: K. Vaxevani et al., *Nature* **658** (2026), published 14 October 2026, [DOI:10.1038/s41586-026-11117-y](https://doi.org/10.1038/s41586-026-11117-y). The paper investigates Haldane spin-1 triangulene chains on proximitized Au/Nb and parity-dependent YSR resonances. Important caution for finite systems: A. Machens et al., [arXiv:1211.4357](https://arxiv.org/abs/1211.4357). Neither study verifies NBG.

## Locked experimental question

For open, antiferromagnetic spin-1 Heisenberg chains of length N=3–8, does the **computed** ground-state total spin alternate S=1 (odd) and S=0 (even), without imposing parity in the Hamiltonian? Does this pattern persist when a wraparound interaction closes the chain into a periodic ring?

## Frozen model and arithmetic

- H = J Σ_(nearest-neighbor bonds) Sᵢ·Sⱼ, with isotropic spin-1 matrices and fixed J=+1 for the committed reference.
- Construct the physical three-state basis mᵢ=-1,0,+1; overall Hilbert space grows as 3^N. Cap computation at N≤8.
- Preserve total Sz through independent M=0,1,2 sectors. Diagonal terms are Jmᵢmⱼ. Off-diagonal terms use J/2 (Sᵢ⁺Sⱼ⁻ + Sᵢ⁻Sⱼ⁺).
- Diagonalize tiny sectors densely and others through deterministic-start SciPy sparse `eigsh`. Compare sector ground energies under SU(2) symmetry to infer the lowest multiplet total spin.
- The reported finite-chain excitation gap is the smallest resolved positive difference in the sampled spectra, in **model units J**, not a laboratory gap, a YSR energy, or a thermodynamic Haldane gap.
- **Negative control:** add the bond from the last to the first site with no change in J, spin matrices or N. This removes exposed ends.

## Acceptance criteria

1. Analytical N=2 open spin-1 two-site eigenvalues in M=0: −2, −1, +1.
2. Each Hamiltonian is real symmetric and preserves total Sz.
3. For N=3–8, open-chain ground spins equal [1,0,1,0,1,0], an output of eigensolvers and not an assumption.
4. The N=3 periodic ring has S=0, different from N=3 open S=1; the tested N=3–8 rings show S=0.
5. Independently replay browser data from Python. Compare numerical results within 1e-7 across platforms. Keep any discrepancies visible.
6. Retain metadata `SIMULATED / authority NONE / attested false` and both positive and negative control results.
7. Do not assume monotonicity across even and odd N: finite-chain gaps can oscillate. Do not silently promote model output to observations.

## How to run

Install the optional numerical physics tools:
```bash
python -m pip install -e ".[spinchain]"
python -m phifieldlab spinchain --start 3 --stop 8
python -m phifieldlab spinchain --start 3 --stop 8 --write artifacts/local/qp1-replay.json
python -m unittest discover -s tests -v
cd web && npm test && npm run build
```
`--write` uses exclusive create: frozen JSON is never overwritten. The web dashboard reads only its source-controlled JSON snapshot. It does **not** diagonalize the Hamiltonian in the browser or run neural inference.

## Unsolved gates

QP1 has **not** established string order, fractional edge-state localization, a thermodynamic Haldane phase, or actual proximity-induced superconductivity. It does not predict Yu–Shiba–Rusinov spectra and does not fit published molecular tunnelling data. Next steps require independently reviewed theoretical benchmarks, data access/rights, and separately specified superconducting physics. Any NBG comparison requires a new pre-registered falsifiable protocol.

**Ledger Above Ego:** finding a pattern is not the same as explaining all of the physics.
