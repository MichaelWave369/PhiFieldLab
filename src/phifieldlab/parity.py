"""QP0: exact 4x4 diagonalization of a two-spin-1/2 exchange TOY.

No superconducting bath, YSR solver, spin-1 bulk chain, or experimental fit.
Every result is SIMULATED and carries authority NONE.
"""
from __future__ import annotations

import math
import numpy as np

PROTOCOL = "PHIFIELD_QP0_EDGE_EXCHANGE_V1"
SX = np.array([[0., 1.], [1., 0.]], dtype=complex) / 2
SY = np.array([[0., -1j], [1j, 0.]], dtype=complex) / 2
SZ = np.diag([.5, -.5]).astype(complex)
I2 = np.eye(2, dtype=complex)
DOT = sum(np.kron(s, s) for s in (SX, SY, SZ))
TOTAL_S2 = 1.5 * np.eye(4) + 2 * DOT


def edge_spectrum(n: int, amplitude: float = 1., decay_length: float = 4.,
                  parity_blind: bool = False) -> dict:
    """Compute ground-state total spin from an explicitly diagonalized Hamiltonian."""
    if isinstance(n, bool) or not isinstance(n, int) or not 2 <= n <= 100:
        raise ValueError("n must be an integer in [2, 100]")
    for value, label in ((amplitude, "amplitude"), (decay_length, "decay_length")):
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{label} must be positive and finite")
    magnitude = amplitude * math.exp(-(n - 2) / decay_length)
    exchange = (-1 if n % 2 and not parity_blind else 1) * magnitude
    h = exchange * DOT
    energies, vectors = np.linalg.eigh(h)
    ground = vectors[:, 0]
    s2 = float(np.real(np.vdot(ground, TOTAL_S2 @ ground)))
    # S(S+1) equals 0 for singlet, 2 for triplet, even when triplet is degenerate.
    spin = 0 if abs(s2) < 1e-9 else 1 if abs(s2 - 2.) < 1e-9 else None
    if spin is None:
        raise ArithmeticError("ground spin invariant failed")
    return {
        "protocol": PROTOCOL,
        "origin": "SIMULATED", "authority": "NONE",
        "n": n, "parity": "ODD" if n % 2 else "EVEN",
        "model": "PARITY_BLIND_NEGATIVE_CONTROL" if parity_blind else "SIGN_ALTERNATING_TOY",
        "exchange": exchange,
        "eigenvalues": [float(x) for x in energies],
        "ground_total_spin": spin,
        "excitation_gap": abs(exchange),
    }


def ladder(start: int = 3, stop: int = 16, amplitude: float = 1.,
           decay_length: float = 4., parity_blind: bool = False) -> list[dict]:
    if isinstance(start, bool) or isinstance(stop, bool) or not isinstance(start, int) or not isinstance(stop, int) or start < 2 or stop > 100 or start > stop:
        raise ValueError("invalid range")
    return [edge_spectrum(n, amplitude, decay_length, parity_blind) for n in range(start, stop + 1)]
