"""QP5 finite spin-1 Schmidt spectrum and entanglement controls.

Computes finite bipartite eigenstate entanglement from the unchanged QP1
Hamiltonian + QP3 anisotropy. SIMULATED / authority NONE.
No thermodynamic SPT invariant, measured entanglement, or neural weights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh

from .spin_chain import _basis, sector_hamiltonian
from .qp3 import LENGTHS, ANISOTROPY

PROTOCOL = "PHIFIELD_QP5_FINITE_SCHMIDT_AUDIT_V1"
BOUNDS = ("open", "periodic")
TOLERANCE = 1e-7


def _validate(n: int, d: int, boundary: str, cut: int):
    # Validation MUST be outside memoized code: 1 and 1.0 share an lru key.
    if type(n) is not int or n not in LENGTHS:
        raise ValueError("N must be 4, 6 or 8")
    if type(d) is not int or d not in ANISOTROPY:
        raise ValueError("D/J must be 0, 1, 4 or 12")
    if type(boundary) is not str or boundary not in BOUNDS:
        raise ValueError("boundary must be open or periodic")
    if type(cut) is not int or cut not in (1, n//2):
        raise ValueError("cut must be one site or the center")


def _ternary_index(state) -> int:
    """Spin product basis (-1,0,1) maps to digit (0,1,2)."""
    idx = 0
    for m in state:
        idx = 3*idx + int(m) + 1
    return idx


@lru_cache(maxsize=24)
def _ground(n: int, d: int, boundary: str):
    basis = np.asarray(_basis(n, 0), dtype=np.int8)
    h = sector_hamiltonian(n, 0, coupling=1., boundary=boundary)
    occupation = np.square(basis.astype(float)).sum(axis=1)
    h = h + diags(float(d)*occupation, offsets=0, format="csr")
    if h.shape[0] <= 24:
        energies, vectors = np.linalg.eigh(h.toarray())
        energy, psi = float(energies[0]), vectors[:, 0]
    else:
        gen = np.random.default_rng(
            369_500 + n*101 + d*13 + (1 if boundary=="periodic" else 0))
        energies, vectors = eigsh(
            h, k=1, which="SA", v0=gen.standard_normal(h.shape[0]),
            tol=1e-12, maxiter=20000)
        energy, psi = float(energies[0]), vectors[:, 0]
    psi = np.asarray(psi, dtype=float)
    residual = float(np.linalg.norm(h@psi-energy*psi))
    norm = float(np.dot(psi, psi))
    if not np.isfinite(residual) or residual > TOLERANCE or abs(norm-1.)>1e-9:
        raise ArithmeticError("ground eigenvector residual or norm unacceptable")
    return energy, psi, residual


@lru_cache(maxsize=48)
def _audit_cached(n: int, d: int, boundary: str, cut: int) -> dict:
    energy, psi, residual = _ground(n,d,boundary)
    states = _basis(n,0)
    matrix = np.zeros((3**cut,3**(n-cut)),dtype=float)
    for idx,state in enumerate(states):
        i = _ternary_index(state[:cut])
        j = _ternary_index(state[cut:])
        matrix[i,j] = psi[idx]
    singular = np.linalg.svd(matrix, compute_uv=False)
    probabilities = np.sort(np.square(singular))[::-1]
    if abs(float(probabilities.sum())-1.)>1e-9:
        raise ArithmeticError("Schmidt probabilities do not normalize")
    if np.any(probabilities < -1e-12):
        raise ArithmeticError("negative Schmidt probability")
    nonzero = probabilities[probabilities > 1e-15]
    entropy = float(-np.sum(nonzero*np.log(nonzero)))
    purity = float(np.dot(probabilities,probabilities))
    p0,p1 = float(probabilities[0]),float(probabilities[1])
    if not 0<=purity<=1.+1e-9 or entropy < -1e-9:
        raise ArithmeticError("invalid reduced-state statistics")
    spectrum = [round(float(q),10) for q in probabilities[:6]]
    spectrum += [0.]*max(0,6-len(spectrum))
    return {
        "n":n,"d_over_j":d,"boundary":boundary,
        "magnetization_sector":0,"cut_after_site":cut,
        "left_dimension":3**cut,"right_dimension":3**(n-cut),
        "ground_energy_m0":round(energy,10),
        "entropy_von_neumann_nats":round(entropy,9),
        "purity":round(purity,9),
        "largest_schmidt_probability":round(p0,9),
        "schmidt_pair_split":round(p0-p1,9),
        "schmidt_probabilities_top6":spectrum,
        "eigenpair_residual":residual,
        "probability_trace":round(float(probabilities.sum()),10),
        "kind":"FINITE_M0_BIPARTITE_REDUCED_STATE",
    }


def audit(n: int, d: int, boundary: str, cut: int) -> dict:
    _validate(n,d,boundary,cut)
    return _audit_cached(n,d,boundary,cut)


@lru_cache(maxsize=1)
def reference() -> dict:
    rows=[audit(n,d,boundary,cut)
          for n in LENGTHS
          for boundary in BOUNDS
          for d in ANISOTROPY
          for cut in (1,n//2)]
    return {
        "protocol":PROTOCOL,"origin":"SIMULATED","authority":"NONE",
        "attested":False,
        "data_kind":"FINITE_EIGENSTATE_ENTANGLEMENT_NOT_LAB_OBSERVATION",
        "model":"Spin-1, J sum Si dot S(i+1) + D sum (Sz_i)^2, J=1",
        "state":"lowest M=0 eigenstate",
        "entropy_units":"nats (natural logarithm)",
        "n_values":list(LENGTHS),"d_values":list(ANISOTROPY),
        "boundaries":list(BOUNDS),
        "cut_policy":"A first-site cut and a central cut; contiguous sites 0..cut-1 | cut..N-1",
        "rows":rows,
        "caveats":[
            "Finite Schmidt probabilities do NOT establish a symmetry-protected Haldane phase.",
            "Schmidt pair splitting at small N is not a protected-degeneracy certificate.",
            "A periodic bipartition severs TWO bonds; an open-chain cut severs ONE.",
            "D=12 favors a simple product-like state but is not a proven thermodynamic phase.",
            "The lowest finite M=0 sector eigenstate is used; no finite-size extrapolation.",
            "No measurement, superconductivity, YSR spectra, quantum hardware, or neural model training."
        ]
    }


def canonical_bytes(payload):
    return (json.dumps(payload,sort_keys=True,indent=2,allow_nan=False)+"\n").encode("utf-8")


def write_reference(out: Path):
    out=Path(out);raw=canonical_bytes(reference())
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("xb") as fp:
        fp.write(raw)
    return {"path":str(out),"sha256":hashlib.sha256(raw).hexdigest(),
            "protocol":PROTOCOL,"origin":"SIMULATED","authority":"NONE"}


def _strict_compare(expected,observed,path="root"):
    if type(expected)!=type(observed):
        raise ValueError("type mismatch: "+path)
    if isinstance(expected,dict):
        if set(expected)!=set(observed):
            raise ValueError("schema mismatch: "+path)
        for k in expected:
            _strict_compare(expected[k],observed[k],path+"/"+str(k))
    elif isinstance(expected,list):
        if len(expected)!=len(observed):
            raise ValueError("length mismatch: "+path)
        for i,(x,y) in enumerate(zip(expected,observed)):
            _strict_compare(x,y,path+"/"+str(i))
    elif isinstance(expected,float):
        if not np.isfinite(observed) or abs(expected-observed)>TOLERANCE:
            raise ValueError("numeric mismatch: "+path)
    elif expected!=observed:
        raise ValueError("metadata mismatch: "+path)


def verify_reference(out: Path):
    out=Path(out);raw=out.read_bytes()
    observed=json.loads(raw)
    _strict_compare(reference(),observed)
    # Cross-check against QP4's independently computed M0 energies.
    from .qp4 import spectrum
    for row in observed["rows"]:
        model=spectrum(row["n"],row["d_over_j"],row["boundary"])
        if abs(model["lowest_m0_energy"]-row["ground_energy_m0"])>TOLERANCE:
            raise ValueError("QP4 energy cross-check mismatch")
    return {"ok":True,"protocol":PROTOCOL,"origin":"SIMULATED",
            "authority":"NONE","attested":False,"rows":len(observed["rows"]),
            "sha256":hashlib.sha256(raw).hexdigest(),"tolerance":TOLERANCE}


def main():
    p=argparse.ArgumentParser(description="QP5 finite Schmidt entanglement audit")
    subs=p.add_subparsers(dest="action",required=True)
    subs.add_parser("show")
    w=subs.add_parser("write");w.add_argument("--out",type=Path,required=True)
    v=subs.add_parser("verify");v.add_argument("--file",type=Path,required=True)
    args=p.parse_args()
    if args.action=="show":
        print(json.dumps(reference(),indent=2))
    elif args.action=="write":
        print(json.dumps(write_reference(args.out),indent=2))
    else:
        print(json.dumps(verify_reference(args.file),indent=2))


if __name__=="__main__":
    main()
