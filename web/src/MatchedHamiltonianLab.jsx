import { useState } from 'react';
import { ArrowUpRight, Atom, RotateCcw, ShieldCheck } from 'lucide-react';
import data from './data/qp3-reference.json';
import './qp3.css';

const REPO='https://github.com/MichaelWave369/PhiFieldLab';
const f = x => Number(x).toFixed(5);
const pct = x => (100*Number(x)).toFixed(1)+'%';

export default function MatchedHamiltonianLab() {
  const [n,setN]=useState(6);
  const [d,setD]=useState(12);
  const current=data.rows.find(x=>x.n===n && x.anisotropy_d===d);
  const reference=data.rows.find(x=>x.n===n && x.anisotropy_d===0);
  const compare=data.rows.filter(x=>x.n===n);
  if(!current||!reference) return <section className="shell section">QP3 dataset is unavailable.</section>;
  return <section className="shell section qp3-section" id="matched-hamiltonian">
    <div className="section-heading">
      <div className="eyebrow"><b>01E</b><span/> QP3 · MATCHED HAMILTONIAN CONTROL</div>
      <h2>Change the rule. <em>Keep the test.</em></h2>
      <p>We hold the finite spin-1 chain, boundary geometry and measured observable constant. Only the single-ion anisotropy term changes. What survives this control, and what fades?</p>
    </div>
    <div className="qp3-grid">
      <article className="qp3-panel">
        <div className="card-bar"><span><Atom size={17}/> FINITE SPIN-1 HAMILTONIAN</span><small>COMPUTED / NOT OBSERVED</small></div>
        <div className="qp3-body">
          <div className="qp3-formula">H = J Σ Sᵢ·Sᵢ₊₁ <span>+</span> D Σ (Sᶻᵢ)²</div>
          <div className="qp3-controls">
            <fieldset><legend>Open chain length</legend><div className="qp3-buttons">{data.n_values.map(x=><button type="button" key={x} className={x===n?'selected':''} onClick={()=>setN(x)} aria-pressed={x===n}>N={x}</button>)}</div></fieldset>
            <fieldset><legend>Single-ion anisotropy D/J</legend><div className="qp3-buttons">{data.d_values.map(x=><button type="button" key={x} className={x===d?'selected':''} onClick={()=>setD(x)} aria-pressed={x===d}>D={x}</button>)}</div></fieldset>
            <button type="button" className="qp3-reset" onClick={()=>{setN(6);setD(12)}}><RotateCcw size={15}/> Reset</button>
          </div>
          <div className="qp3-comparison">
            <div className="qp3-measure"><small>FINITE STRING CORRELATION</small><strong>{f(current.string_zz)}</strong><span>D=0 reference: {f(reference.string_zz)}</span></div>
            <div className="qp3-measure"><small>ALL-ZERO PRODUCT OVERLAP</small><strong>{pct(current.all_zero_product_overlap)}</strong><span>D=0 reference: {pct(reference.all_zero_product_overlap)}</span></div>
            <div className="qp3-measure"><small>LOCAL (Sᶻ)² OCCUPATION</small><strong>{f(current.mean_local_sz_squared)}</strong><span>D=0 reference: {f(reference.mean_local_sz_squared)}</span></div>
            <div className="qp3-measure"><small>SAME-SITE-PAIR TWO-POINT</small><strong>{f(current.two_point_zz)}</strong><span>M=0, sites 0 and N−2</span></div>
          </div>
          <p className="qp3-small-note">All values are computed finite-eigenstate expectations in model units J=1. D=0 reuses the QP2 Hamiltonian; no neural predictions are involved.</p>
        </div>
      </article>
      <article className="qp3-panel">
        <div className="card-bar"><span>THE CONTROL LADDER</span><small>FIXED N={n}</small></div>
        <div className="qp3-body">
          <p className="qp3-lead">Every row changes <strong>only D</strong>. A high positive D favors the local spin-zero product state, giving us a meaningful alternative model regime rather than a fake zero-correlation control.</p>
          <div className="qp3-row-head"><span>D/J</span><span>STRING |Oᶻ|</span><span>ZERO-STATE OVERLAP</span></div>
          {compare.map(row=><button type="button" className={'qp3-ladder '+(d===row.anisotropy_d?'current':'')} key={row.anisotropy_d} aria-pressed={d===row.anisotropy_d} onClick={()=>setD(row.anisotropy_d)}>
            <b>{row.anisotropy_d}</b>
            <div><span style={{width:Math.min(100,Math.abs(row.string_zz)*160)+'%'}}/><small>{f(row.string_zz)}</small></div>
            <div><span className="qp3-overlap" style={{width:(100*row.all_zero_product_overlap)+'%'}}/><small>{pct(row.all_zero_product_overlap)}</small></div>
          </button>)}
          <div className="qp3-warning"><ShieldCheck size={21}/><div><strong>Do not promote finite correlations to a phase claim.</strong><p>Changing D breaks the full spin-rotation symmetry and changes the quantum state. This experiment does not locate a critical point, establish thermodynamic string order or reproduce superconducting spectra. The all-zero overlap is a computational reference, not experimental fidelity.</p></div></div>
          <div className="qp3-source">SIMULATED · AUTHORITY NONE · INDEPENDENT ATTESTATION FALSE</div>
          <a className="qp3-link" href={REPO+'/blob/main/docs/QP3_PROTOCOL.md'} target="_blank" rel="noopener noreferrer">Read the frozen QP3 protocol <ArrowUpRight size={16}/></a>
          <a className="qp3-link" href={REPO+'/blob/main/src/phifieldlab/qp3.py'} target="_blank" rel="noopener noreferrer">Inspect the original Python solver <ArrowUpRight size={16}/></a>
        </div>
      </article>
    </div>
  </section>;
}
