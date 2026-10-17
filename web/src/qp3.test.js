import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const result=JSON.parse(readFileSync(new URL('./data/qp3-reference.json',import.meta.url),'utf8'));
const row=(n,d)=>result.rows.find(x=>x.n===n&&x.anisotropy_d===d);

test('QP3 model output is a Python-generated simulated research artifact',()=>{
  assert.equal(result.protocol,'PHIFIELD_QP3_ANISOTROPY_CONTROL_V1');
  assert.equal(result.origin,'SIMULATED');
  assert.equal(result.authority,'NONE');
  assert.equal(result.attested,false);
  assert.match(result.data_kind,/NOT_LAB_OBSERVATION/);
  assert.deepEqual(result.n_values,[4,6,8]);
  assert.deepEqual(result.d_values,[0,1,4,12]);
  assert.equal(result.rows.length,12);
});

test('QP3 keeps geometry, probe sites and sector fixed',()=>{
  for(const r of result.rows){
    assert.equal(r.boundary,'open');
    assert.equal(r.magnetization_sector,0);
    assert.deepEqual(r.probe_sites_zero_based,[0,r.n-2]);
    assert.equal(r.coupling_j,1);
    assert.ok(Number.isFinite(r.string_zz));
    assert.ok(Number.isFinite(r.two_point_zz));
    assert.ok(r.eigenpair_residual<1e-7);
  }
});

test('Large anisotropy increases product overlap and reduces local Sz²',()=>{
  for(const n of result.n_values){
    assert.ok(row(n,12).all_zero_product_overlap>row(n,0).all_zero_product_overlap);
    assert.ok(row(n,12).mean_local_sz_squared<row(n,0).mean_local_sz_squared);
    assert.ok(row(n,12).all_zero_product_overlap>.85);
  }
});

test('QP3 refuses to claim a phase transition',()=>{
  assert.ok(result.caveats.some(x=>x.includes('thermodynamic')));
  assert.ok(result.caveats.some(x=>x.includes('AI training')));
  assert.ok(result.caveats.some(x=>x.includes('not experimental')));
});
