import policy from '../../src/phifieldlab/schemas/d2_policy.json' with { type: 'json' };

export const D2_POLICY = policy;
export function inspectD2Receipt(candidate) {
  const fail = explanation => ({ ok: false, explanation });
  if (!candidate || typeof candidate !== 'object' || Array.isArray(candidate)) return fail('Not a D2 receipt object');
  if (candidate.protocol !== 'PHIFIELD_D2_EXECUTION_RECEIPT_V1' ||
      candidate.adapter !== policy.adapter || candidate.mission_id !== policy.mission_id)
    return fail('Unknown protocol, adapter or mission');
  if (candidate.origin !== 'SIMULATED' || candidate.authority !== 'NONE' ||
      candidate.attested !== false) return fail('Provenance or authority mismatch');
  const runtime = candidate.runtime_gate;
  if (!runtime || runtime.os_network_and_filesystem_sandbox !== false ||
      runtime.allowed_external_spend_usd !== 0) return fail('Runtime gate mismatch');
  const data = candidate.result;
  if (!data || data.protocol !== 'PHIFIELD_D2_SYNTHETIC_QUEUE_V1' ||
      data.origin !== 'SIMULATED' || data.authority !== 'NONE' ||
      data.attested !== false || data.review?.scientific_promotion !== 'BLOCKED')
    return fail('Result data or claim firewall mismatch');
  if (data.workload?.ticks_per_seed !== policy.ticks_per_seed ||
      data.workload?.queue_capacity_packets !== policy.queue_capacity_packets ||
      JSON.stringify(data.workload?.seeds) !== JSON.stringify(policy.seeds))
    return fail('Unexpected workload');
  if (!Array.isArray(data.rows) || data.rows.length !== policy.seeds.length)
    return fail('Expected exactly five runs');
  for (let i = 0; i < data.rows.length; i++) {
    const row = data.rows[i];
    if (row?.seed !== policy.seeds[i] || row?.sham_equals_baseline !== true ||
        typeof row?.trace_sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(row.trace_sha256))
      return fail('Malformed seed or sham control');
    const oldResult = row.baseline, newResult = row.candidate;
    if (oldResult?.policy !== 'fifo' || newResult?.policy !== 'fair')
      return fail('Wrong comparator policy');
    for (const measure of [oldResult, newResult]) {
      if (!Number.isSafeInteger(measure.offered_packets) || measure.offered_packets <= 0 ||
          !Number.isSafeInteger(measure.dropped_packets) || measure.dropped_packets < 0 ||
          !Number.isSafeInteger(measure.delivered_packets) || measure.delivered_packets < 0 ||
          measure.delivered_packets + measure.dropped_packets !== measure.offered_packets ||
          !Number.isFinite(measure.latency_p95_ms) || measure.latency_p95_ms <= 0)
        return fail('Invalid packet accounting or latency');
    }
    if (oldResult.offered_packets !== newResult.offered_packets ||
        typeof row.sensitive_p95_reduction_percent !== 'number' ||
        !Number.isFinite(row.sensitive_p95_reduction_percent) ||
        row.loss_not_worse !== (newResult.dropped_packets <= oldResult.dropped_packets))
      return fail('Unmatched input or unsupported loss claim');
    const expected = 100 * (oldResult.latency_p95_ms - newResult.latency_p95_ms) / oldResult.latency_p95_ms;
    if (Math.abs(row.sensitive_p95_reduction_percent - expected) > 1e-5)
      return fail('Reported reduction does not match displayed samples');
  }
  return {
    ok: true, rows: data.rows,
    verdict: data.review.verdict,
    scope: 'STRUCTURAL_CHECK_ONLY__NOT_A_REPLAY_OR_ATTESTATION'
  };
}
