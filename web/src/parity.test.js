import test from 'node:test';
import assert from 'node:assert/strict';
import { QP0_PROTOCOL, edgeSpectrum, parityLadder, qualitativeStudyNote } from './parity.js';

test('parity switches the toy ground-state spin without altering absolute exchange', () => {
  const even = edgeSpectrum(6, 1, 4), odd = edgeSpectrum(7, 1, 4);
  assert.equal(even.ground_total_spin, 0);
  assert.equal(odd.ground_total_spin, 1);
  assert.ok(even.exchange > 0 && odd.exchange < 0);
  assert.equal(even.protocol, QP0_PROTOCOL);
  assert.equal(even.origin, 'SIMULATED');
  assert.equal(even.authority, 'NONE');
});
test('analytical singlet and triplet levels with triplet degeneracy', () => {
  for (const n of [3,4,8,9,14,16]) {
    const r = edgeSpectrum(n, 1.3, 3.4);
    assert.ok(Math.abs(r.singlet_energy * 1 + 3*r.exchange/4) < 1e-12);
    assert.ok(Math.abs(r.triplet_energy - r.exchange/4) < 1e-12);
    assert.ok(Math.abs(r.eigenvalues.reduce((a,b)=>a+b,0)) < 1e-12);
    assert.equal(r.eigenvalues.length, 4);
    assert.ok(r.excitation_gap > 0);
  }
});
test('parity-blind negative control does not switch its ground state', () => {
  const rows = parityLadder(3, 16, 1, 4, true);
  assert.equal(rows.length,14);
  assert.ok(rows.every(x=>x.ground_total_spin===0 && x.exchange>0));
  assert.ok(rows.every(x=>x.model==='PARITY_BLIND_NEGATIVE_CONTROL'));
});
test('exchange magnitude decays with N at fixed parameters', () => {
  const r=parityLadder(3,16);
  assert.ok(r.every((x,i)=>i===0 || x.excitation_gap < r[i-1].excitation_gap));
});
test('invalid parameters are refused, and observation caveat is retained', () => {
  for (const call of [()=>edgeSpectrum(1),()=>edgeSpectrum(5.5),()=>edgeSpectrum(4,0),()=>edgeSpectrum(3,1,-2),()=>parityLadder(5,4)])
    assert.throws(call,RangeError);
  assert.match(qualitativeStudyNote(14),/incipient/i);
  assert.match(qualitativeStudyNote(16),/extrapolation/i);
});
