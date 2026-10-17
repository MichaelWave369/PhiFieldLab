import { useState } from 'react';
import { ArrowUpRight, CheckCircle2, FileJson, FlaskConical, LockKeyhole,
  Network, ShieldAlert, UploadCloud } from 'lucide-react';
import { D2_POLICY, inspectD2Receipt } from './d2Receipt.js';
import './discovery-d2.css';

const milestones = [
  ['01', 'ADMIT', 'Only the reviewed networking proposal, byte for byte'],
  ['02', 'APPROVE', 'Human confirms the exact mission digest'],
  ['03', 'SIMULATE', 'Fixed Python worker with five synthetic workload seeds'],
  ['04', 'CHALLENGE', 'FIFO baseline, fair queue and sham re-run'],
  ['05', 'REPLAY', 'Locally verify create-only receipt against a fresh computation']
];

export default function DiscoveryD2() {
  const [receipt, setReceipt] = useState(null);
  const [status, setStatus] = useState('No receipt selected. The public page never runs experiments.');
  async function inspect(event) {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;
    if (file.size > 128 * 1024) {
      setReceipt(null);
      setStatus('Refused: receipt exceeds 128 KiB.');
      return;
    }
    try {
      const payload = JSON.parse(await file.text());
      const outcome = inspectD2Receipt(payload);
      if (!outcome.ok) {
        setReceipt(null);
        setStatus('Refused: ' + outcome.explanation);
        return;
      }
      setReceipt(outcome);
      setStatus('Structure inspected locally. This is NOT a cryptographic verification, replay, or scientific attestation.');
    } catch {
      setReceipt(null);
      setStatus('Refused: invalid receipt JSON.');
    }
  }
  return <section className="shell section d2-research" id="experiment-runner">
    <div className="d2-heading">
      <div>
        <p className="d2-overline"><FlaskConical size={17}/> DISCOVERY D2 / BOUNDED EXPERIMENT RUNNER</p>
        <h2>Run the model. <em>Challenge the outcome.</em></h2>
        <p>Our first execution adapter evaluates a synthetic queueing question, not a live router. D2 is a separate, locally approved tool. The website can only explain the workflow and inspect an imported receipt.</p>
      </div>
      <div className="d2-static"><LockKeyhole size={21}/><b>NO BROWSER EXECUTION</b><small>SIMULATED · UNATTESTED</small></div>
    </div>
    <div className="d2-stages">{milestones.map(([id,title,desc]) =>
      <div className="d2-stage" key={id}><small>{id} / {title}</small><p>{desc}</p></div>
    )}</div>
    <div className="d2-columns">
      <article className="d2-panel">
        <h3><Network size={19}/> Registered adapter: network-latency toy</h3>
        <p>Compare fixed FIFO to a simplified two-flow fair queue using matched synthetic traces. A repeated FIFO run acts as a sham control. The primary measurement is the latency-sensitive class's p95 delay, not a prediction of actual switch performance.</p>
        <div className="d2-data">
          <div><span>Registered mission</span><strong>{D2_POLICY.mission_id}</strong></div>
          <div><span>Seeds</span><strong>{D2_POLICY.seeds.join(' · ')}</strong></div>
          <div><span>Simulation size</span><strong>{D2_POLICY.ticks_per_seed} ticks × {D2_POLICY.seeds.length}</strong></div>
          <div><span>Queue capacity</span><strong>{D2_POLICY.queue_capacity_packets} packets</strong></div>
          <div><span>Worker deadline</span><strong>{D2_POLICY.max_wall_seconds} seconds</strong></div>
          <div><span>Automatic publishing</span><strong>DENIED</strong></div>
        </div>
        <p className="d2-caveat"><ShieldAlert size={17}/> A separate Python process, temporary directory and timeout do not provide an OS-enforced network or filesystem sandbox. This fixed adapter contains no socket or arbitrary-command functionality.</p>
        <a href="https://github.com/MichaelWave369/PhiFieldLab/blob/main/docs/D2_SYNTHETIC_RUNNER.md"
           target="_blank" rel="noopener noreferrer">View the offline commands and review contract <ArrowUpRight size={15}/></a>
      </article>
      <article className="d2-panel">
        <h3><FileJson size={19}/> Inspect a local D2 receipt</h3>
        <p>Select a JSON receipt produced by the Python runner. This viewer performs limited structural checks only. To verify its contents against a fresh simulation, use the documented offline CLI.</p>
        <label className="d2-import" htmlFor="d2-local-receipt"><UploadCloud size={17}/> Select local receipt JSON</label>
        <input className="visually-hidden" type="file" id="d2-local-receipt"
          accept=".json,application/json" onChange={inspect}/>
        <p className="d2-status" role="status">{status}</p>
        {receipt && <div className="d2-imported">
          <p><CheckCircle2 size={18}/> STRUCTURALLY CONSISTENT · NOT VERIFIED</p>
          <strong>Reported verdict: {receipt.verdict.replaceAll('_', ' ')}</strong>
          <div className="d2-tablewrap"><table>
            <thead><tr><th>Seed</th><th>FIFO p95</th><th>Fair p95</th><th>Change</th><th>Loss gate</th></tr></thead>
            <tbody>{receipt.rows.map(row => <tr key={row.seed}>
              <td>{row.seed}</td><td>{row.baseline.latency_p95_ms} ms</td>
              <td>{row.candidate.latency_p95_ms} ms</td>
              <td>{row.sensitive_p95_reduction_percent.toFixed(1)}%</td>
              <td>{row.loss_not_worse ? 'Pass' : 'Fail'}</td>
            </tr>)}</tbody>
          </table></div>
          <p>Numbers were read from a user-supplied file. Passing this browser check does not prove the file was created by our runner.</p>
        </div>}
      </article>
    </div>
  </section>;
}
