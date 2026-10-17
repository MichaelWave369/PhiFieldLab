import test from 'node:test';
import assert from 'node:assert/strict';
import policy from '../../src/phifieldlab/schemas/d3_policy.json' with {type:'json'};

test('D3 policy includes all required hardening and no external capabilities', () => {
  assert.equal(policy.protocol, 'PHIFIELD_D3_CLEANROOM_V1');
  assert.equal(policy.adapter, 'SYNTHETIC_QUEUE_V1');
  assert.equal(policy.isolated_backend, 'DOCKER_LINUX_CONTAINER');
  assert.equal(policy.origin, 'SIMULATED');
  assert.equal(policy.authority, 'NONE');
  assert.equal(policy.attested, false);
  assert.equal(policy.controls.network, 'none');
  assert.equal(policy.controls.read_only_rootfs, true);
  assert.equal(policy.controls.rootless_container_user, '65534:65534');
  assert.equal(policy.controls.drop_capabilities, 'ALL');
  assert.equal(policy.controls.no_new_privileges, true);
  assert.equal(policy.controls.pids_limit, 32);
  assert.equal(policy.controls.memory, '128m');
  assert.equal(policy.controls.memory_swap, '128m');
  assert.equal(policy.controls.cpus, '1.0');
  assert.equal(policy.max_wall_seconds, 35);
  assert.ok(Object.entries(policy.permission).every(([key,value]) =>
    key === 'local_approval_required' ? value === true : value === false));
});
