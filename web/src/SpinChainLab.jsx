import { useState } from 'react';
import { ArrowUpRight, RotateCcw, ShieldCheck } from 'lucide-react';
import reference from './data/qp1-reference.json';
import './spin-chain.css';

const RAW = 'https://github.com/MichaelWave369/PhiFieldLab/blob/main/web/src/data/qp1-reference.json';
const SOURCE = 'https://doi.org/10.1038/s41586-026-11117-y';
const fmt = value => value.toFixed(5);

function ChainDiagram({ n, boundary }) {
  const xs = Array.from({length:n}, (_,i)=>35+570*i/(n-1));
  return <svg className="q1-chain" viewBox="0 0 640 125" role="img"
    aria-label={n+' spin-one sites, '+(boundary==='open'?'open chain':'periodic ring')}>
    <line x1="35" y1="67" x2="605" y2="67" stroke="#6bd5be" strokeWidth="3" opacity=".7"/>
    {boundary==='periodic'&&<path d="M35 55 Q320 -55 605 55" fill="none" stroke="#ffc38c" strokeWidth="2.5" strokeDasharray="8 5"/>}
    {xs.map((x,i)=><g key={i}>
      <circle cx={x} cy="67" r="20" fill="#153f47" stroke={boundary==='open'&&(i===0||i===n-1)?'#ffc38c':'#8bead0'} strokeWidth="2.5"/>
      <text x={x} y="72" fill="#e8fff7" fontSize="15" fontWeight="750" textAnchor="middle">1</text>
      <text x={x} y="103" fill="#91b3bb" fontSize="11" textAnchor="middle">{i+1}</text>
    </g>)}
  </svg>;
}

function GapChart({ n, boundary, onSelect }) {
  const set=boundary==='open'?reference.open:reference.periodic_negative_control;
  const max=Math.max(...[...reference.open,...reference.periodic_negative_control].map(x=>x.lowest_excitation_gap));
  return <div className="q1-chart" role="group" aria-label="Finite-chain lowest excitation gaps by chain length">
    {set.map(p=><button type="button" key={p.n} className={'q1-bar'+(p.n===n?' active':'')}
      title={'N='+p.n+'; gap='+fmt(p.lowest_excitation_gap)+' J'} onClick={()=>onSelect(p.n)}
      aria-pressed={p.n===n} aria-label={'Select '+p.n+' units; computed gap '+fmt(p.lowest_excitation_gap)}>
      <span className="q1-bar-area"><span style={{height:(100*p.lowest_excitation_gap/max)+'%'}}/></span>
      <b>{p.n}</b>
    </button>)}
  </div>;
}

export default function SpinChainLab() {
  const [n,setN]=useState(5);
  const [boundary,setBoundary]=useState('open');
  const chosen=boundary==='open'?reference.open:reference.periodic_negative_control;
  const alternate=boundary==='open'?reference.periodic_negative_control:reference.open;
  const result=chosen.find(x=>x.n===n);
  const control=alternate.find(x=>x.n===n);
  return <section className="shell section q1-section" id="spin-chain">
    <div className="section-heading">
      <div className="eyebrow"><b>01C</b><span/> QP1 · FINITE SPIN-1 CHAIN</div>
      <h2>Test the chain. <em>Not just its edges.</em></h2>
      <p>Spin-1 Heisenberg Hamiltonians solved numerically in Python. The parity of the ground-state spin is a computed outcome, not an input rule. Switch the boundary to test the role of exposed ends.</p>
    </div>
    <div className="q1-layout">
      <article className="q1-panel">
        <div className="card-bar"><span>SPIN-1 MANY-BODY SPECTRUM</span><small>COMPUTED · NOT OBSERVED</small></div>
        <div className="q1-body">
          <div className="q1-inline"><span>{boundary==='open'?'OPEN BOUNDARIES':'PERIODIC RING'}</span><span>FULL DIMENSION 3^{n} = {3**n}</span></div>
          <ChainDiagram n={n} boundary={boundary}/>
          <div className="q1-metrics">
            <div><small>GROUND TOTAL SPIN</small><strong>S = {result.ground_total_spin}</strong><span>From sector minima</span></div>
            <div><small>FIRST EXCITATION GAP</small><strong>{fmt(result.lowest_excitation_gap)}</strong><span>Units of J = 1</span></div>
          </div>
          <h3>Lowest energy in each total magnetization sector</h3>
          <div className="q1-sectors">{['0','1','2'].map(m=><div key={m}><small>M = {m}</small><b>{fmt(result.sector_minima[m])}</b><span>{result.sector_dimensions[m]} basis states</span></div>)}</div>
          <h3>Calculated gap across N = 3–8</h3>
          <GapChart n={n} boundary={boundary} onSelect={setN}/>
          <p className="q1-note">Click a bar to inspect that chain. These read-only numbers are precomputed Python results, not browser-side simulation or measured tunnelling spectra.</p>
        </div>
      </article>
      <article className="q1-panel">
        <div className="card-bar"><span>STRUCTURAL CONTROLS</span><button type="button" className="icon-button" onClick={()=>{setN(5);setBoundary('open')}} aria-label="Reset spin-chain controls"><RotateCcw size={17}/></button></div>
        <div className="q1-body">
          <div className="q1-field"><div><label htmlFor="q1-n">Number of spin-1 units</label><b>{n}</b></div>
            <input id="q1-n" type="range" min="3" max="8" step="1" value={n} onChange={e=>setN(Number(e.target.value))}/>
            <aside><span>N=3</span><span>N=8</span></aside>
          </div>
          <fieldset className="q1-boundary"><legend>Boundary condition</legend>
            <label><input type="radio" name="qp1-boundary" checked={boundary==='open'} onChange={()=>setBoundary('open')}/> Open chain · two exposed ends</label>
            <label><input type="radio" name="qp1-boundary" checked={boundary==='periodic'} onChange={()=>setBoundary('periodic')}/> Periodic ring · endpoints connected</label>
          </fieldset>
          <div className="q1-control-result"><small>BOUNDARY NEGATIVE CONTROL</small><strong>Same N, different boundary</strong>
            <p>With {boundary==='open'?'periodic':'open'} boundaries, N={n} has ground spin S={control.ground_total_spin} and first excitation gap {fmt(control.lowest_excitation_gap)} J.</p>
            <b>{result.ground_total_spin===control.ground_total_spin?'Ground-state spin unchanged':'Ground-state spin CHANGED'}</b>
          </div>
          <div className="q1-warning"><ShieldCheck size={22}/><strong>Evidence boundary</strong>
            <p>Isotropic spin-1 finite-chain model only. No YSR states, no superconducting film, no quantitative fit to the Nature paper, and no measured Haldane invariant.</p>
          </div>
          <a className="q1-link" href={RAW} target="_blank" rel="noopener noreferrer">Inspect computed JSON <ArrowUpRight size={16}/></a>
          <a className="q1-link" href="https://github.com/MichaelWave369/PhiFieldLab/blob/main/docs/QP1_PROTOCOL.md" target="_blank" rel="noopener noreferrer">Read QP1 protocol <ArrowUpRight size={16}/></a>
          <a className="q1-link" href={SOURCE} target="_blank" rel="noopener noreferrer">Read original study <ArrowUpRight size={16}/></a>
        </div>
      </article>
    </div>
  </section>;
}
