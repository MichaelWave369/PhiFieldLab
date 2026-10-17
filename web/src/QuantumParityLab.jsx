import { useState } from 'react';
import { ArrowUpRight, Download, RotateCcw, ShieldAlert } from 'lucide-react';
import { QP0_PROTOCOL, edgeSpectrum, parityLadder, qualitativeStudyNote } from './parity.js';
import './quantum-parity.css';

const PAPER = 'https://doi.org/10.1038/s41586-026-11117-y';
const fmt = n => n.toFixed(4);
function QuantumChain({ n }) {
  const unitWidth = 600 / n;
  return <svg className="qp-chain" viewBox="0 0 640 155" role="img" aria-label={n + ' conceptual spin-1 triangulene units connected in a line'}>
    <defs>
      <linearGradient id="qp-tile" x1="0" x2="1" y1="0" y2="1"><stop stopColor="#1d6b70"/><stop offset="1" stopColor="#123843"/></linearGradient>
    </defs>
    <line x1="20" y1="76" x2="620" y2="76" stroke="#85e4cf" strokeOpacity=".42" strokeWidth="4"/>
    {Array.from({length:n},(_,i)=>{
      const x = 20 + (i+.5)*unitWidth;
      const outer = Math.min(24,unitWidth*.4);
      return <g key={i}>
        <path d={'M'+x+' '+(76-outer)+' L'+(x-outer)+' '+(76+outer*.68)+' L'+(x+outer)+' '+(76+outer*.68)+' Z'} fill="url(#qp-tile)" stroke={i===0||i===n-1?'#ffcb92':'#73d8c4'} strokeWidth={i===0||i===n-1?2.6:1.6}/>
        {n<=12 && <text x={x} y="83" textAnchor="middle" fontSize="12" fontWeight="750" fill="#ddfff4">{i+1}</text>}
      </g>;
    })}
    <text x="20" y="137" fill="#ffcb92" fontSize="12">edge ½</text>
    <text x="620" y="137" textAnchor="end" fill="#ffcb92" fontSize="12">edge ½</text>
    <text x="320" y="22" textAnchor="middle" fill="#8bb6c0" fontSize="12" letterSpacing="1.5">SPIN-1 UNITS · CONCEPTUAL</text>
  </svg>;
}
function ExchangeChart({ amplitude, decayLength, selectedN }) {
  const points=parityLadder(3,16,amplitude,decayLength);
  const max=points[0].excitation_gap || 1;
  const x=n=>35+(n-3)*35;
  const y=v=>125-100*v/max;
  return <svg className="qp-chart" viewBox="0 0 525 175" role="img" aria-label="Toy excitation gap decreases with molecular chain length; highlighted selected chain">
    {[25,75,125].map(a=><line key={a} x1="35" y1={a} x2="495" y2={a} stroke="#365661" strokeDasharray="4 7"/>)}
    <polyline fill="none" stroke="#75ebd1" strokeWidth="2.5" points={points.map(p=>x(p.n)+','+y(p.excitation_gap)).join(' ')}/>
    {points.map(p=><circle key={p.n} cx={x(p.n)} cy={y(p.excitation_gap)} r={p.n===selectedN?6:3.2} fill={p.n===selectedN?'#ffca88':p.n%2?'#78e7d2':'#82aef2'} stroke={p.n===selectedN?'#fff': 'none'} strokeWidth="1.5"/>)}
    <text x="35" y="12" fontSize="11" fill="#aac8ce">|J| · arbitrary units</text>
    <text x="35" y="148" fontSize="11" fill="#aac8ce">3</text>
    <text x="490" y="148" textAnchor="end" fontSize="11" fill="#aac8ce">16</text>
    <text x="263" y="169" textAnchor="middle" fontSize="11" fill="#aac8ce">CHAIN LENGTH N</text>
  </svg>;
}
export default function QuantumParityLab() {
  const [n,setN]=useState(7);
  const [amplitude,setAmplitude]=useState(1);
  const [decayLength,setDecayLength]=useState(4);
  const [parityBlind,setParityBlind]=useState(false);
  const [exported,setExported]=useState('');
  const current=edgeSpectrum(n,amplitude,decayLength,parityBlind);
  const alternate=edgeSpectrum(n,amplitude,decayLength,!parityBlind);
  const rows=parityLadder(3,16,amplitude,decayLength,parityBlind);
  const isOdd=n%2===1;
  function reset(){setN(7);setAmplitude(1);setDecayLength(4);setParityBlind(false);setExported('');}
  function exportReceipt() {
    const payload={
      protocol: QP0_PROTOCOL,
      origin:'SIMULATED',authority:'NONE',attested:false,
      source_paper_doi:'10.1038/s41586-026-11117-y',
      disclaimer:'Toy two-edge-spin exchange only. No experimental data, superconducting bath or YSR spectra.',
      inputs:{n,amplitude,decay_length:decayLength,parity_blind:parityBlind},
      result:current,negative_control:edgeSpectrum(n,amplitude,decayLength,true),
      ladder:rows
    };
    const blob=new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json'});
    const url=URL.createObjectURL(blob);
    const link=document.createElement('a');
    link.href=url;link.download='phifield-qp0-n'+n+'-'+(parityBlind?'null':'toy')+'.json';
    document.body.appendChild(link);link.click();link.remove();
    URL.revokeObjectURL(url);
    setExported('Local JSON receipt created. Results are simulated, not laboratory evidence.');
  }
  return <section className="shell section qp-section" id="quantum-parity">
    <div className="section-heading">
      <div className="eyebrow"><b>01B</b><span/> QP0 · QUANTUM PARITY LAB</div>
      <h2>One more unit. <em>Another ground state.</em></h2>
      <p>Explore an original, transparent two-spin exchange toy inspired by the 2026 triangulene-chain experiment. Change the molecule count; compare with a parity-blind negative control. No quantum hardware or superconducting simulation runs here.</p>
    </div>
    <div className="qp-layout">
      <article className="qp-panel qp-scene">
        <div className="card-bar"><span>EDGE EXCHANGE / EDUCATIONAL</span><small>SIMULATED · NO FIT</small></div>
        <div className="qp-scene-content">
          <div className="qp-tags"><span>{isOdd?'ODD CHAIN':'EVEN CHAIN'}</span><span>J = {fmt(current.exchange)}</span></div>
          <QuantumChain n={n}/>
          <div className="qp-outcomes">
            <div><small>GROUND TOTAL SPIN</small><strong>S = {current.ground_total_spin}</strong><span>{current.ground_total_spin===0?'Singlet':'Triplet'}</span></div>
            <div><small>EXCITATION GAP |J|</small><strong>{fmt(current.excitation_gap)}</strong><span>Arbitrary units</span></div>
          </div>
          <div className="qp-levels">
            <h3>Four eigenstates of H = J sL · sR</h3>
            <div><span>Singlet · 1 state</span><b>E = {fmt(current.singlet_energy)}</b></div>
            <div><span>Triplet · 3 states</span><b>E = {fmt(current.triplet_energy)}</b></div>
            <small>Levels are computed analytically in the browser; Python independently diagonalizes the 4×4 Hamiltonian.</small>
          </div>
          <ExchangeChart amplitude={amplitude} decayLength={decayLength} selectedN={n}/>
        </div>
      </article>
      <article className="qp-panel qp-settings">
        <div className="card-bar"><span>MODEL CONTROLS</span><button className="icon-button" type="button" onClick={reset} aria-label="Reset quantum parity controls"><RotateCcw size={17}/></button></div>
        <div className="qp-field"><div><label htmlFor="qp-n">Triangulene units</label><b>{n}</b></div><input id="qp-n" type="range" min="3" max="16" step="1" value={n} onChange={e=>{setN(Number(e.target.value));setExported('');}}/><aside><span>N = 3</span><span>N = 16</span></aside></div>
        <div className="qp-field"><div><label htmlFor="qp-j0">Toy coupling amplitude J₀</label><b>{amplitude.toFixed(1)}</b></div><input id="qp-j0" type="range" min=".2" max="2" step=".1" value={amplitude} onChange={e=>setAmplitude(Number(e.target.value))}/><aside><span>0.2</span><span>2.0</span></aside></div>
        <div className="qp-field"><div><label htmlFor="qp-xi">Toy decay length ξ</label><b>{decayLength.toFixed(1)}</b></div><input id="qp-xi" type="range" min="2" max="8" step=".5" value={decayLength} onChange={e=>setDecayLength(Number(e.target.value))}/><aside><span>2.0</span><span>8.0</span></aside></div>
        <fieldset className="qp-switches"><legend>Hypothesis test</legend>
          <label><input type="radio" name="qp-model" checked={!parityBlind} onChange={()=>setParityBlind(false)}/> Alternating-sign exchange toy</label>
          <label><input type="radio" name="qp-model" checked={parityBlind} onChange={()=>setParityBlind(true)}/> Parity-blind negative control</label>
        </fieldset>
        <div className="qp-counter"><small>COMPARISON MODEL</small><strong>{parityBlind?'Alternating-sign toy':'Parity-blind null'}</strong><p>At N = {n}, comparison predicts S = {alternate.ground_total_spin} with J = {fmt(alternate.exchange)}.</p></div>
        <button className="qp-export" type="button" onClick={exportReceipt}><Download size={17}/> Export simulated JSON receipt</button>
        <p className="qp-status" role="status">{exported}</p>
      </article>
    </div>
    <div className="qp-explainer">
      <div><ShieldAlert size={23}/><strong>MODEL IS NOT MEASUREMENT</strong><p>{qualitativeStudyNote(n)} The real paper detects YSR features using scanning tunnelling spectroscopy; this toy does not calculate spectral peaks, the Haldane gap, or superconductivity.</p></div>
      <div><strong>Why the null control matters</strong><p>Removing the assumed parity sign reversal abolishes the switch, even as the coupling still decays. That makes the mechanism easy to inspect and, importantly, easy to challenge.</p><a href={PAPER} target="_blank" rel="noopener noreferrer">Read Nature source <ArrowUpRight size={15}/></a><a href="https://github.com/MichaelWave369/PhiFieldLab/blob/main/docs/QP0_PROTOCOL.md" target="_blank" rel="noopener noreferrer">QP0 protocol <ArrowUpRight size={15}/></a></div>
    </div>
  </section>;
}
