# QP2 · Finite spin-1 edge fingerprints (frozen candidate protocol)

**Protocol:** PHIFIELD_QP2_EDGE_FINGERPRINTS_V1  
**Evidence origin:** SIMULATED  
**Scientific authority:** NONE  
**Independent attestation:** false

QP2 extends QP1's isotropic nearest-neighbor antiferromagnetic spin-1 Heisenberg Hamiltonian with new **computed observables**, not a different speculative Hamiltonian. No NBG correspondence, superconductivity, proximity effect, tunneling spectrum, Yu–Shiba–Rusinov measurement, or thermodynamic Haldane-phase certification is claimed. No AI model weights are trained in QP2.

## The predeclared questions

1. In the lowest **M=+1 magnetization sector** of odd open chains N=3,5,7, what is the **local** site-by-site expectation \`<Sz_i>\`? Is its absolute weight concentrated at endpoints relative to a *uniform-density reference* \`2/N\`?
2. In the lowest **M=0 sector** of even chains N=4,6,8, what does the finite longitudinal nonlocal string correlator look like for open chains and periodic rings?
3. Can we expose interpretation traps using direct two-point correlators and a trivial all-zero product-state reference?

These are computed eigenstate properties of the *short finite model only*, not the long-chain classification.

## Method

Use the existing QP1 \`sector_hamiltonian\` and \`_basis\`. Construct the lowest eigenpair in one selected magnetization sector using dense \`eigh\` for small matrices and deterministic-start sparse \`eigsh\` for larger ones. Require unit-norm eigenvectors and \`||Hψ-Eψ|| < 10^-7\`.

Odd open chains: take the lowest \`M=1\` eigenvector and evaluate each \`<Sz_i>\` as a diagonal expectation over its probability amplitudes. Assert \`sum_i <Sz_i> = 1\` and mirror symmetry. Report \`(|m_0|+|m_(N-1)|)/sum_i |m_i|\` alongside the **illustrative** \`2/N\` uniform fraction. The latter is not a physical null hypothesis or an estimate of a fractional spin.

Even chains: take the lowest \`M=0\` eigenvector under open and periodic boundary conditions and compute

\`\`\`text
O_z(i,j) = - < Sz_i [exp(i π Σ_{k=i+1}^{j-1} Sz_k)] Sz_j >
C_z(i,j) = - < Sz_i Sz_j >
\`\`\`

Use **i=0 and j=N-2 (zero-based)**. The diagonal string factor is \`(-1)^{number of sites between i and j with |Sz|=1}\`. Use the same pair for both observables and both boundaries. The correlators are dimensionless model expectations.

### A built-in false-positive trap

In the fixed \`M=0\` sector, using endpoints \`i=0,j=N-1\` makes the longitudinal string factor **always +1 whenever endpoint Sz product is nonzero**, so that endpoint *string correlator equals the local two-point correlator*. That superficial result can be mistakenly interpreted as independent nonlocal order. QP2 explicitly verifies this equality and deliberately uses a non-endpoint pair instead.

### Controls and limits

- **Periodic ring:** geometry comparison with no exposed ends. Its longitudinal string correlator **need not vanish**; never label it a null control.
- **Two-point expectation:** distinguishes the nonlocal string insertion from an ordinary pair correlation for the same site pair.
- **All-zero product state:** its string correlator is identically zero; a deliberately *trivial* reference, **not** the ground state of the same Hamiltonian.
- **Parity and sector conservation:** reuse QP1's unmodified physics and compare calculated sector energies with QP1 minima; tests enforce magnetization conservation and reflection for open odd chains.
- **Finite-size warning:** nonzero string correlations and apparent edge-weight enhancement are not sufficient proof of symmetry-protected topological order, fractional edge spin, or the infinite-size Haldane phase. N=3–8 only.
- **Numerical reproducibility:** compare replay values within \`10^-7\`; the eigenvector global sign is unobservable and does not affect these diagonal expectations.

## Acceptance gates

1. Odd N=3,5,7: normalized M=1 eigenstate, reflection-symmetric site magnetizations, sum exactly 1 within tolerance; expose absolute edge fractions.
2. Even N=4,6,8: evaluate both boundaries and confirm same-pair string and two-point correlations differ.
3. Demonstrate *periodic nonzero string correlations*, not a manufactured disappearing-signal result.
4. Demonstrate the M=0 **endpoint equality trap**.
5. All reference output marked \`SIMULATED / authority NONE / attested false\`.
6. Read-only browser artifact verified by independent Python recalculation on CI; no live Python executed in browser.
7. No modification to QP1's frozen computed JSON or QP0/E0/E1 experiments.

## Commands

\`\`\`bash
python -m pip install -e ".[spinchain]"
python -m phifieldlab.qp2 show
python -m phifieldlab.qp2 write --out artifacts/local/qp2-replay.json
python -m phifieldlab.qp2 verify --file artifacts/local/qp2-replay.json
python -m unittest discover -s tests -p test_qp2.py -v
\`\`\`

\`write\` refuses to replace an existing file. For the source-controlled browser reference, \`verify\` recomputes the same observables from QP1 and compares within tolerance. An artifact hash establishes consistency, not authenticity of physical observations.

**Next gates:** compare multiple finite sizes and operators, inspect degeneracy and quantum-state correlations, consider genuinely matched trivial reference Hamiltonians and finite-size scaling, and only later attempt independent external data comparisons with proper permissions and interpretation.

**Ledger Above Ego. No shortcut from a finite correlation to a claimed phase.**
