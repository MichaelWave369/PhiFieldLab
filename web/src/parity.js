/**
 * QP0: transparent two-edge-spin exchange toy, NOT a YSR or Haldane-chain solver.
 * Energies in arbitrary model units; no experimental fit.
 */
export const QP0_PROTOCOL = 'PHIFIELD_QP0_EDGE_EXCHANGE_V1';
const validNumber = (value, name) => {
  if (!Number.isFinite(value) || value <= 0) throw new RangeError(name + ' must be positive and finite');
};
export function edgeSpectrum(n, amplitude = 1, decayLength = 4, parityBlind = false) {
  if (!Number.isInteger(n) || n < 2 || n > 100) throw new RangeError('n must be an integer from 2 to 100');
  validNumber(amplitude, 'amplitude');
  validNumber(decayLength, 'decayLength');
  const odd = n % 2 !== 0;
  // H = J_eff s_L dot s_R. Positive J favours the singlet.
  // A sign-alternating J is a model assumption, not a fit or deduction from the Nature data.
  const magnitude = amplitude * Math.exp(-(n - 2) / decayLength);
  const J = (odd && !parityBlind ? -1 : 1) * magnitude;
  const singlet = -3 * J / 4;
  const triplet = J / 4;
  return {
    protocol: QP0_PROTOCOL,
    origin: 'SIMULATED',
    authority: 'NONE',
    n, parity: odd ? 'ODD' : 'EVEN',
    model: parityBlind ? 'PARITY_BLIND_NEGATIVE_CONTROL' : 'SIGN_ALTERNATING_TOY',
    exchange: J,
    singlet_energy: singlet,
    triplet_energy: triplet,
    eigenvalues: [singlet, triplet, triplet, triplet].sort((a, b) => a - b),
    ground_total_spin: J > 0 ? 0 : 1,
    excitation_gap: Math.abs(J)
  };
}
export function parityLadder(from = 3, to = 16, amplitude = 1, decayLength = 4, parityBlind = false) {
  if (!Number.isInteger(from) || !Number.isInteger(to) || from < 2 || to > 100 || from > to)
    throw new RangeError('invalid ladder endpoints');
  return Array.from({ length: to - from + 1 }, (_, i) =>
    edgeSpectrum(from + i, amplitude, decayLength, parityBlind));
}
export function qualitativeStudyNote(n) {
  if (n < 3 || n > 14) return 'Outside N=3–14 examples discussed in the published paper: toy extrapolation only.';
  if (n === 14) return 'N=14: faint incipient YSR-like components were reported, despite even-chain singlet character.';
  if (n % 2) return 'Odd chains: intragap YSR bound states were observed. This model does not calculate their energies.';
  return 'Even chains: singlet-like ground state and extra-gap spin excitations were observed; not magnetically empty.';
}
