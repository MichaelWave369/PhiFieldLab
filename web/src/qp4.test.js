import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const data=JSON.parse(readFileSync(new URL('./data/qp4-reference.json',import.meta.url),'utf8'));
const by=(n,d,b)=>data.rows.find(r=>r.n===n&&r.d_over_j===d&&r.boundary===b);

test('QP4 has original numerical data and explicit provenance firewall',()=>{
  assert.equal(data.protocol,'PHIFIELD_QP4_FINITE_GAP_SPECTROSCOPY_V1');
  assert.equal(data.origin,'SIMULATED');
  assert.equal(data.authority,'NONE');
  assert.equal(data.attested,false);
  assert.match(data.data_kind,/NOT_LAB_SPECTROSCOPY/);
  assert.equal(data.rows.length,24);
  assert.deepEqual(data.n_values,[4,6,8]);
  assert.deepEqual(data.d_values,[0,1,4,12]);
  assert.deepEqual(data.boundaries,['open','periodic']);
});

test('QP4 includes every nonnegative M sector and finite positive gaps',()=>{
  for(const row of data.rows){
    assert.equal(row.global_ground_is_m0,true);
    assert.ok(row.first_excitation_gap>0);
    assert.ok(row.magnetization_changing_gap>0);
    assert.ok(row.neutral_m0_gap>0);
    assert.ok(Math.abs(row.first_excitation_gap-
      Math.min(row.magnetization_changing_gap,row.neutral_m0_gap))<1e-7);
    assert.deepEqual(Object.keys(row.magnetization_sector_minima).map(Number),
      Array.from({length:row.n+1},(_,i)=>i));
    for(const energy of Object.values(row.magnetization_sector_minima)){
      assert.ok(energy>=row.lowest_m0_energy-1e-7);
    }
  }
});

test('QP4 has matched open/periodic and D controls with guarded interpretation',()=>{
  for(const n of data.n_values)for(const d of data.d_values){
    assert.ok(by(n,d,'open'));
    assert.ok(by(n,d,'periodic'));
  }
  assert.ok(data.caveats.some(x=>x.includes('NOT a phase')));
  assert.ok(data.caveats.some(x=>x.includes('NOT a measured')));
  assert.ok(data.caveats.some(x=>x.includes('M<0')));
});
