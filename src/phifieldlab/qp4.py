"""QP4 finite spin-one spectral cross-examination.

No lab data, thermodynamic-limit inference, superconductivity or AI training.
Origin SIMULATED; authority NONE. Reuse QP1 sector Hamiltonian exactly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import eigsh

from .spin_chain import sector_hamiltonian
from .qp3 import fingerprint as qp3_fingerprint, LENGTHS, ANISOTROPY

PROTOCOL = "PHIFIELD_QP4_FINITE_GAP_SPECTROSCOPY_V1"
BOUNDS = ("open", "periodic")
TOLERANCE = 1e-7


def _lowest_levels(h, n: int, m: int, d: int, boundary: str, count: int):
    size = h.shape[0]
    if size <= max(24, count + 2):
        levels = np.linalg.eigvalsh(h.toarray())[:count]
    else:
        rng = np.random.default_rng(
            369_400 + n * 1000 + m * 100 + d * 7 +
            (1 if boundary == "periodic" else 0))
        levels = eigsh(
            h, k=count, which="SA", return_eigenvectors=False,
            v0=rng.standard_normal(size), tol=1e-11, maxiter=20000)
    return [float(v) for v in sorted(levels)]


@lru_cache(maxsize=32)
def _compute_cached(n: int, d: int, boundary: str) -> dict:
    # Enumerate ALL nonnegative M sectors for the actual finite spectrum.
    # Energies at negative M are equal by spin reversal of this Hamiltonian.
    sector = {}
    for m in range(n+1):
        h = sector_hamiltonian(n, m, coupling=1., boundary=boundary)
        # The diagonal term is D * sum_j (Sz_j)^2 in the same basis.
        from .spin_chain import _basis
        from scipy.sparse import diags
        basis = np.asarray(_basis(n, m), dtype=np.int8)
        occupation = np.square(basis.astype(np.float64)).sum(axis=1)
        h = h + diags(float(d)*occupation, offsets=0, format="csr")
        sector[m] = _lowest_levels(h,n,m,d,boundary,
                                   count=2 if m==0 and h.shape[0]>1 else 1)
    ground = sector[0][0]
    for m, vals in sector.items():
        if vals[0] < ground-TOLERANCE:
            raise ArithmeticError(f"lowest state is outside M=0: M={m}")

    candidate = []
    if len(sector[0])>1 and sector[0][1]>ground+TOLERANCE:
        candidate.append(("M=0",sector[0][1]-ground))
    for m in range(1,n+1):
        if sector[m][0]>ground+TOLERANCE:
            candidate.append((f"|M|={m}",sector[m][0]-ground))
        elif abs(sector[m][0]-ground)<=TOLERANCE:
            raise ArithmeticError("unexpected degenerate ground state across sectors")
    first_sector,gap = min(candidate,key=lambda x:x[1])
    magnetic=min(sector[m][0]-ground for m in range(1,n+1))
    neutral = sector[0][1]-ground
    result = {
        "n":n,"d_over_j":d,"boundary":boundary,"j":1,
        "lowest_m0_energy":round(ground,10),
        "global_ground_is_m0":True,
        "first_excitation_gap":round(float(gap),9),
        "first_excitation_sector":first_sector,
        "neutral_m0_gap":round(float(neutral),9),
        "magnetization_changing_gap":round(float(magnetic),9),
        "magnetization_sector_minima":{
            str(m):round(sector[m][0],10) for m in range(n+1)},
        "interpretation":"Finite many-body energy differences (units J); not a measured or thermodynamic bulk gap."
    }
    return result


def spectrum(n: int, d: int, boundary: str):
    # Validate BEFORE hitting cached numerical values. Python caches treat
    # integer 1 and float 1.0 as equal keys otherwise.
    if type(n) is not int or n not in LENGTHS:
        raise ValueError("N must be 4,6,8")
    if type(d) is not int or d not in ANISOTROPY:
        raise ValueError("D/J must be 0,1,4,12")
    if type(boundary) is not str or boundary not in BOUNDS:
        raise ValueError("boundary must be open or periodic")
    return _compute_cached(n,d,boundary)


@lru_cache(maxsize=1)
def reference():
    rows = [spectrum(n,d,boundary)
            for n in LENGTHS for boundary in BOUNDS for d in ANISOTROPY]
    return {
        "protocol":PROTOCOL,"origin":"SIMULATED","authority":"NONE","attested":False,
        "data_kind":"FINITE_NUMERICAL_SPECTRUM_NOT_LAB_SPECTROSCOPY",
        "model":"Spin-1 H=J sum S_i dot S_(i+1) + D sum (Sz_i)^2; J=1",
        "n_values":list(LENGTHS),"d_values":list(ANISOTROPY),
        "boundaries":list(BOUNDS),"rows":rows,
        "caveats":[
            "Only finite even N=4,6,8; no thermodynamic critical point is inferred.",
            "The first finite-level excitation gap is NOT a measured Haldane bulk gap.",
            "A minimum among four D values is NOT a phase-transition location.",
            "Open and periodic geometries have different finite-size spectra.",
            "All M>=0 sectors are checked; spin inversion makes M<0 redundant.",
            "At D>0 SU(2) total spin labels do not generally apply.",
            "No empirical quantum device, superconductivity, YSR spectrum or learned neural weights."
        ]
    }


def canonical_bytes(value):
    return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n").encode("utf-8")


def write_reference(path: Path):
    path=Path(path)
    raw=canonical_bytes(reference())
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("xb") as handle:
        handle.write(raw)
    return {"file":str(path),"sha256":hashlib.sha256(raw).hexdigest(),
            "protocol":PROTOCOL,"origin":"SIMULATED","authority":"NONE"}


def _compare(a,b,where="root"):
    if type(a) is not type(b):
        raise ValueError("type mismatch: "+where)
    if isinstance(a,dict):
        if set(a)!=set(b):
            raise ValueError("schema mismatch: "+where)
        for key in a:
            _compare(a[key],b[key],where+"/"+str(key))
    elif isinstance(a,list):
        if len(a)!=len(b):
            raise ValueError("length mismatch: "+where)
        for i,(v,w) in enumerate(zip(a,b)):
            _compare(v,w,where+"/"+str(i))
    elif isinstance(a,float):
        if not np.isfinite(b) or abs(a-b)>TOLERANCE:
            raise ValueError("numeric mismatch: "+where)
    elif a!=b:
        raise ValueError("metadata mismatch: "+where)


def verify_reference(path: Path):
    contents=Path(path).read_bytes()
    observed=json.loads(contents)
    _compare(reference(),observed)
    # Independent QP3 consistency gate for every open-geometry grid point.
    for row in observed["rows"]:
        if row["boundary"]=="open":
            qp3=qp3_fingerprint(row["n"],row["d_over_j"])
            if abs(qp3["ground_energy_sector_m0"]-row["lowest_m0_energy"])>TOLERANCE:
                raise ValueError("QP3 ground-energy cross-check mismatch")
    return {"ok":True,"protocol":PROTOCOL,"origin":"SIMULATED",
            "authority":"NONE","attested":False,"rows":len(observed["rows"]),
            "sha256":hashlib.sha256(contents).hexdigest()}


def main():
    parser=argparse.ArgumentParser(description="QP4 finite spectrum cross-examination")
    subs=parser.add_subparsers(dest="action",required=True)
    subs.add_parser("show")
    w=subs.add_parser("write");w.add_argument("--out",required=True,type=Path)
    v=subs.add_parser("verify");v.add_argument("--file",required=True,type=Path)
    args=parser.parse_args()
    if args.action=="show":
        print(json.dumps(reference(),indent=2))
    elif args.action=="write":
        print(json.dumps(write_reference(args.out),indent=2))
    else:
        print(json.dumps(verify_reference(args.file),indent=2))


if __name__=="__main__":
    main()
