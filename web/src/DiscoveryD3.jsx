import { ArrowUpRight, Container, FileCheck2, LockKeyhole, ShieldAlert } from 'lucide-react';
import policy from '../../src/phifieldlab/schemas/d3_policy.json';
import './discovery-d3.css';

const controlRows = [
  ['Network', 'Disabled at the container boundary'],
  ['Filesystem', 'Read-only root; isolated temporary memory filesystem'],
  ['Privileges', 'Nonroot user, no added Linux capabilities'],
  ['Resources', '128 MiB memory, 1 CPU, 32 processes'],
  ['Provenance', 'Mission SHA-256 + exact container image ID'],
  ['Reproducibility', 'New isolated worker for every replay']
];
export default function DiscoveryD3() {
  return <section className="shell section d3-cleanroom" id="research-cleanroom">
    <div className="d3-header">
      <div>
        <p className="d3-overline"><Container size={17}/> DISCOVERY D3 / RESEARCH CLEANROOM</p>
        <h2>Permission before <em>execution.</em></h2>
        <p>Take the frozen D2 networking toy into a restricted local Linux container. Only its reviewed worker can run. D3 must pass Docker preflight and receive explicit local approval, and the web exhibit never runs code.</p>
      </div>
      <div className="d3-no-run"><LockKeyhole size={20}/><b>LOCAL OPT-IN ONLY</b><small>NO CLOUD EXECUTION</small></div>
    </div>
    <div className="d3-columns">
      <article className="d3-card">
        <h3><FileCheck2 size={18}/> Allowlisted capabilities</h3>
        <div className="d3-controls">{controlRows.map(([key,value]) =>
          <div key={key}><span>{key}</span><strong>{value}</strong></div>
        )}</div>
        <p className="d3-footnote">Runner policy: {policy.protocol} · Adapter: {policy.adapter}</p>
      </article>
      <aside className="d3-card">
        <h3><ShieldAlert size={18}/> Security claims remain bounded</h3>
        <p>Container restrictions are enforced by Docker and the Linux kernel when that backend is available. This is a meaningful improvement over a plain Python subprocess, not a hardened multi-tenant sandbox or proof against container escapes.</p>
        <p>Unknown missions, remote Docker contexts, unsupported host controls, mutable image tags, network mounts and unpublished results are all rejected or withheld.</p>
        <p><b>SIMULATED · AUTHORITY NONE · UNATTESTED</b></p>
        <a href="https://github.com/MichaelWave369/PhiFieldLab/blob/main/docs/D3_CLEANROOM.md"
          target="_blank" rel="noopener noreferrer">Read local setup and frozen approval contract <ArrowUpRight size={16}/></a>
      </aside>
    </div>
  </section>;
}
