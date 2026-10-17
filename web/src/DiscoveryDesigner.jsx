import { useMemo, useRef, useState } from 'react';
import { AlertTriangle, ArrowUpRight, CheckCircle2, ClipboardList, Download, FileJson,
  LockKeyhole, Plus, RotateCcw, ShieldCheck, UploadCloud, XCircle } from 'lucide-react';
import { DOMAIN_OPTIONS, formatDraft, newDraft, validateDraft } from './d1Mission.js';
import './discovery-designer.css';

const EVAL_FIELDS = [
  ['method', 'Test method'], ['metric', 'Outcome measure / rubric'], ['baseline', 'Baseline'],
  ['negative_control', 'Negative control'], ['success_criterion', 'Success criterion'],
  ['failure_criterion', 'Failure criterion'], ['uncertainty', 'Uncertainty and limits']
];

function Field({ title, value, onChange, multiline = false, note }) {
  return <label className="d1-field">
    <span>{title}</span>
    {multiline
      ? <textarea rows={3} value={value} onChange={event => onChange(event.target.value)} />
      : <input type="text" value={value} onChange={event => onChange(event.target.value)} />}
    {note && <small>{note}</small>}
  </label>;
}

export default function DiscoveryDesigner() {
  const [draft, setDraft] = useState(() => newDraft('networking'));
  const [message, setMessage] = useState('');
  const [showJson, setShowJson] = useState(false);
  const fileInput = useRef(null);
  const validation = useMemo(() => validateDraft(draft), [draft]);

  function edit(section, property, value) {
    setDraft(prev => ({ ...prev, [section]: { ...prev[section], [property]: value } }));
    setMessage('');
  }
  function editTop(property, value) {
    setDraft(prev => ({ ...prev, [property]: value }));
    setMessage('');
  }
  function editHypothesis(index, key, value) {
    setDraft(prev => ({
      ...prev,
      candidates: prev.candidates.map((candidate, i) =>
        i === index ? { ...candidate, [key]: value } : candidate)
    }));
    setMessage('');
  }
  function reset(domain) {
    setDraft(newDraft(domain));
    setMessage('Loaded a proposal template. No research has been run.');
  }
  function addHypothesis() {
    setDraft(prev => ({
      ...prev,
      candidates: [...prev.candidates, {
        id: 'H' + (prev.candidates.length + 1),
        hypothesis: '', prediction: '', falsifier: ''
      }]
    }));
    setMessage('');
  }
  function removeHypothesis() {
    setDraft(prev => ({ ...prev, candidates: prev.candidates.slice(0, -1) }));
    setMessage('');
  }
  function download() {
    if (!validation.ok) { setMessage('Fix the validation findings before exporting.'); return; }
    const blob = new Blob([formatDraft(draft)], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = draft.mission_id + '.json';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
    setMessage('Proposal JSON exported locally. Export is not approval or execution.');
  }
  async function importFile(event) {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;
    if (file.size > 128 * 1024) { setMessage('Import refused: file exceeds 128 KiB.'); return; }
    try {
      const imported = JSON.parse(await file.text());
      const checked = validateDraft(imported);
      if (!checked.ok) {
        setMessage('Import refused: ' + checked.errors.slice(0, 2).join(' • '));
        return;
      }
      setDraft(imported);
      setMessage('Local proposal loaded and validated. Not approved or executed.');
    } catch {
      setMessage('Import refused: not a valid D1 JSON proposal.');
    }
  }
  return <section className="shell section d1-designer" id="mission-designer">
    <div className="d1-title">
      <div>
        <p className="d1-eyebrow"><ClipboardList size={18} /> DISCOVERY D1 / MISSION DESIGNER</p>
        <h2>Ask better questions. <em>Keep the receipts.</em></h2>
        <p>Design a rigorous research proposal across scientific, technical and creative domains. This browser drafts and validates plans only. It never executes experiments, contacts servers, or grants approvals.</p>
      </div>
      <div className="d1-status"><LockKeyhole size={18}/><strong>PROPOSAL ONLY</strong><small>NO EXECUTION GRANT</small></div>
    </div>
    <div className="d1-workbench">
      <div className="d1-form">
        <div className="d1-group">
          <div className="d1-group-header"><b>01 / Research question</b><span>Choose a starting point</span></div>
          <label className="d1-field"><span>Domain / template</span>
            <select value={draft.domain} onChange={event => reset(event.target.value)}>
              {DOMAIN_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
          <div className="d1-two">
            <Field title="Mission ID" value={draft.mission_id} onChange={value => editTop('mission_id', value)} note="Lowercase letters, digits and hyphens. No spaces."/>
            <Field title="Title" value={draft.title} onChange={value => editTop('title', value)} />
          </div>
          <Field title="Research question" value={draft.question} multiline onChange={value => editTop('question', value)}/>
          <div className="d1-two">
            <Field title="In scope" value={draft.scope.in_scope} multiline onChange={value => edit('scope','in_scope',value)}/>
            <Field title="Outside scope" value={draft.scope.out_of_scope} multiline onChange={value => edit('scope','out_of_scope',value)}/>
          </div>
        </div>
        <div className="d1-group">
          <div className="d1-group-header"><b>02 / Competing explanations</b><span>2 to 4 hypotheses</span></div>
          {draft.candidates.map((candidate, index) =>
            <div key={candidate.id} className="d1-hypothesis">
              <div className="d1-hypothesis-head"><strong>{candidate.id}</strong><small>Predeclare before testing</small></div>
              <Field title="Hypothesis" value={candidate.hypothesis} multiline onChange={value => editHypothesis(index, 'hypothesis', value)}/>
              <Field title="Observable prediction" value={candidate.prediction} multiline onChange={value => editHypothesis(index, 'prediction', value)}/>
              <Field title="What would disprove it?" value={candidate.falsifier} multiline onChange={value => editHypothesis(index, 'falsifier', value)}/>
            </div>
          )}
          <div className="d1-actions">
            <button type="button" onClick={addHypothesis} disabled={draft.candidates.length >= 4}><Plus size={16}/> Add hypothesis</button>
            <button type="button" onClick={removeHypothesis} disabled={draft.candidates.length <= 2}>Remove last</button>
          </div>
        </div>
        <details className="d1-group d1-details" open>
          <summary>03 / Evidence and evaluation</summary>
          <div className="d1-detail-body">
            <label className="d1-field"><span>Claimed source kind (not an attestation)</span>
              <select value={draft.evidence.source_kind} onChange={event => edit('evidence','source_kind',event.target.value)}>
                {['UNKNOWN','SIMULATED','LITERATURE','OBSERVED'].map(value => <option key={value}>{value}</option>)}
              </select>
            </label>
            <Field title="Source description" multiline value={draft.evidence.source_description} onChange={value => edit('evidence','source_description',value)}/>
            <Field title="How could evidence be independently replayed?" multiline value={draft.evidence.replay_plan} onChange={value => edit('evidence','replay_plan',value)}/>
            {EVAL_FIELDS.map(([key,label]) => <Field key={key} title={label} multiline value={draft.evaluation[key]} onChange={value => edit('evaluation',key,value)}/>)}
          </div>
        </details>
        <details className="d1-group d1-details" open>
          <summary>04 / Budget, risk and stopping conditions</summary>
          <div className="d1-detail-body">
            <div className="d1-two">
              <label className="d1-field"><span>Future runtime cap (minutes)</span>
                <input type="number" min="1" max="240" step="1" value={draft.resources.max_runtime_minutes}
                  onChange={event => edit('resources','max_runtime_minutes', Number(event.target.value))}/>
              </label>
              <label className="d1-field"><span>Future compute-unit cap</span>
                <input type="number" min="1" max="100" step="1" value={draft.resources.max_compute_units}
                  onChange={event => edit('resources','max_compute_units', Number(event.target.value))}/>
              </label>
            </div>
            <label className="d1-field"><span>Risk classification</span>
              <select value={draft.risk.level} onChange={event => edit('risk','level',event.target.value)}>
                {['LOW','MODERATE','HIGH'].map(value => <option key={value}>{value}</option>)}
              </select>
            </label>
            <Field title="Potential harms" multiline value={draft.risk.potential_harms} onChange={value => edit('risk','potential_harms',value)}/>
            <Field title="When must a future experiment stop?" multiline value={draft.risk.stop_condition} onChange={value => edit('risk','stop_condition',value)}/>
          </div>
        </details>
      </div>
      <aside className="d1-inspector">
        <div className="d1-panel">
          <h3><ShieldCheck size={18}/> Proposal validation</h3>
          <div className={'d1-validation '+(validation.ok ? 'pass' : 'fail')}>
            {validation.ok ? <CheckCircle2 size={21}/> : <XCircle size={21}/>}
            <span>{validation.ok ? 'SCHEMA VALID · NOT APPROVED' : validation.errors.length + ' VALIDATION FINDINGS'}</span>
          </div>
          {validation.ok
            ? <p>All required fields, candidate controls, and restricted permissions pass the draft contract. Scientific merit has not been evaluated.</p>
            : <ul className="d1-errors">{validation.errors.slice(0, 8).map((error, index) => <li key={index}>{error}</li>)}</ul>}
        </div>
        <div className="d1-panel">
          <h3><LockKeyhole size={18}/> Hard permission boundaries</h3>
          <div className="d1-rules">
            <div><span>Local experiment execution</span><strong>DENIED</strong></div>
            <div><span>Internet / outside systems</span><strong>DENIED</strong></div>
            <div><span>Repository writes / publication</span><strong>DENIED</strong></div>
            <div><span>External spending</span><strong>$0</strong></div>
            <div><span>Human review</span><strong>REQUIRED</strong></div>
          </div>
          <p><AlertTriangle size={15}/> Resource caps are proposed limits, not permission to consume resources. External actions require a separately reviewed future protocol.</p>
        </div>
        <div className="d1-panel">
          <h3><FileJson size={18}/> Proposal file</h3>
          <div className="d1-actionstack">
            <button type="button" className="d1-export" disabled={!validation.ok} onClick={download}><Download size={17}/> Export JSON proposal</button>
            <button type="button" onClick={() => fileInput.current?.click()}><UploadCloud size={17}/> Import local D1 JSON</button>
            <input ref={fileInput} type="file" accept=".json,application/json" hidden onChange={importFile}/>
            <button type="button" onClick={() => reset(draft.domain)}><RotateCcw size={17}/> Reset template</button>
            <button type="button" onClick={() => setShowJson(!showJson)}><FileJson size={17}/> {showJson ? 'Hide' : 'Preview'} JSON</button>
          </div>
          {message && <p className="d1-feedback" role="status">{message}</p>}
          {showJson && <pre className="d1-json">{formatDraft(draft)}</pre>}
          <a href="https://github.com/MichaelWave369/PhiFieldLab/blob/main/docs/D1_MISSION_DESIGNER.md"
            target="_blank" rel="noopener noreferrer">D1 contract and offline CLI <ArrowUpRight size={15}/></a>
        </div>
      </aside>
    </div>
  </section>;
}
