import { useState } from 'react';
import { ArrowUpRight, Layers3, RotateCcw, ShieldCheck } from 'lucide-react';
import data from './data/qp5-reference.json';
import './qp5.css';

const REPO = 'https://github.com/MichaelWave369/PhiFieldLab';
const fmt = value => Number(value).toFixed(5);
const percent = value => (Number(value)*100).toFixed(1)+'%';

export default function SchmidtSpectrumLab() {
  const [n,setN]=useState(6);
  const [d,setD]=useState(0);
  const [boundary,setBoundary]=useState('open');
  const [cutMode,setCutMode]=useState('center');
  const cut = cutMode==='center' ? n/2 : 1;
  const matching = (length,anisotropy,geometry,position) => data.rows.find(
    row => row.n===length && row.d_over_j===anisotropy &&
           row.boundary===geometry && row.cut_after_site===position);
  const selected=matching(n,d,boundary,cut);
  const matched=matching(n,0,boundary,cut);
  const comparison=data.d_values.map(x=>matching(n,x,boundary,cut));
  const reset=()=>{setN(6);setD(0);setBoundary('open');setCutMode('center');};
  if(!selected||!matched||comparison.some(x=>!x))return <section className="shell section">QP5 computed reference unavailable.</section>;
  return <section className="shell section q5-section" id="schmidt-spectrum">
    <div className="section-heading">
      <div className="eyebrow"><b>01G</b><span/> QP5 · FINITE SCHMIDT SPECTRUM</div>
      <h2>Split the chain. <em>Inspect the state.</em></h2>
      <p>Numbers from actual eigenvectors of our existing spin-1 Hamiltonian, not from an assumed topological label. See how much quantum information survives a one-site or central cut, and compare the same calculation as anisotropy changes.</p>
    </div>
    <div className="q5-layout">
      <article className="q5-panel">
        <div className="card-bar"><span><Layers3 size={17}/> COMPUTED SCHMIDT PROBABILITIES</span><small>STATE / M=0 · J=1</small></div>
        <div className="q5-body">
          <div className="q5-chain" role="img" aria-label={'An '+n+'-site spin chain cut after site '+cut}>
            {Array.from({length:n},(_,i)=><div key={i} className={'q5-site '+(i+1===cut?'q5-after-cut':'')}>
              <b>1</b><small>{i+1}</small>
            </div>)}
          </div>
          <div className="q5-mini-meta"><span>{boundary==='open'?'OPEN: ONE BOND CUT':'PERIODIC: TWO BONDS CUT'}</span><span>{cut} SITES | {n-cut} SITES</span></div>
          <div className="q5-top-metrics">
            <div><small>ENTANGLEMENT ENTROPY</small><strong>{fmt(selected.entropy_von_neumann_nats)}</strong><span>Nats · natural logarithm</span></div>
            <div><small>TOP SCHMIDT PAIR SPLIT</small><strong>{fmt(selected.schmidt_pair_split)}</strong><span>λ₁ − λ₂, not protected-degeneracy proof</span></div>
            <div><small>REDUCED STATE PURITY</small><strong>{fmt(selected.purity)}</strong><span>Tr(ρ²)</span></div>
          </div>
          <h3>Six leading reduced-state eigenvalues</h3>
          <div className="q5-spectrum">{selected.schmidt_probabilities_top6.map((value,i)=><div className="q5-spectrum-row" key={i}>
            <span>λ{i+1}</span><div><span style={{width:(value*100)+'%'}}/></div><b>{fmt(value)}</b>
          </div>)}</div>
          <p className="q5-note">The entire Schmidt distribution is normalized to 1 before rounding. Zero-padded entries appear when the smaller subsystem has fewer than six possible states. The bars show probabilities, not physical excitation energies.</p>
        </div>
      </article>
      <article className="q5-panel">
        <div className="card-bar"><span>MATCHED CONTROLS</span><button type="button" className="q5-reset" onClick={reset} aria-label="Reset QP5 controls"><RotateCcw size={18}/></button></div>
        <div className="q5-body">
          <fieldset className="q5-field"><legend>Chain length</legend><div className="q5-choices">{data.n_values.map(x=><button type="button" key={x} className={n===x?'selected':''} onClick={()=>setN(x)} aria-pressed={n===x}>N={x}</button>)}</div></fieldset>
          <fieldset className="q5-field"><legend>Single-ion anisotropy D/J</legend><div className="q5-choices">{data.d_values.map(x=><button type="button" key={x} className={d===x?'selected':''} onClick={()=>setD(x)} aria-pressed={d===x}>D={x}</button>)}</div></fieldset>
          <fieldset className="q5-field"><legend>Boundary condition</legend><label><input type="radio" name="q5-boundary" checked={boundary==='open'} onChange={()=>setBoundary('open')}/> Open ends</label><label><input type="radio" name="q5-boundary" checked={boundary==='periodic'} onChange={()=>setBoundary('periodic')}/> Periodic ring</label></fieldset>
          <fieldset className="q5-field"><legend>Partition</legend><label><input type="radio" name="q5-cut" checked={cutMode==='center'} onChange={()=>setCutMode('center')}/> Central cut, after site {n/2}</label><label><input type="radio" name="q5-cut" checked={cutMode==='edge'} onChange={()=>setCutMode('edge')}/> One-site cut</label></fieldset>
          <div className="q5-compare">
            <span className="q5-small-label">ENTROPY vs. D/J · SAME N, BOUNDARY AND CUT</span>
            {comparison.map(row=><button type="button" key={row.d_over_j} onClick={()=>setD(row.d_over_j)} className={'q5-entropy-row '+(row.d_over_j===d?'active':'')} aria-pressed={row.d_over_j===d}>
              <b>D={row.d_over_j}</b><span><span style={{width:(row.entropy_von_neumann_nats/Math.log(row.left_dimension)*100)+'%'}}/></span><strong>{fmt(row.entropy_von_neumann_nats)}</strong>
            </button>)}
          </div>
          <div className="q5-caveat"><ShieldCheck size={21}/><div><b>Not a topological certificate</b><p>A finite Schmidt doublet or nonzero entropy does not establish protected Haldane order. A ring cut crosses two bonds; an open-chain cut crosses one. Large D favors a product-like state but does not locate a thermodynamic phase boundary.</p></div></div>
          <div className="q5-provenance">SIMULATED · AUTHORITY NONE · UNATTESTED</div>
          <a className="q5-link" href={REPO+'/blob/main/docs/QP5_PROTOCOL.md'} target="_blank" rel="noopener noreferrer">QP5 frozen protocol <ArrowUpRight size={16}/></a>
          <a className="q5-link" href={REPO+'/blob/main/src/phifieldlab/qp5.py'} target="_blank" rel="noopener noreferrer">Original Python calculation <ArrowUpRight size={16}/></a>
        </div>
      </article>
    </div>
  </section>;
}
