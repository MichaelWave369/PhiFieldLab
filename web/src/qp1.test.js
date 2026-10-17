import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const artifact=JSON.parse(readFileSync(new URL('./data/qp1-reference.json',import.meta.url),'utf8'));
test('QP1 provenance is explicitly computed rather than observed',()=>{
  assert.equal(artifact.origin,'SIMULATED');assert.equal(artifact.authority,'NONE');
  assert.equal(artifact.attested,false);
  assert.equal(artifact.data_kind,'COMPUTED_MODEL_OUTPUT_NOT_LAB_OBSERVATION');
  for(const row of [...artifact.open,...artifact.periodic_negative_control]){
    assert.equal(row.origin,'SIMULATED');assert.equal(row.authority,'NONE');
    assert.equal(row.protocol,artifact.protocol);
  }
});
test('QP1 open parity emerges while periodic control removes it',()=>{
  assert.deepEqual(artifact.range,[3,8]);
  assert.deepEqual(artifact.open.map(p=>p.n),[3,4,5,6,7,8]);
  assert.deepEqual(artifact.open.map(p=>p.ground_total_spin),[1,0,1,0,1,0]);
  assert.deepEqual(artifact.periodic_negative_control.map(p=>p.ground_total_spin),[0,0,0,0,0,0]);
});
test('QP1 model levels have positive gaps and consistent sector sizes',()=>{
  for(const row of [...artifact.open,...artifact.periodic_negative_control]){
    assert.ok(row.lowest_excitation_gap>0);
    assert.ok(Math.abs(row.sector_minima['0']-row.ground_energy)<1e-8);
    assert.ok(row.sector_dimensions['0']>row.sector_dimensions['2']);
  }
});
