import { useState } from 'react';
import { ArrowUpRight, ClipboardList, FlaskConical, LockKeyhole, ShieldCheck } from 'lucide-react';
import mission from '../../missions/qp5-d0-matched-controls.json';
import './discovery.css';

const phases = [
  ['01', 'QUESTION', 'A defined, falsifiable research question'],
  ['02', 'CANDIDATES', 'Competing hypotheses and predeclared tests'],
  ['03', 'RUN', 'Explicitly approved, bounded local calculation'],
  ['04', 'CHALLENGE', 'Matched controls and numerical cross-check'],
  ['05', 'RECEIPT', 'Create-only artifact and full replay verification']
];

export default function DiscoveryLab() {
  const [selected, setSelected] = useState(mission.candidates[0].id);
  const active = mission.candidates.find(candidate => candidate.id === selected);
  return <section className="shell section discovery-lab" id="discovery">
    <div className="discovery-kicker"><FlaskConical size={17}/> D0 · GOVERNED DISCOVERY PROTOCOL <span>LOCAL / READ ONLY</span></div>
    <div className="discovery-head">
      <div>
        <h2>Curiosity needs <em>controls.</em></h2>
        <p>Turn a question into competing, falsifiable candidates. Then run a bounded experiment, challenge the result, and preserve a replayable receipt. No trading bots. No scientific shortcuts.</p>
      </div>
      <div className="discovery-badge"><LockKeyhole size={19}/><strong>SPECIFIED</strong><small>Not executed by this web page</small></div>
    </div>
    <div className="discovery-phases" aria-label="Discovery protocol stages">
      {phases.map(([number, title, detail]) =>
        <div className="discovery-phase" key={number}>
          <small>{number} / {title}</small><span>{detail}</span>
        </div>
      )}
    </div>
    <div className="discovery-panels">
      <article className="discovery-card">
        <p className="discovery-overline"><ClipboardList size={16}/> FIRST FROZEN MISSION · QP5</p>
        <h3>{mission.question}</h3>
        <div className="discovery-options" aria-label="Select a candidate hypothesis">
          {mission.candidates.map((candidate) =>
            <button key={candidate.id} type="button"
              className={selected === candidate.id ? 'discovery-choice active' : 'discovery-choice'}
              onClick={() => setSelected(candidate.id)} aria-pressed={selected === candidate.id}>
              <strong>{candidate.id.startsWith('C1') ? 'C1' : 'C2'}</strong>
              <span>{candidate.id.startsWith('C1') ? 'High-D hypothesis' : 'Invariance null control'}</span>
            </button>
          )}
        </div>
        <div className="discovery-candidate" aria-live="polite">
          <small>DECLARED CANDIDATE · NOT A RESULT</small>
          <p>{active.statement}</p>
          <strong>Falsifier</strong><p>{active.falsifier}</p>
        </div>
      </article>
      <aside className="discovery-card discovery-guard">
        <p className="discovery-overline"><ShieldCheck size={16}/> PERMISSION FIREWALL</p>
        <h3>Evidence before promotion.</h3>
        <div className="discovery-facts">
          <div><span>Source</span><b>Frozen QP5 numerical model</b></div>
          <div><span>Bounded scope</span><b>48 rows · 12 matched pairs</b></div>
          <div><span>Adversary</span><b>Null candidate + QP4 energy check</b></div>
          <div><span>Operator approval</span><b>Mandatory before local run</b></div>
          <div><span>Remote calls / publication</span><b>Not permitted</b></div>
          <div><span>Scientific authority</span><b>NONE · SIMULATED</b></div>
        </div>
        <p className="discovery-caution">This is a declared research mission, not a live AI agent or measured physics. Running, receipt verification and approvals happen locally using Python.</p>
        <a href="https://github.com/MichaelWave369/PhiFieldLab/blob/main/docs/D0_DISCOVERY_PROTOCOL.md"
          target="_blank" rel="noopener noreferrer">Read D0 protocol and commands <ArrowUpRight size={16}/></a>
      </aside>
    </div>
  </section>;
}
