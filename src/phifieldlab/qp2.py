"""QP2 finite-spin-1 edge fingerprints. SIMULATED / authority NONE.

Reuses QP1's frozen Hamiltonian. No superconducting coupling, YSR spectrum,
thermodynamic Haldane invariant, or trained AI model is computed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import eigsh

from .spin_chain import _basis, sector_hamiltonian

PROTOCOL = "PHIFIELD_QP2_EDGE_FINGERPRINTS_V1"
ORIGIN = "SIMULATED"
AUTHORITY = "NONE"
ODD = (3, 5, 7)
EVEN = (4, 6, 8)


def lowest_state(n: int, magnetization: int, boundary: str):
    """Deterministic-start lowest sector eigenpair with a numerical residual."""
    if n not in range(3, 9) or magnetization not in (0, 1):
        raise ValueError("only 3<=N<=8 and M in {0,1} are admitted")
    if boundary not in ("open", "periodic"):
        raise ValueError("boundary must be open or periodic")
    h = sector_hamiltonian(n, magnetization, boundary=boundary)
    if h.shape[0] <= 24:
        vals, vectors = np.linalg.eigh(h.toarray())
        energy, psi = float(vals[0]), vectors[:, 0]
    else:
        v0 = np.random.default_rng(369_000 + 19*n + 7*magnetization
                                    + (1 if boundary == "periodic" else 0)).standard_normal(h.shape[0])
        vals, vectors = eigsh(h, k=1, which="SA", v0=v0, tol=1e-12, maxiter=15000)
        energy, psi = float(vals[0]), vectors[:, 0]
    psi = np.asarray(psi, dtype=np.float64)
    norm = float(np.dot(psi, psi))
    if abs(norm - 1.0) > 1e-8:
        raise ArithmeticError("eigenstate not normalized")
    residual = float(np.linalg.norm(h @ psi - energy*psi))
    if residual > 1e-7:
        raise ArithmeticError("eigensolver residual exceeds tolerance")
    return energy, psi, residual


def edge_profile(n: int):
    """Odd open chain, M=1 lowest-state local Sz expectations."""
    if n not in ODD:
        raise ValueError("edge profile requires odd N = 3,5,7")
    energy, psi, residual = lowest_state(n, 1, "open")
    basis = np.asarray(_basis(n, 1), dtype=np.float64)
    magnetization = np.square(psi) @ basis
    if abs(float(magnetization.sum()) - 1.0) > 1e-8:
        raise ArithmeticError("total M=1 not conserved")
    if np.max(np.abs(magnetization - magnetization[::-1])) > 1e-7:
        raise ArithmeticError("reflection symmetry not resolved")
    absolute = np.abs(magnetization)
    fraction = float((absolute[0] + absolute[-1]) / absolute.sum())
    return {
        "n": n, "boundary": "open", "magnetization_sector": 1,
        "lowest_sector_energy": round(energy, 10),
        "site_magnetization": [round(float(x), 9) for x in magnetization],
        "edge_absolute_fraction": round(fraction, 9),
        "uniform_fraction_reference": round(2/n, 9),
        "eigenpair_residual": residual,
        "interpretation": "Finite M=1 site expectations; not a direct fractional-edge-spin measurement."
    }


def string_correlator(n: int, boundary: str):
    """Even chain M=0: longitudinal nonlocal string versus two-point control.

    Deliberately use (i,j)=(0,N-2), not endpoints (0,N-1): in fixed M=0
    the endpoint string operator collapses to the two-point operator.
    """
    if n not in EVEN:
        raise ValueError("string probe requires even N = 4,6,8")
    energy, psi, residual = lowest_state(n, 0, boundary)
    basis = np.asarray(_basis(n, 0), dtype=np.int8)
    weight = np.square(psi)
    i, j = 0, n-2
    z = basis[:,i].astype(np.float64)*basis[:,j].astype(np.float64)
    parity = np.where(np.abs(basis[:,i+1:j]).sum(axis=1)%2 == 0, 1., -1.)
    string = -float(np.dot(weight, z*parity))
    local = -float(np.dot(weight, z))
    # In M=0, the endpoint string has the same value as the endpoint
    # two-point correlator. This is a trap for naïve interpretations.
    endz = basis[:,0].astype(np.float64)*basis[:,-1].astype(np.float64)
    endparity = np.where(np.abs(basis[:,1:-1]).sum(axis=1)%2 == 0, 1., -1.)
    trivial_string = -float(np.dot(weight, endz*endparity))
    trivial_local = -float(np.dot(weight, endz))
    if abs(trivial_string-trivial_local)>1e-9:
        raise ArithmeticError("endpoint M=0 identity violated")
    return {
        "n":n, "boundary":boundary, "magnetization_sector":0,
        "lowest_sector_energy":round(energy,10), "probe_sites_zero_based":[i,j],
        "string_zz":round(string,9), "two_point_zz":round(local,9),
        "all_zero_product_state_string":0.0,
        "endpoint_string_minus_endpoint_two_point":round(trivial_string-trivial_local,12),
        "eigenpair_residual":residual,
        "interpretation":"Finite longitudinal correlation only; not proof of thermodynamic string order."
    }


def reference():
    return {
        "protocol":PROTOCOL,"origin":ORIGIN,"authority":AUTHORITY,"attested":False,
        "data_kind":"FINITE_COMPUTED_STATE_EXPECTATIONS_NOT_LAB_OBSERVATIONS",
        "chain_model":"Isotropic spin-1 nearest-neighbor antiferromagnetic Heisenberg J=1",
        "scope":"Exact/sparse sector eigenvectors, N<=8; no superconducting substrate",
        "open_odd_edge_profiles":[edge_profile(n) for n in ODD],
        "even_string_open":[string_correlator(n,"open") for n in EVEN],
        "even_string_periodic_geometry_control":[string_correlator(n,"periodic") for n in EVEN],
        "warnings":[
            "A finite nonzero string correlator is not sufficient to establish the Haldane phase.",
            "Periodic chain is a geometry comparison, NOT a null control: its string correlator can be nonzero.",
            "In a fixed M=0 sector, the full endpoint string reduces to the endpoint two-point correlator.",
            "All-zero product-state string is a trivial zero reference, not a matched Hamiltonian phase control.",
            "Site magnetization in a finite M=1 sector is not a direct observation of fractional edge spin."
        ],
    }


def canonical_bytes(payload):
    return (json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n").encode("utf-8")


def write_reference(path: Path):
    path=Path(path)
    payload=reference()
    data=canonical_bytes(payload)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("xb") as fp:
        fp.write(data)
    return {"path":str(path),"sha256":hashlib.sha256(data).hexdigest(),
            "protocol":PROTOCOL,"origin":ORIGIN,"authority":AUTHORITY}


def verify_reference(path: Path, *, tolerance=1e-7):
    saved=json.loads(Path(path).read_text(encoding="utf-8"))
    expected=reference()
    if saved.keys()!=expected.keys() or saved["protocol"]!=PROTOCOL:
        raise ValueError("reference schema mismatch")
    if saved["origin"]!=ORIGIN or saved["authority"]!=AUTHORITY or saved["attested"] is not False:
        raise ValueError("unsupported provenance claim")
    for group in ("open_odd_edge_profiles","even_string_open","even_string_periodic_geometry_control"):
        if len(saved[group])!=len(expected[group]):
            raise ValueError("reference row count mismatch")
        for old,new in zip(saved[group],expected[group]):
            if old.keys()!=new.keys():
                raise ValueError("reference row schema mismatch")
            for key in old:
                if isinstance(old[key],float) or (isinstance(old[key],list) and key=="site_magnetization"):
                    lhs = np.asarray(old[key],dtype=float)
                    rhs = np.asarray(new[key],dtype=float)
                    if not np.allclose(lhs,rhs,atol=tolerance,rtol=0):
                        raise ValueError("reference numeric mismatch: "+group+"/"+key)
                elif old[key]!=new[key]:
                    raise ValueError("reference metadata mismatch: "+group+"/"+key)
    for key in ("data_kind","chain_model","scope","warnings"):
        if saved[key]!=expected[key]:
            raise ValueError("reference metadata mismatch: "+key)
    return {"ok":True,"protocol":PROTOCOL,"origin":ORIGIN,"authority":AUTHORITY,
            "replay_tolerance":tolerance,"reference_sha256":hashlib.sha256(
                Path(path).read_bytes()).hexdigest()}


def main():
    parser=argparse.ArgumentParser(description="QP2 finite spin-chain edge fingerprints")
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("show")
    write=sub.add_parser("write")
    write.add_argument("--out",type=Path,required=True)
    verify=sub.add_parser("verify")
    verify.add_argument("--file",type=Path,required=True)
    args=parser.parse_args()
    if args.command=="show":print(json.dumps(reference(),indent=2))
    elif args.command=="write":print(json.dumps(write_reference(args.out),indent=2))
    else:print(json.dumps(verify_reference(args.file),indent=2))


if __name__=="__main__":
    main()
