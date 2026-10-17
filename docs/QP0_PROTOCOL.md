# QP0 · Quantum Parity Laboratory | frozen toy-model protocol

**Status: IMPLEMENTED TOY MODEL, SIMULATED / authority NONE.** This branch adds an independently written educational edge-exchange calculation to PhiFieldLab. It does **not** reproduce the experiment, use its raw scanning-tunnelling spectra, measure YSR energies, solve a superconducting impurity problem, or establish a theory of NBG.

## Published inspiration, not our evidence

K. Vaxevani et al., "Parity-dependent coupling of molecular spin chains to a superconductor", *Nature* **658**, 617–622 (published 14 Oct 2026), DOI [10.1038/s41586-026-11117-y](https://doi.org/10.1038/s41586-026-11117-y).

The article describes spin-1 triangulene Haldane chains atop a proximity-superconducting Au(111)/Nb(110) surface: odd-length chains exhibit intragap Yu–Shiba–Rusinov (YSR) states with global S=1, while even-length chains have an S=0 ground state. Crucial limitations: even chains still exhibit spin excitations, and at N=14 faint incipient YSR components are discussed. "Even = no magnetism" and "adding a molecule switches off superconductivity" would both be misleading.

## Exactly what QP0 computes

Model **only** two spin-1/2 edge degrees of freedom, with a prescribed effective exchange:

H_edge = J_eff(N) (s_L · s_R)

J_eff(N) = (-1)^N × J0 × exp[-(N - 2)/xi], for integer N >= 2.

Here J0 > 0, xi > 0 are arbitrary **model-unit** controls. Positive J favours the spin-0 singlet (E_s = -3J/4); negative J favours the spin-1 triplet (E_t = +J/4). The excited multiplet gap is |J|. We assume the parity-alternating sign: this is **not a derived prediction** or a fit of measured coupling constants.

Negative control: keep J_eff positive for all N while preserving its magnitude. It should remain singlet for odd and even N, exposing that QP0's parity result depends entirely on the sign-alternation assumption.

JavaScript implements the analytic energy levels for the browser display; Python independently constructs the 4×4 quantum-spin Hamiltonian with Pauli spin operators and diagonalizes it. A numerical calculation at four Hilbert-space dimensions is **not** a full chain many-body simulation.

## Locked acceptance / failure criteria

1. Analytic and matrix-diagonalized eigenvalues agree at tested N.
2. Alternating toy exchange yields spin 0 for even N, spin 1 for odd N.
3. Parity-blind negative control does *not* exhibit switching.
4. Excitation gap decreases monotonically with N for J0, xi > 0.
5. Every exported web receipt includes SIMULATED, authority NONE, input parameters, and negative-control outputs.
6. Invalid model parameters fail explicitly.
7. Do not label the model "verified against Nature"; study notes are **qualitative sourced descriptions**, not imported observations or fits.

Run: `python -m phifieldlab parity --start 3 --stop 16 --amplitude 1 --decay-length 4`.
Web tests: `cd web && npm test`. Python tests: `python -m unittest discover -s tests -v`.

## Next gates, not achieved

**QP1:** implement genuine finite *spin-1 chain* Hamiltonian (small N, full diagonalization) and compare low-energy edge properties to independent theoretical baselines. Pre-register sizes, convergence tests, and boundary-condition negative controls.

**QP2:** only with appropriately licensed, numerically available paper data or independent observations, compare predictions and failures without fitting and scoring on the same sample. Data availability in the paper says data are available from the corresponding author; do not fabricate digitized spectra.

**QP3:** superconducting bath / YSR physics needs a physically specified additional Hamiltonian and specialist validation. No fabricated spectra. Any optional NBG comparison is a separate falsifiable proposal, not a validation result.

**Ledger Above Ego:** keep negative controls and observed/model provenance separate.
