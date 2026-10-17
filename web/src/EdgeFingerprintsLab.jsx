import { useState } from 'react';
import { ArrowUpRight, Fingerprint, RotateCcw, ShieldAlert } from 'lucide-react';
import data from './data/qp2-reference.json';
import './qp2.css';

const REPO='https://github.com/MichaelWave369/PhiFieldLab';
const fixed=n=>Number(n).toFixed(5);
const edgeSizes=[3,5,7],stringSizes=[4,6,8];

export default function EdgeFingerprintsLab(){
  const [mode,setMode]=useState('edges');
  const [n,setN]=useState(5);
  const [boundary,setBoundary]=useState('open');
  const edge=data.open_odd_edge_profiles.find(p=>p.n===n) || data.open_odd_edge_profiles[1];
  const stringRows=boundary==='open'?data.even_string_open:data.even_string_periodic_geometry_control;
  const string=stringRows.find(p=>p.n===n) || stringRows[1];
  const alternative=(boundary==='open'?data.even_string_periodic_geometry_control:data.even_string_open).find(p=>p.n===string.n);
  const options=mode==='edges'?edgeSizes:stringSizes;
  function chooseMode(next){setMode(next);setN(next==='edges'?5:6);}
  function reset(){setMode('edges');setN(5);setBoundary('open');}
  return <section className="shell section q2-section" id="edge-fingerprints">
    <div className="section-heading">
      <div className="eyebrow"><b>01D</b><span/> QP2 · EDGE-STATE FINGERPRINTS</div>
      <h2>Where does the <em>signal live?</em></h2>
      <p>Finite spin-1 Heisenberg eigenstates computed independently of the QP0 parity toy. Inspect signed site magnetizations, nonlocal string correlations, and the interpretation traps that keep a finite calculation from becoming an unsupported phase claim.</p>
    </div>
    <div className="q2-mode" role="group" aria-label="Choose finite spin-chain observable">
      <button type="button" className={mode==='edges'?'active':''} onClick={()=>chooseMode('edges')} aria-pressed={mode==='edges'}>Odd open · site spin</button>
      <button type="button" className={mode==='string'?'active':''} onClick={()=>chooseMode('string')} aria-pressed={mode==='string'}>Even chain · string probe</button>
      <button type="button" className="q2-reset" onClick={reset} title="Reset QP2 controls" aria-label="Reset QP2 controls"><RotateCcw size={17}/></button>
    </div>
    <div className="q2-layout">
      <article className="q2-panel">
        <div className="card-bar"><span><Fingerprint size={17}/> {mode==='edges'?'LOCAL SPIN DENSITY · M=+1':'LONGITUDINAL STRING · M=0'}</span><small>COMPUTED · NOT MEASURED</small></div>
        <div className="q2-content">
          <div className="q2-topline"><span>SPIN-1 · J = 1</span><span>{mode==='edges'?'OPEN ENDS':boundary==='open'?'OPEN CHAIN':'PERIODIC RING'}</span></div>
          {mode==='edges'?
            <>
              <div className="q2-spin-sites" role="img" aria-label={'Site magnetization profile for odd open N='+edge.n}>
                {edge.site_magnetization.map((m,i)=><div key={i} className="q2-spin-site">
                  <div className={'q2-spin-circle '+(i===0||i===edge.n-1?'end':'')} style={{opacity:.65+Math.min(.35,Math.abs(m)*.5)}}>{m>=0?'+':'−'}</div>
                  <strong>{fixed(m)}</strong><small>SITE {i+1}</small>
                </div>)}
              </div>
              <div className="q2-measures">
                <div><small>ABSOLUTE WEIGHT AT ENDS</small><strong>{(100*edge.edge_absolute_fraction).toFixed(2)}%</strong></div>
                <div><small>UNIFORM DISTRIBUTION REFERENCE</small><strong>{(100*edge.uniform_fraction_reference).toFixed(2)}%</strong></div>
              </div>
              <p className="q2-explain">The signed site expectations sum to M=+1 and show alternating local signs. A higher absolute fraction at the ends than a uniform reference is a finite-state fingerprint, <strong>not a measurement of two fractional edge spins.</strong></p>
            </>
            :
            <>
              <div className="q2-observables">
                <div><small>STRING CORRELATOR Oᶻ (0, N−2)</small><strong>{fixed(string.string_zz)}</strong><span>Nonlocal parity factor included</span></div>
                <div><small>ORDINARY TWO-POINT Cᶻ (0, N−2)</small><strong>{fixed(string.two_point_zz)}</strong><span>Exactly the same pair of sites</span></div>
              </div>
              <div className="q2-compare">
                <div className="q2-meter"><span>STRING</span><b style={{width:Math.min(100,Math.abs(string.string_zz)*190)+'%'}}/></div>
                <div className="q2-meter alt"><span>TWO-POINT</span><b style={{width:Math.min(100,Math.abs(string.two_point_zz)*190)+'%'}}/></div>
              </div>
              <p className="q2-explain"><strong>The periodic ring does not make the string signal vanish.</strong> For this N, the {boundary==='open'?'periodic':'open'} geometry produces {fixed(alternative.string_zz)}. A nonzero finite-chain string correlator alone is not a topological-phase test.</p>
            </>
          }
        </div>
      </article>
      <article className="q2-panel">
        <div className="card-bar"><span>FINITE MODEL CONTROLS</span><small>SIMULATED / NONE</small></div>
        <div className="q2-content">
          <fieldset className="q2-fieldset"><legend>Chain length</legend>
            <div className="q2-options">{options.map(k=><button type="button" key={k} className={k===n?'selected':''} aria-pressed={k===n} onClick={()=>setN(k)}>N={k}</button>)}</div>
          </fieldset>
          {mode==='string'&&<fieldset className="q2-fieldset"><legend>Boundary geometry</legend><label><input type="radio" name="q2-boundary" checked={boundary==='open'} onChange={()=>setBoundary('open')}/> Open, exposed ends</label><label><input type="radio" name="q2-boundary" checked={boundary==='periodic'} onChange={()=>setBoundary('periodic')}/> Periodic, closed ring</label></fieldset>}
          <div className="q2-trap">
            <ShieldAlert size={22}/>
            <div><strong>{mode==='edges'?'What the profile does NOT establish':'The full-endpoint trap'}</strong>
              {mode==='edges'?<p>This is a local expectation in a chosen finite magnetization sector, not evidence of superconducting response or an asymptotic fractional boundary mode.</p>:
                <p>In fixed M=0, the full end-to-end longitudinal string equals the ordinary two-point correlation. QP2 deliberately probes sites 0 and N−2 instead. Its all-zero product-state reference is trivial, not a matched control Hamiltonian.</p>}
            </div>
          </div>
          <div className="q2-origin"><b>PROVENANCE</b><span>SIMULATED · AUTHORITY NONE · ATTESTED FALSE</span><small>Eigenstate calculations are precomputed with the QP1 Python Hamiltonian. No in-browser diagonalization, trained-model inference, superconductivity, or independent physical measurements.</small></div>
          <a className="q2-link" href={REPO+'/blob/main/docs/QP2_PROTOCOL.md'} target="_blank" rel="noopener noreferrer">Read frozen QP2 protocol <ArrowUpRight size={16}/></a>
          <a className="q2-link" href={REPO+'/blob/main/web/src/data/qp2-reference.json'} target="_blank" rel="noopener noreferrer">Inspect read-only calculations <ArrowUpRight size={16}/></a>
        </div>
      </article>
    </div>
  </section>;
}
