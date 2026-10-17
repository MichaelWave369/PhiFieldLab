"""QP3: matched finite spin-1 Hamiltonian anisotropy controls.

SIMULATED / authority NONE. This compares the same finite-chain model,
same observable, same N, and same open boundaries with D * sum_i (Sz_i)^2.
No thermodynamic phase transition or experimental observation is claimed.
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

PROTOCOL = "PHIFIELD_QP3_ANISOTROPY_CONTROL_V1"
ORIGIN = "SIMULATED"
AUTHORITY = "NONE"
LENGTHS = (4, 6, 8)
ANISOTROPY = (0, 1, 4, 12)


def fingerprint(n: int, d: int) -> dict:
    """Validate input types before accessing any cached numerical result."""
    if type(n) is not int or n not in LENGTHS:
        raise ValueError("N must be exactly 4, 6 or 8")
    if type(d) is not int or d not in ANISOTROPY:
        raise ValueError("D must be exactly one of 0, 1, 4, 12")
    return _fingerprint_cached(n, d)


@lru_cache(maxsize=20)
def _fingerprint_cached(n: int, d: int) -> dict:
    """Evaluate an already validated finite M=0 eigenstate."""
    # QP1's Hamiltonian and basis ordering are unchanged.
    basis = np.asarray(_basis(n, 0), dtype=np.int8)
    base = sector_hamiltonian(n, 0, 1.0, "open")
    occupancy = np.square(basis.astype(np.float64)).sum(axis=1)
    h = base + diags(float(d) * occupancy, offsets=0, format="csr")
    if h.shape[0] <= 24:
        energy_all, vectors = np.linalg.eigh(h.toarray())
        energy, psi = float(energy_all[0]), vectors[:, 0]
    else:
        rng = np.random.default_rng(369_300 + 101*n + 17*d)
        vals, vectors = eigsh(h, k=1, which="SA",
                             v0=rng.standard_normal(h.shape[0]),
                             tol=1e-12, maxiter=18000)
        energy, psi = float(vals[0]), vectors[:, 0]
    psi = np.asarray(psi, dtype=np.float64)
    weights = np.square(psi)
    residual = float(np.linalg.norm(h @ psi - energy*psi))
    if abs(float(weights.sum())-1.0) > 1e-9 or residual > 1e-7:
        raise ArithmeticError("eigenpair norm or residual failed")

    # Same fixed pair as QP2. Full endpoints would be a misleading
    # degeneracy of string and two-point values in M=0.
    i, j = 0, n-2
    zz = basis[:, i].astype(float) * basis[:, j].astype(float)
    parity = np.where(np.sum(np.abs(basis[:, i+1:j]), axis=1) % 2 == 0, 1., -1.)
    string_zz = -float(np.dot(weights, zz * parity))
    two_point_zz = -float(np.dot(weights, zz))
    local_sz2 = float(np.dot(weights, occupancy)/n)

    # |0,0,...,0> is an exact product reference at large positive D.
    zero_index = np.flatnonzero(np.all(basis==0, axis=1))
    if len(zero_index)!=1:
        raise AssertionError("unexpected M=0 basis / product state")
    product_overlap = float(weights[int(zero_index[0])])

    return {
        "n":n, "boundary":"open", "coupling_j":1,
        "anisotropy_d":d, "magnetization_sector":0,
        "ground_energy_sector_m0":round(energy, 10),
        "probe_sites_zero_based":[i,j],
        "string_zz":round(string_zz, 9),
        "two_point_zz":round(two_point_zz, 9),
        "mean_local_sz_squared":round(local_sz2, 9),
        "all_zero_product_overlap":round(product_overlap, 9),
        "eigenpair_residual":residual,
    }


@lru_cache(maxsize=1)
def reference() -> dict:
    rows = [fingerprint(n, d) for n in LENGTHS for d in ANISOTROPY]
    return {
        "protocol":PROTOCOL, "origin":ORIGIN,"authority":AUTHORITY,
        "attested":False,
        "data_kind":"COMPUTED_FINITE_HAMILTONIAN_NOT_LAB_OBSERVATION",
        "model":"H=J*sum_(nearest open bonds) S_i dot S_j + D*sum_i (Sz_i)^2; J=1",
        "n_values":list(LENGTHS),"d_values":list(ANISOTROPY),
        "rows":rows,
        "caveats":[
            "Changing D changes the Hamiltonian, not the measured environment.",
            "D/J >= 4 is a high positive anisotropy comparison, not an independently certified phase.",
            "Finite N<=8 cannot establish a thermodynamic critical point or Haldane phase.",
            "The nonendpoint string and two-point probes use exactly the same sites, i=0 and j=N-2.",
            "Overlap with |0...0> is a chosen product-state reference, not experimental fidelity.",
            "No superconducting substrate, YSR spectrum, particle experiment, or AI training is present."
        ],
    }


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+"\n").encode("utf-8")


def write_reference(path: Path) -> dict:
    path = Path(path)
    raw = canonical_bytes(reference())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        output.write(raw)
    return {"path":str(path),"sha256":hashlib.sha256(raw).hexdigest(),
            "origin":ORIGIN,"authority":AUTHORITY,"attested":False}


def _compare(expected, observed, location="", atol=1e-7):
    """Strict schema and metadata, small tolerance only for finite floats."""
    if type(expected) is not type(observed):
        raise ValueError("schema type mismatch at "+location)
    if isinstance(expected, dict):
        if set(expected)!=set(observed):
            raise ValueError("schema keys mismatch at "+location)
        for key in expected:
            _compare(expected[key],observed[key],location+"/"+str(key),atol)
    elif isinstance(expected,list):
        if len(expected)!=len(observed):
            raise ValueError("schema length mismatch at "+location)
        for i,(a,b) in enumerate(zip(expected,observed)):
            _compare(a,b,location+"/"+str(i),atol)
    elif isinstance(expected,float):
        if not np.isfinite(observed) or abs(expected-observed)>atol:
            raise ValueError("numeric mismatch at "+location)
    elif expected != observed:
        raise ValueError("metadata mismatch at "+location)


def verify_reference(path: Path) -> dict:
    raw = Path(path).read_bytes()
    observed = json.loads(raw)
    _compare(reference(),observed)
    return {"ok":True, "protocol":PROTOCOL, "origin":ORIGIN,
            "authority":AUTHORITY,"attested":False,"rows":len(observed["rows"]),
            "sha256":hashlib.sha256(raw).hexdigest(),
            "replay_tolerance":1e-7}


def main():
    parser=argparse.ArgumentParser(description="QP3 matched finite-chain Hamiltonian controls")
    subs=parser.add_subparsers(dest="command",required=True)
    subs.add_parser("show")
    writer=subs.add_parser("write");writer.add_argument("--out",type=Path,required=True)
    verifier=subs.add_parser("verify");verifier.add_argument("--file",type=Path,required=True)
    args=parser.parse_args()
    if args.command=="show":
        print(json.dumps(reference(),indent=2))
    elif args.command=="write":
        print(json.dumps(write_reference(args.out),indent=2))
    else:
        print(json.dumps(verify_reference(args.file),indent=2))


if __name__=="__main__":
    main()
