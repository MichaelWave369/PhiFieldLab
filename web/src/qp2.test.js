import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const data=JSON.parse(readFileSync(new URL('./data/qp2-reference.json',import.meta.url),'utf8'));

test('QP2 is openly labeled simulated, not independent physics observation',()=>{
  assert.equal(data.protocol,'PHIFIELD_QP2_EDGE_FINGERPRINTS_V1');
  assert.equal(data.origin,'SIMULATED');
  assert.equal(data.authority,'NONE');
  assert.equal(data.attested,false);
  assert.match(data.data_kind,/NOT_LAB_OBSERVATIONS/);
});
test('Odd open profiles conserve total M=1 and exhibit reflection',()=>{
  assert.deepEqual(data.open_odd_edge_profiles.map(x=>x.n),[3,5,7]);
  for(const row of data.open_odd_edge_profiles){
    assert.equal(row.boundary,'open');
    assert.equal(row.site_magnetization.length,row.n);
    assert.ok(Math.abs(row.site_magnetization.reduce((a,b)=>a+b,0)-1)<1e-7);
    row.site_magnetization.forEach((x,i)=>assert.ok(Math.abs(x-row.site_magnetization[row.n-1-i])<1e-7));
    assert.ok(row.edge_absolute_fraction>row.uniform_fraction_reference);
  }
});
test('String and same-pair ordinary correlations are distinct, rings are not null',()=>{
  for(const group of ['even_string_open','even_string_periodic_geometry_control']){
    const rows=data[group];
    assert.deepEqual(rows.map(x=>x.n),[4,6,8]);
    for(const row of rows){
      assert.deepEqual(row.probe_sites_zero_based,[0,row.n-2]);
      assert.ok(row.string_zz>0);
      assert.ok(row.two_point_zz<0);
      assert.ok(Math.abs(row.string_zz-row.two_point_zz)>.1);
      assert.ok(Math.abs(row.endpoint_string_minus_endpoint_two_point)<1e-7);
      assert.equal(row.all_zero_product_state_string,0);
    }
  }
});
test('Interpretation traps are explicitly documented',()=>{
  assert.ok(data.warnings.some(x=>x.includes('not sufficient')));
  assert.ok(data.warnings.some(x=>x.includes('NOT a null')));
  assert.ok(data.warnings.some(x=>x.includes('endpoint string')));
});
