import test from 'node:test';
import assert from 'node:assert/strict';
import { D2_POLICY, inspectD2Receipt } from './d2Receipt.js';

function fakeReceipt() {
  const row = seed => ({
    seed, trace_sha256: 'a'.repeat(64), sham_equals_baseline: true,
    baseline: { policy: 'fifo', offered_packets: 100, delivered_packets: 90,
      dropped_packets: 10, latency_p95_ms: 40 },
    candidate: { policy: 'fair', offered_packets: 100, delivered_packets: 90,
      dropped_packets: 10, latency_p95_ms: 20 },
    sensitive_p95_reduction_percent: 50,
    loss_not_worse: true
  });
  return {
    protocol: 'PHIFIELD_D2_EXECUTION_RECEIPT_V1', adapter: D2_POLICY.adapter,
    mission_id: D2_POLICY.mission_id, origin: 'SIMULATED', authority: 'NONE', attested: false,
    runtime_gate: { os_network_and_filesystem_sandbox: false, allowed_external_spend_usd: 0 },
    result: {
      protocol: 'PHIFIELD_D2_SYNTHETIC_QUEUE_V1',
      origin: 'SIMULATED', authority: 'NONE', attested: false,
      workload: {ticks_per_seed: D2_POLICY.ticks_per_seed, queue_capacity_packets: D2_POLICY.queue_capacity_packets,
        seeds: D2_POLICY.seeds},
      rows: D2_POLICY.seeds.map(row),
      review: {scientific_promotion: 'BLOCKED', verdict: 'MEETS_DECLARED_TOY_THRESHOLD'}
    }
  };
}

test('D2 policy permanently denies network, production devices and publication', () => {
  assert.equal(D2_POLICY.protocol, 'PHIFIELD_D2_RUN_POLICY_V1');
  assert.equal(D2_POLICY.mode, 'LOCAL_APPROVAL_REQUIRED');
  assert.deepEqual(D2_POLICY.seeds, [101,103,107,109,113]);
  assert.equal(D2_POLICY.max_wall_seconds, 30);
  assert.ok(Object.values(D2_POLICY.permissions).every(value => value === false));
});

test('local inspector validates structural claims, explicitly not attestation', () => {
  const result = inspectD2Receipt(fakeReceipt());
  assert.equal(result.ok, true);
  assert.equal(result.rows.length, 5);
  assert.match(result.scope, /NOT_A_REPLAY/);
});

test('local inspector rejects spoofed authority and manipulated metrics', () => {
  const changes = [
    r => { r.attested = true; },
    r => { r.runtime_gate.os_network_and_filesystem_sandbox = true; },
    r => { r.result.review.scientific_promotion = 'VERIFIED'; },
    r => { r.result.rows[0].seed = 999; },
    r => { r.result.rows[0].baseline.dropped_packets = 50; },
    r => { r.result.rows[0].sensitive_p95_reduction_percent = 100; },
    r => { r.result.rows[0].sham_equals_baseline = false; },
    r => { r.result.rows = []; }
  ];
  for (const modify of changes) {
    const item = fakeReceipt();
    modify(item);
    assert.equal(inspectD2Receipt(item).ok, false, JSON.stringify(item).slice(0, 120));
  }
});
