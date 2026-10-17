import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const data=JSON.parse(readFileSync(new URL('./data/qp5-reference.json',import.meta.url),'utf8'));
const find=(n,d,boundary,cut)=>data.rows.find(x=>x.n===n&&x.d_over_j===d&&x.boundary===boundary&&x.cut_after_site===cut);

test('QP5 is a finite computed eigenstate experiment, not a certified phase',()=>{
  assert.equal(data.protocol,'PHIFIELD_QP5_FINITE_SCHMIDT_AUDIT_V1');
  assert.equal(data.origin,'SIMULATED');
  assert.equal(data.authority,'NONE');
  assert.equal(data.attested,false);
  assert.match(data.data_kind,/NOT_LAB_OBSERVATION/);
  assert.equal(data.entropy_units,'nats (natural logarithm)');
  assert.equal(data.rows.length,48);
  assert.ok(data.caveats.some(x=>x.includes('do NOT establish')));
  assert.ok(data.caveats.some(x=>x.includes('TWO bonds')));
});

test('Schmidt probabilities normalize and all cut metadata are present',()=>{
  for(const row of data.rows){
    assert.ok(row.eigenpair_residual<1e-7);
    assert.equal(row.probability_trace,1);
    assert.equal(row.schmidt_probabilities_top6.length,6);
    assert.ok(row.entropy_von_neumann_nats>=0);
    assert.ok(row.schmidt_pair_split>=0);
    assert.ok(row.purity>0&&row.purity<=1);
    assert.ok(row.cut_after_site===1||row.cut_after_site===row.n/2);
    assert.equal(row.left_dimension,3**row.cut_after_site);
    assert.equal(row.right_dimension,3**(row.n-row.cut_after_site));
    row.schmidt_probabilities_top6.forEach((p,i)=>{
      assert.ok(p>=0&&p<=1);
      if(i)assert.ok(p<=row.schmidt_probabilities_top6[i-1]+1e-9);
    });
    if(row.cut_after_site===1){
      assert.ok(Math.abs(row.schmidt_probabilities_top6.reduce((a,b)=>a+b,0)-1)<2e-8);
    }
  }
});

test('High D lowers finite entanglement in matched systems',()=>{
  for(const n of data.n_values){
    for(const boundary of data.boundaries){
      for(const cut of [1,n/2]){
        const a=find(n,0,boundary,cut);
        const b=find(n,12,boundary,cut);
        assert.ok(a&&b);
        assert.ok(b.entropy_von_neumann_nats<a.entropy_von_neumann_nats);
        assert.ok(b.largest_schmidt_probability>a.largest_schmidt_probability);
      }
    }
  }
});

test('Every model condition has both open and periodic bipartitions',()=>{
  for(const n of data.n_values)for(const d of data.d_values)for(const boundary of data.boundaries){
    assert.ok(find(n,d,boundary,1));
    assert.ok(find(n,d,boundary,n/2));
  }
});
