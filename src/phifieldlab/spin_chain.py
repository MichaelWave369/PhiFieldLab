"""QP1: exact finite spin-1 Heisenberg chain sectors (not superconducting spectroscopy).

Outputs are SIMULATED with authority NONE; no experimental fit or NBG validation.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import product
import json
import math
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import eigsh

PROTOCOL = "PHIFIELD_QP1_SPIN1_HEISENBERG_V1"
TOL = 1e-7


@lru_cache(maxsize=40)
def _basis(n: int, magnetization: int) -> tuple[tuple[int, ...], ...]:
    return tuple(s for s in product((-1, 0, 1), repeat=n) if sum(s) == magnetization)


def sector_hamiltonian(n: int, magnetization: int = 0, coupling: float = 1.,
                       boundary: str = "open"):
    """H=J sum(Sz_i Sz_j + (S+_i S-_j + S-_i S+_j)/2), restricted to total Sz."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 2 or n > 8:
        raise ValueError("n must be an integer from 2 to 8")
    if isinstance(magnetization, bool) or not isinstance(magnetization, int) or abs(magnetization) > n:
        raise ValueError("invalid magnetization sector")
    if not math.isfinite(coupling) or coupling <= 0:
        raise ValueError("coupling must be finite and positive")
    if boundary not in ("open", "periodic"):
        raise ValueError("boundary must be open or periodic")
    if boundary == "periodic" and n < 3:
        raise ValueError("periodic N=2 would double count the same bond")
    states = _basis(n, magnetization)
    index = {s: i for i, s in enumerate(states)}
    bonds = [(i, i + 1) for i in range(n - 1)]
    if boundary == "periodic":
        bonds.append((n - 1, 0))
    rows, cols, values = [], [], []
    for col, state in enumerate(states):
        diag = 0.
        for i, j in bonds:
            mi, mj = state[i], state[j]
            diag += coupling * mi * mj
            for sign in (-1, 1):
                new_i, new_j = mi + sign, mj - sign
                if abs(new_i) > 1 or abs(new_j) > 1:
                    continue
                factor = .5 * coupling * math.sqrt(2 - mi * new_i) * math.sqrt(2 - mj * new_j)
                target = list(state)
                target[i], target[j] = new_i, new_j
                rows.append(index[tuple(target)])
                cols.append(col)
                values.append(factor)
        rows.append(col)
        cols.append(col)
        values.append(diag)
    return coo_matrix((values, (rows, cols)), shape=(len(states), len(states))).tocsr()


def _lowest(h, n: int, m: int, boundary: str, count: int = 4) -> list[float]:
    size = h.shape[0]
    if size <= max(12, count + 1):
        vals = np.linalg.eigvalsh(h.toarray())[:count]
    else:
        seed = 36900 + 100 * n + 7 * m + (1 if boundary == "periodic" else 0)
        rng = np.random.default_rng(seed)
        vals = eigsh(h, k=min(count, size - 2), which="SA", return_eigenvectors=False,
                     v0=rng.standard_normal(size), tol=1e-11, maxiter=15000)
    return [float(v) for v in sorted(vals)]


def chain_spectrum(n: int, boundary: str = "open", coupling: float = 1.) -> dict:
    """Infer total spin from degenerate lowest energies across M=0,1,2 sectors.

    These quantum multiplets are computed: odd/even parity is NOT given to H.
    """
    levels, dims = {}, {}
    for m in (0, 1, 2):
        h = sector_hamiltonian(n, m, coupling, boundary)
        dims[str(m)] = h.shape[0]
        levels[str(m)] = _lowest(h, n, m, boundary)
    e0 = levels["0"][0]
    spin = max(m for m in (0, 1, 2) if abs(levels[str(m)][0] - e0) < TOL)
    excited = sorted({round(v - e0, 10) for values in levels.values()
                      for v in values if v > e0 + TOL})
    if not excited:
        raise ArithmeticError("no excited level resolved")
    return {
        "protocol": PROTOCOL, "origin": "SIMULATED", "authority": "NONE",
        "n": n, "boundary": boundary, "coupling": coupling,
        "ground_total_spin": spin, "ground_energy": round(e0, 10),
        "lowest_excitation_gap": excited[0],
        "sector_minima": {m: round(values[0], 10) for m, values in levels.items()},
        "sector_low_energies": {m: [round(v, 10) for v in values] for m, values in levels.items()},
        "sector_dimensions": dims,
        "limitations": "Finite Heisenberg chain; no YSR spectra or superconductivity."
    }


def reference_ladder(start: int = 3, stop: int = 8) -> dict:
    if any(isinstance(x, bool) or not isinstance(x, int) for x in (start, stop)) or not 3 <= start <= stop <= 8:
        raise ValueError("reference range must be in [3,8]")
    return {
        "protocol": PROTOCOL, "origin": "SIMULATED", "authority": "NONE", "attested": False,
        "data_kind": "COMPUTED_MODEL_OUTPUT_NOT_LAB_OBSERVATION",
        "hamiltonian": "H = J sum_(i,j bonds) S_i dot S_j, with spin S=1 and J=1",
        "method": "Sparse eigensolver in magnetization sectors; finite spin-1 Heisenberg model",
        "source_paper_doi": "10.1038/s41586-026-11117-y",
        "range": [start, stop],
        "open": [chain_spectrum(n, "open") for n in range(start, stop + 1)],
        "periodic_negative_control": [chain_spectrum(n, "periodic") for n in range(start, stop + 1)],
    }


def browser_reference(start: int = 3, stop: int = 8) -> dict:
    """Compact source-controlled projection. Its receipt is *not* attestation."""
    data = reference_ladder(start, stop)
    keep = ("protocol", "origin", "authority", "n", "boundary", "coupling",
            "ground_total_spin", "ground_energy", "lowest_excitation_gap",
            "sector_minima", "sector_dimensions")
    for boundary in ("open", "periodic_negative_control"):
        data[boundary] = [{key: row[key] for key in keep} for row in data[boundary]]
    return data


def write_reference(path: Path, start: int = 3, stop: int = 8) -> None:
    """Never overwrite frozen output; write separate file for an audit replay."""
    payload = browser_reference(start, stop)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
