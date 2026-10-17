import { useState } from 'react';
import QuantumParityLab from './QuantumParityLab.jsx';
import SpinChainLab from './SpinChainLab.jsx';
import EdgeFingerprintsLab from './EdgeFingerprintsLab.jsx';
import MatchedHamiltonianLab from './MatchedHamiltonianLab.jsx';
import SpectralGapLab from './SpectralGapLab.jsx';
import SchmidtSpectrumLab from './SchmidtSpectrumLab.jsx';
import { Activity, ArrowDown, ArrowRight, ArrowUpRight, Check, ClipboardCopy, Cpu, Database, FileJson, FlaskConical, Github, Layers, LockKeyhole, Menu, Network, RotateCcw, ShieldCheck, SlidersHorizontal, UploadCloud, X } from 'lucide-react';
import reportSample from '../../artifacts/sample-e0/report.json';
import config from '../../artifacts/sample-e0/config.json';
import manifest from '../../artifacts/sample-e0/manifest.json';

const REPO = 'https://github.com/MichaelWave369/PhiFieldLab';
const PAGES = 'https://michaelwave369.github.io/PhiFieldLab/';
const pct = n => (n * 100).toFixed(1) + '%';
const number = n => n.toLocaleString('en-US');
function Tag({ children }) { return <span className="tag">{children}</span>; }
function Heading({ index, eyebrow, title, desc }) {
  return <div className="section-heading"><div className="eyebrow"><b>{index}</b><span />{eyebrow}</div><h2>{title}</h2><p>{desc}</p></div>;
}
function Cycle({ nodes, defect }) {
  const points = Array.from({ length: nodes }, (_, i) => {
    const a = (Math.PI * 2 * i / nodes) - Math.PI/2;
    return { x: 250 + 142*Math.cos(a), y: 204 + 142*Math.sin(a) };
  });
  const potentials = points.map((_,i) => Math.sin(i*1.91+0.3)*0.85+Math.cos(i*.77)*.35);
  const edges = points.map((p,i) => {
    const q = points[(i+1)%nodes];
    const dx = q.x-p.x, dy = q.y-p.y, length = Math.hypot(dx,dy);
    const edge = potentials[(i+1)%nodes]-potentials[i]+(i===nodes-1?defect:0);
    return { start:{x:p.x+dx/length*26,y:p.y+dy/length*26}, end:{x:q.x-dx/length*28,y:q.y-dy/length*28}, edge, mid:{x:(p.x+q.x)/2,y:(p.y+q.y)/2} };
  });
  return <svg className="cycle-svg" viewBox="0 0 500 410" role="img" aria-label={'Synthetic directed cycle with '+nodes+' nodes and exact residual '+defect.toFixed(2)}>
    <defs><radialGradient id="halo"><stop stopColor="#2b6e72" stopOpacity=".31"/><stop offset="1" stopColor="#091923" stopOpacity="0"/></radialGradient><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#71e8cb"/></marker></defs>
    <circle cx="250" cy="204" r="199" fill="url(#halo)"/>
    {[55,102,178,196].map(n=><circle key={n} cx="250" cy="204" r={n} fill="none" stroke="#609e9e" strokeOpacity=".22" strokeDasharray={n>170?'4 8':''}/>)}
    <path d="M17 204H483M250 0V408" stroke="#7de6d0" strokeOpacity=".08"/>
    {edges.map((edge,i)=><g key={i}><line x1={edge.start.x} y1={edge.start.y} x2={edge.end.x} y2={edge.end.y} stroke={i===nodes-1&&defect>.4?'#e8ae77':'#65d9c2'} strokeWidth="2.5" markerEnd="url(#arrow)" opacity=".84"/>{nodes<=6&&<text x={edge.mid.x} y={edge.mid.y} fill="#b2cfcd" textAnchor="middle" fontSize="12" dominantBaseline="central">{edge.edge.toFixed(2)}</text>}</g>)}
    {points.map((p,i)=><g key={i}><circle cx={p.x} cy={p.y} r="24" fill="#112a34" stroke="#74ebd3" strokeWidth="1.7"/><circle cx={p.x} cy={p.y} r="17" fill="#234c50" fillOpacity=".7"/><text x={p.x} y={p.y+5} textAnchor="middle" fontSize="14" fontWeight="700" fill="#eafffa">{i+1}</text></g>)}
    <text x="250" y="185" textAnchor="middle" fontSize="11" letterSpacing="2" fill="#8db5bb">Σ TRANSPORT</text>
    <text x="250" y="226" textAnchor="middle" fontSize="36" fill={defect>.4?'#ffd0a0':'#a1ffdf'} fontWeight="750">{defect.toFixed(2)}</text>
    <text x="250" y="247" textAnchor="middle" fontSize="11" fill="#91b2b9">EXACT RESIDUAL</text>
  </svg>;
}
function Score({label,caption,value,color}) {
  return <div className="score"><div className="score-head"><div><strong>{label}</strong><small>{caption}</small></div><b>{pct(value)}</b></div><div className="bar" role="img" aria-label={label+': '+pct(value)}><div className={'bar-fill '+color} style={{width:Math.min(100,Math.max(0,value*100))+'%'}}/></div></div>;
}
function validateLocal(r) {
  const t=r?.heldout_test;
  return r?.protocol==='PHIFIELD_E0_CYCLE_TRANSPORT_V1'&&r?.origin==='SIMULATED'&&r?.authority==='NONE'
    &&Number.isSafeInteger(t?.n)&&t.n>0&&t.n<100000000
    &&Array.isArray(t.size_range)&&t.size_range.length===2&&t.size_range.every(Number.isFinite)
    &&[t?.learned?.accuracy,t?.exact_closure_rule?.accuracy,t?.single_edge_negative_control?.accuracy].every(x=>Number.isFinite(x)&&x>=0&&x<=1)
    &&Number.isFinite(t?.residue_mae)&&t.residue_mae>=0;
}
export default function App(){
  const [nodes,setNodes]=useState(6);
  const [defect,setDefect]=useState(1.1);
  const [report,setReport]=useState(reportSample);
  const [imported,setImported]=useState('');
  const [error,setError]=useState('');
  const [copied,setCopied]=useState('');
  const [view,setView]=useState('all');
  const [menu,setMenu]=useState(false);
  const test=report.heldout_test;
  const exactClosed=Math.abs(defect)<=config.threshold;
  async function handleFile(event){
    const file=event.target.files?.[0]; event.target.value='';
    if(!file)return;
    if(file.size>1024*1024){setError('Maximum file size is 1 MB.');return;}
    try{const obj=JSON.parse(await file.text());if(!validateLocal(obj))throw Error('Invalid E0 simulated report.');setReport(obj);setImported(file.name);setError('');}
    catch(e){setError(e.message||'Invalid JSON file.');}
  }
  async function copyHash(sha){try{await navigator.clipboard.writeText(sha);setCopied('Digest copied.')}catch{setCopied('Clipboard unavailable; use repository view.');}}
  const roadmap=[
    ['E0','Cycle transport','IMPLEMENTED','Original numerical weights, saved checkpoint and replayed synthetic evaluation.'],
    ['E1','Graph generalization','PROPOSED','Message passing, missing edges and genuinely withheld graph topologies.'],
    ['E2','NBG research bridge','PROPOSED','Frozen hypotheses, lineage controls and independently scored comparisons.'],
    ['E3','Scientific data','FUTURE','Licensed physical datasets, established baselines and measured uncertainty.'],
    ['E4','Model ecosystem','FUTURE','Opt-in adapters for PhiStream, PocketMesh and Super Φ.Vessel.']
  ];
  return <div className="page">
    <a className="skip" href="#content">Skip to content</a>
    <div className="ribbon"><i/> OPEN RESEARCH · v0.1 / E0 <span>SIMULATED / AUTHORITY NONE</span></div>
    <header className="site-header"><div className="shell nav">
      <a className="logo" href="#top"><span className="logo-mark">Φ</span><span>FIELD<em>LAB</em><small>INDEPENDENT MODEL RESEARCH</small></span></a>
      <nav className={menu?'links open':'links'} aria-label="Main navigation">{[['Experiment','#experiment'],['Quantum Parity','#quantum-parity'],['Spin-1 Chains','#spin-chain'],['Benchmarks','#benchmarks'],['Evidence','#evidence'],['Roadmap','#roadmap']].map(([t,h])=><a key={t} href={h} onClick={()=>setMenu(false)}>{t}</a>)}</nav>
      <a className="github-link" href={REPO} target="_blank" rel="noopener noreferrer"><Github size={17}/> Repository <ArrowUpRight size={15}/></a>
      <button className="menu-toggle" onClick={()=>setMenu(!menu)} aria-label={menu?'Close menu':'Open menu'} aria-expanded={menu}>{menu?<X/>:<Menu/>}</button>
    </div></header>
    <main id="content">
      <section className="shell hero" id="top"><div className="hero-copy">
        <p className="kicker"><i/> SCIENTIFIC AI, BUILT IN THE OPEN</p>
        <h1>Science needs <em>receipts.</em></h1>
        <p className="hero-desc">Independent models. Original learned weights. Reproducible experiments. Every claim tied to the evidence, even when the experiment proves less than we hoped.</p>
        <div className="buttons"><a className="btn primary" href="#experiment">Explore E0 <ArrowRight size={18}/></a><a className="btn ghost" href="#benchmarks">See the results <ArrowDown size={18}/></a></div>
        <div className="tag-group"><Tag>E0 · SYNTHETIC</Tag><Tag>ORIGINAL WEIGHTS</Tag><Tag>NO CLOUD API</Tag></div>
      </div><div className="hero-art" aria-hidden="true"><div className="grid-overlay"/><div className="ring ring-a"/><div className="ring ring-b"/><div className="ring ring-c"/><div className="dot dot-a"/><div className="dot dot-b"/><div className="dot dot-c"/><div className="art-core"><span>Φ</span><small>FIELD / 001</small></div><div className="art-caption">STRUCTURE // SIGNAL // EVIDENCE <span>FIG 01</span></div></div></section>
      <section className="shell stats" aria-label="Bundled experimental results">
        {[['MODEL ACCURACY',pct(reportSample.heldout_test.learned.accuracy),'Held-out synthetic sizes'],['TEST EXAMPLES',number(reportSample.heldout_test.n),'Cycle lengths 7–10'],['EXACT BASELINE',pct(reportSample.heldout_test.exact_closure_rule.accuracy),'Ties the trained model'],['WEAK CONTROL',pct(reportSample.heldout_test.single_edge_negative_control.accuracy),'Intentionally limited']].map(([k,v,d])=><div className="stat" key={k}><small>{k}</small><strong>{v}</strong><p>{d}</p></div>)}
      </section>
      <section className="shell section" id="experiment">
        <Heading index="01" eyebrow="INTERACTIVE EXPERIMENT" title={<>Play with <em>closure.</em></>} desc="Change the cycle and inject a transport defect. Watch a known exact arithmetic rule respond. This is an interactive mathematical illustration, not inference using trained E0 weights."/>
        <div className="experiment">
          <article className="graph-card"><div className="card-bar"><span><i className="led"/> DIRECTED CYCLE / SYNTHETIC</span><small>EXACT ARITHMETIC</small></div><Cycle nodes={nodes} defect={defect}/><div className="legend"><span><i className="node-key"/> Nodes</span><span><i className="edge-key"/> Signed transport</span><span>Σ = {defect.toFixed(2)}</span></div></article>
          <div className="controls"><div className="card-bar"><span><SlidersHorizontal size={16}/> EXPERIMENT CONTROLS</span><button className="icon-button" onClick={()=>{setNodes(6);setDefect(1.1)}} title="Reset controls" aria-label="Reset controls"><RotateCcw size={17}/></button></div>
            <div className="field"><div><label htmlFor="nodes">Cycle nodes</label><b>{nodes}</b></div><input id="nodes" type="range" min="3" max="10" step="1" value={nodes} onChange={e=>setNodes(+e.target.value)}/><aside><span>3 NODES</span><span>10 NODES</span></aside></div>
            <div className="field"><div><label htmlFor="defect">Injected residue</label><b>{defect.toFixed(2)}</b></div><input id="defect" type="range" min="0" max="1.5" step=".05" value={defect} onChange={e=>setDefect(+e.target.value)}/><aside><span>0.00</span><span>1.50</span></aside></div>
            <div className={exactClosed?'readout closed':'readout open'}><small>EXACT CLOSURE TEST</small><strong>{exactClosed?'WITHIN THRESHOLD':'DEFECT DETECTED'}</strong><span>|Σ edge transport| {exactClosed?'≤':'>'} {config.threshold.toFixed(2)}</span></div>
            <p className="disclaimer"><ShieldCheck size={17}/> Edge values telescope around a constructed cycle. No neural checkpoint runs in this browser.</p>
          </div>
        </div>
      </section>
      <QuantumParityLab/>
      <SpinChainLab/>
      <EdgeFingerprintsLab/>
      <MatchedHamiltonianLab/>
      <SpectralGapLab/>
      <SchmidtSpectrumLab/>
      <section className="shell section" id="benchmarks">
        <Heading index="02" eyebrow="MEASURED RESULTS" title={<>Numbers, not <em>narratives.</em></>} desc="Reported scores come from the bundled E0 experiment, or a locally loaded report you explicitly select. Imported files are not independently attested."/>
        <div className="results">
          <article className="scores card"><div className="card-bar"><span><Activity size={18}/> HELD-OUT CLASSIFICATION</span><small>E0 / TEST</small></div>
            <div className="score-list"><Score label="Learned E0 model" caption="Original trained weights" value={test.learned.accuracy} color="green"/><Score label="Exact closure rule" caption="Known arithmetic baseline" value={test.exact_closure_rule.accuracy} color="blue"/><Score label="Single-edge negative control" caption="Deliberately weak baseline" value={test.single_edge_negative_control.accuracy} color="orange"/></div>
            <div className="score-foot"><span>N = {number(test.n)}</span><span>Lengths {test.size_range[0]}–{test.size_range[1]}</span><span>Residue MAE {test.residue_mae.toFixed(5)}</span></div>
          </article>
          <aside className="finding card"><div className="round-icon"><FlaskConical size={23}/></div><p className="kicker">THE IMPORTANT BIT</p><h3>The exact rule <em>also scores 100%.</em></h3><p>This synthetic benchmark shows that learned weights can reproduce its closure behavior. It does not demonstrate new physics, superiority to mathematics, or general reasoning on unseen graph topologies.</p><a href={REPO+'/blob/main/docs/E0_PROTOCOL.md'} target="_blank" rel="noopener noreferrer">Read the frozen E0 protocol <ArrowUpRight size={16}/></a></aside>
        </div>
        <div className="datasets">{[['TRAIN',config.n_train,'Lengths 3–6',<Cpu/>],['VALIDATE',config.n_validation,'Lengths 3–6',<Layers/>],['TEST',config.n_test,'Lengths 7–10',<Database/>]].map(([name,n,range,icon])=><div key={name} className="dataset"><span>{icon}</span><div><small>{name}</small><strong>{number(n)} <i>examples</i></strong><p>{range}</p></div></div>)}</div>
      </section>
      <section className="shell section" id="evidence">
        <Heading index="03" eyebrow="CHECKPOINT & EVIDENCE" title={<>Trust the method. <em>Check the files.</em></>} desc="The sample includes a safetensors checkpoint, training settings, a report and SHA-256 digests. A matching hash establishes file consistency, not independent provenance."/>
        <div className="evidence">
          <article className="card artifacts"><div className="card-bar"><span>ARTIFACT REGISTER / SAMPLE E0</span><small className="warn">UNATTESTED</small></div>
            <div className="artifact-list">{Object.entries(manifest.sha256).map(([name,hash])=><div className="artifact" key={name}><FileJson size={21}/><div><strong>{name}</strong><code>{hash.slice(0,18)}...{hash.slice(-9)}</code></div><button className="icon-button" onClick={()=>copyHash(hash)} aria-label={'Copy hash for '+name} title="Copy digest"><ClipboardCopy size={18}/></button></div>)}</div>
            <p className="copy-status" role="status">{copied||'The hashes shown are values recorded in the committed manifest.'}</p><a className="artifact-link" href={REPO+'/tree/main/artifacts/sample-e0'} target="_blank" rel="noopener noreferrer">View the model artifacts <ArrowUpRight size={17}/></a>
          </article>
          <article className="card provenance"><p className="kicker"><LockKeyhole size={20}/> CLAIM FIREWALL</p><div className="matrix">{[['ORIGIN','SIMULATED'],['AUTHORITY','NONE'],['ATTESTED','NO'],['WEIGHTS','SAFETENSORS']].map(([k,v])=><div key={k}><small>{k}</small><strong>{v}</strong></div>)}</div><p>The original weights were saved during CPU training and are replayable through the Python verifier. These receipts do not prove scientific validity or that an independent observer witnessed training.</p><div className="provenance-bottom"><Check size={16}/> Separate simulation, observation, inference and proof.</div></article>
        </div>
        <div className="import-row"><div><UploadCloud size={24}/><div><strong>Inspect your local E0 report</strong><p>Read a JSON report from your own run. It stays in your browser tab; nothing is uploaded.</p></div></div><div className="import-buttons"><label htmlFor="report-file" className="btn ghost small"><FileJson size={16}/> Select JSON file</label><input className="visually-hidden" id="report-file" type="file" accept=".json,application/json" onChange={handleFile}/>{imported&&<button className="reset" onClick={()=>{setReport(reportSample);setImported('');setError('')}}>Reset sample</button>}</div></div>
        {(error||imported)&&<p className={error?'import-state error':'import-state'} role="status">{error||('Showing locally imported, unverified report: '+imported+'. The header and datasets still describe the bundled sample.')}</p>}
      </section>
      <section className="shell section" id="roadmap">
        <Heading index="04" eyebrow="THE EXPERIMENT LADDER" title={<>A bigger field <em>ahead.</em></>} desc="Each future research gate must earn its own evidence. E1 is real graph learning with genuinely withheld topologies, not just a larger toy classifier."/>
        <div className="roadmap">{roadmap.filter((r)=>view==='all'||(view==='implemented'?r[2]==='IMPLEMENTED':r[2]!=='IMPLEMENTED')).map(([gate,title,state,desc])=><article className={state==='IMPLEMENTED'?'step done':'step'} key={gate}><div><strong>{gate}</strong>{state==='IMPLEMENTED'?<Check size={20}/>:<Network size={20}/>}</div><h3>{title}</h3><p>{desc}</p><small>{state}</small></article>)}</div>
        <div className="filter" aria-label="Filter research gates">{[['all','ALL GATES'],['implemented','IMPLEMENTED'],['planned','PLANNED']].map(([key,name])=><button key={key} className={view===key?'selected':''} onClick={()=>setView(key)}>{name}</button>)}</div>
      </section>
      <section className="shell outro"><div><p className="kicker">OPEN QUESTIONS · OPEN LABORATORY</p><h2>Ledger above ego.<br/><em>Evidence above everything.</em></h2><p>Independent research isn't the absence of mistakes. It's the practice of making them visible, measurable, and correctable.</p><a className="btn primary" href={REPO} target="_blank" rel="noopener noreferrer"><Github size={18}/> Explore code and weights <ArrowUpRight size={18}/></a></div><div aria-hidden="true">Φ</div></section>
    </main>
    <footer className="shell footer"><b>Φ FIELD LAB · E0</b><span>SIMULATED DATA / NO PHYSICAL VALIDATION</span><a href={REPO} target="_blank" rel="noopener noreferrer">GITHUB <ArrowUpRight size={14}/></a></footer>
  </div>;
}
