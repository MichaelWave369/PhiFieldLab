import { useState } from 'react';
import { Activity, ArrowUpRight, RotateCcw, ShieldCheck } from 'lucide-react';
import ref from './data/qp4-reference.json';
import './qp4.css';

const REPO='https://github.com/MichaelWave369/PhiFieldLab';
const fmt=value=>Number(value).toFixed(5);
export default function SpectralGapLab(){
  const [n,setN]=useState(6);
  const [d,setD]=useState(1);
  const [boundary,setBoundary]=useState('open');
  const chosen=ref.rows.find(x=>x.n===n&&x.d_over_j===d&&x.boundary===boundary);
  const series=ref.rows.filter(x=>x.n===n&&x.boundary===boundary);
  const other=ref.rows.find(x=>x.n===n&&x.d_over_j===d&&x.boundary!==(boundary));
  if(!chosen||!other)return <section className="shell section">QP4 computed reference unavailable.</section>;
  const maximum=Math.max(...series.map(x=>x.first_excitation_gap),.01);
  return <section className="shell section q4-section" id="spectral-gaps">
    <div className="section-heading">
      <div className="eyebrow"><b>01F</b><span/> QP4 · FINITE SPECTRAL CROSS-EXAMINATION</div>
      <h2>Follow the <em>energy.</em></h2>
      <p>QP3 followed correlations as the Hamiltonian changed. QP4 checks the low-energy spectrum of the same finite spin-1 system, including every magnetization sector, with open-chain versus ring comparisons and no manufactured critical point.</p>
    </div>
    <div className="q4-grid">
      <article className="q4-panel">
        <div className="card-bar"><span><Activity size={17}/> FINITE MANY-BODY LEVELS</span><small>SIMULATED · J=1</small></div>
        <div className="q4-inside">
          <div className="q4-grid-select">
            <fieldset><legend>Number of spin-1 sites</legend><div className="q4-options">{ref.n_values.map(x=><button type="button" key={x} className={n===x?'selected':''} aria-pressed={n===x} onClick={()=>setN(x)}>N={x}</button>)}</div></fieldset>
            <fieldset><legend>Anisotropy D/J</legend><div className="q4-options">{ref.d_values.map(x=><button type="button" key={x} className={d===x?'selected':''} aria-pressed={d===x} onClick={()=>setD(x)}>D={x}</button>)}</div></fieldset>
          </div>
          <fieldset className="q4-boundary"><legend>Chain geometry</legend>
            <label><input type="radio" name="q4-boundary" checked={boundary==='open'} onChange={()=>setBoundary('open')}/> Open chain</label>
            <label><input type="radio" name="q4-boundary" checked={boundary==='periodic'} onChange={()=>setBoundary('periodic')}/> Periodic ring</label>
          </fieldset>
          <div className="q4-gaps">
            <div><small>FIRST POSITIVE EXCITATION</small><strong>{fmt(chosen.first_excitation_gap)}</strong><span>{chosen.first_excitation_sector} · model units J</span></div>
            <div><small>NEUTRAL M=0 GAP</small><strong>{fmt(chosen.neutral_m0_gap)}</strong><span>Within fixed magnetization</span></div>
            <div><small>MAGNETIZATION-CHANGING GAP</small><strong>{fmt(chosen.magnetization_changing_gap)}</strong><span>Minimum over |M|=1 to {n}</span></div>
          </div>
          <div className="q4-check"><ShieldCheck size={17}/> Lowest sector M=0 checked against all M=1…{n}. Ground energy {fmt(chosen.lowest_m0_energy)} J.</div>
          <div className="q4-chart">
            <div className="q4-chart-caption">COARSE D GRID · CLICK TO COMPARE</div>
            {series.map(point=><button type="button" aria-pressed={point.d_over_j===d} className={'q4-data-line '+(point.d_over_j===d?'selected':'')} key={point.d_over_j} onClick={()=>setD(point.d_over_j)}>
              <span>D={point.d_over_j}</span><span className="q4-track"><span style={{width:(point.first_excitation_gap/maximum*100)+'%'}}/></span><b>{fmt(point.first_excitation_gap)}</b>
            </button>)}
          </div>
          <p className="q4-fine">A minimum among these four samples cannot locate a physical phase boundary. Open-chain end states can affect the lowest finite gap. These numbers are eigenvalue differences, not experimental tunnelling energies.</p>
        </div>
      </article>
      <article className="q4-panel">
        <div className="card-bar"><span>GEOMETRY CROSS-CHECK</span><button type="button" aria-label="Reset QP4 controls" className="q4-reset" onClick={()=>{setN(6);setD(1);setBoundary('open')}}><RotateCcw size={18}/></button></div>
        <div className="q4-inside">
          <div className="q4-side-by-side">
            <div><small>SELECTED: {boundary.toUpperCase()}</small><strong>{fmt(chosen.first_excitation_gap)}</strong></div>
            <div><small>OTHER: {other.boundary.toUpperCase()}</small><strong>{fmt(other.first_excitation_gap)}</strong></div>
          </div>
          <p className="q4-comparison">Same N={n}, same D/J={d}, different boundary connectivity. This comparison can reveal finite edge sensitivity, but cannot identify a bulk phase on its own.</p>
          <h3>Calculated M-sector minima</h3>
          <div className="q4-sector-list">{Object.entries(chosen.magnetization_sector_minima).map(([sector,value])=><div key={sector}><span>M = {sector}</span><code>{fmt(value)}</code></div>)}</div>
          <div className="q4-caution"><ShieldCheck size={21}/><div><b>Scientific status: SIMULATED / authority NONE</b><p>All nonnegative M sectors were evaluated; negative M sectors mirror them for this Hamiltonian. D&gt;0 breaks full spin-rotation symmetry. Neither the first finite excitation nor a coarse-grid minimum is a measured Haldane gap or a phase-transition estimate.</p></div></div>
          <a className="q4-link" href={REPO+'/blob/main/docs/QP4_PROTOCOL.md'} target="_blank" rel="noopener noreferrer">Frozen QP4 protocol <ArrowUpRight size={16}/></a>
          <a className="q4-link" href={REPO+'/blob/main/src/phifieldlab/qp4.py'} target="_blank" rel="noopener noreferrer">Original Python spectrum calculation <ArrowUpRight size={16}/></a>
        </div>
      </article>
    </div>
  </section>;
}
