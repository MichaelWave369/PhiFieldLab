import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const mission = JSON.parse(readFileSync(new URL('../../missions/qp5-d0-matched-controls.json', import.meta.url), 'utf8'));

test('D0 public viewer only exposes an explicitly bounded, simulated mission', () => {
  assert.equal(mission.protocol, 'PHIFIELD_DISCOVERY_D0_V1');
  assert.equal(mission.adapter, 'QP5_FROZEN_READ_ONLY');
  assert.equal(mission.reference_protocol, 'PHIFIELD_QP5_FINITE_SCHMIDT_AUDIT_V1');
  assert.deepEqual([mission.origin, mission.authority, mission.attested], ['SIMULATED', 'NONE', false]);
  assert.deepEqual(mission.approval, {
    operator_required: true, network: false, external_writes: false,
    publication: false, code_changes: false
  });
  assert.deepEqual(mission.limits, { maximum_rows: 48, maximum_candidates: 2 });
});

test('D0 mission defines competing falsifiable candidates without a claimed verdict', () => {
  assert.deepEqual(mission.candidates.map(c => c.test), ['D12_LT_D0', 'D12_EQ_D0']);
  assert.ok(mission.candidates.every(c => c.falsifier && c.statement));
  assert.ok(mission.candidates.every(c => !('verdict' in c)));
});
