import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { DOMAIN_OPTIONS, PROTOCOL, formatDraft, newDraft, validateDraft } from './d1Mission.js';

const clone = v => structuredClone(v);
const fixture = name => JSON.parse(readFileSync(
  new URL('../../missions/d1-examples/' + name + '.json', import.meta.url), 'utf8'));

test('all shipped D1 proposal examples validate; no action is authorized', () => {
  for (const file of ['network-switch-latency', 'music-arrangement-listener-study',
    'spin-chain-scaling-question']) {
    const proposal = fixture(file);
    const result = validateDraft(proposal);
    assert.equal(result.ok, true, result.errors.join('\n'));
    assert.equal(proposal.protocol, PROTOCOL);
    assert.equal(proposal.status, 'PROPOSAL_ONLY');
    assert.deepEqual(proposal.provenance, { origin: 'PROPOSED', authority: 'NONE', attested: false });
    assert.deepEqual(proposal.permissions, {
      operator_approval_required: true, local_execution: false, network_access: false,
      repository_writes: false, publication: false, external_spend: false
    });
  }
});

test('all domain templates validate and round-trip through JSON', () => {
  for (const [domain] of DOMAIN_OPTIONS) {
    const proposal = newDraft(domain);
    const result = validateDraft(proposal);
    assert.equal(result.ok, true, domain + ': ' + result.errors.join('\n'));
    assert.deepEqual(JSON.parse(formatDraft(proposal)), proposal);
  }
});

test('reject permission escalations, false attestation, new fields and candidate cloning', () => {
  const cases = [];
  const base = newDraft('networking');
  for (const key of ['local_execution', 'network_access', 'repository_writes', 'publication', 'external_spend']) {
    const x = clone(base); x.permissions[key] = true; cases.push(x);
  }
  for (const [parent, key, value] of [
    ['permissions', 'operator_approval_required', false],
    ['provenance', 'attested', true],
    ['resources', 'max_external_cost_usd', 10],
    ['resources', 'max_runtime_minutes', 9000],
    ['resources', 'max_compute_units', 1.5],
    ['evaluation', 'success_criterion', base.evaluation.failure_criterion]
  ]) {
    const x = clone(base); x[parent][key] = value; cases.push(x);
  }
  { const x = clone(base); x.action = 'run'; cases.push(x); }
  { const x = clone(base); x.candidates[1].id = 'H1'; cases.push(x); }
  { const x = clone(base); x.candidates[0].falsifier = x.candidates[0].prediction; cases.push(x); }
  { const x = clone(base); x.title = ''; cases.push(x); }
  { const x = clone(base); x.candidates = []; cases.push(x); }
  for (const bad of cases) assert.equal(validateDraft(bad).ok, false, JSON.stringify(bad).slice(0, 140));
});

test('D1 only validates proposals; never accepts a D0 execution protocol', () => {
  const d0 = fixture('network-switch-latency');
  d0.protocol = 'PHIFIELD_DISCOVERY_D0_V1';
  assert.equal(validateDraft(d0).ok, false);
});
