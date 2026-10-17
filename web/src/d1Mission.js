import schema from '../../src/phifieldlab/schemas/d1.schema.json' with { type: 'json' };
import networking from '../../missions/d1-examples/network-switch-latency.json' with { type: 'json' };
import creative from '../../missions/d1-examples/music-arrangement-listener-study.json' with { type: 'json' };
import science from '../../missions/d1-examples/spin-chain-scaling-question.json' with { type: 'json' };

export const DOMAIN_OPTIONS = [
  ['networking', 'Networking'], ['science', 'Science'], ['software', 'Software'],
  ['engineering', 'Engineering'], ['environment', 'Environment'],
  ['creative', 'Creative work'], ['mathematics', 'Mathematics']
];
export const PROTOCOL = 'PHIFIELD_DISCOVERY_D1_MISSION_V1';
const templates = { networking, creative, science };

export function newDraft(domain = 'networking') {
  if (!DOMAIN_OPTIONS.some(([id]) => id === domain)) throw new Error('Unknown domain');
  const source = templates[domain] || networking;
  const copy = JSON.parse(JSON.stringify(source));
  copy.domain = domain;
  if (!templates[domain]) {
    copy.mission_id = domain + '-research-proposal';
    copy.title = domain[0].toUpperCase() + domain.slice(1) + ' research comparison';
    copy.question = 'What measurable evidence could distinguish two competing ' + domain + ' explanations under controlled conditions?';
    copy.scope.in_scope = 'A bounded, reviewable evaluation of two proposed ' + domain + ' hypotheses using permitted evidence only.';
    copy.scope.out_of_scope = 'Unapproved field deployments, external actions, and claims unsupported by available evidence.';
    copy.evidence = { source_kind: 'UNKNOWN', source_description: 'Sources have not been collected, inspected or verified.',
      replay_plan: 'Document future data origin, versions, limits and a reproducible audit procedure.' };
    copy.candidates = [
      { id: 'H1', hypothesis: 'One proposed explanation produces a reproducible measurable improvement.',
        prediction: 'The predefined measurement changes under matched and controlled conditions.',
        falsifier: 'Independent repeated comparisons fail to show the proposed change.' },
      { id: 'H2', hypothesis: 'The measured effect is explained by random variation or a confounding factor.',
        prediction: 'The apparent difference vanishes once conditions and confounders are matched.',
        falsifier: 'Repeated independent comparisons retain the effect beyond noise.' }
    ];
    copy.evaluation = {
      method: 'Pre-register a matched comparison before gathering measurements.',
      metric: 'A domain-appropriate, predeclared quantitative or qualitative metric',
      baseline: 'An unchanged reference condition evaluated under identical assumptions.',
      negative_control: 'A sham or null condition expected not to produce a measurable change.',
      success_criterion: 'The proposed effect clears a stated threshold on held-out comparison data.',
      failure_criterion: 'The threshold is not met or a required control produces a false-positive.',
      uncertainty: 'Report sample size, uncertainty, assumptions, and any methodological disagreements.'
    };
    copy.risk = { level: 'LOW', potential_harms: 'Overstating weak evidence or taking action without required review.',
      stop_condition: 'Refuse any external work until a separate authorized execution protocol exists.' };
  }
  return copy;
}

const scalarType = value => Array.isArray(value) ? 'array' : value === null ? 'null' : typeof value;
function deepEqual(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}
function walk(value, spec, path, errors) {
  if (Object.prototype.hasOwnProperty.call(spec, 'const') && !deepEqual(value, spec.const)) {
    errors.push(path + ': fixed value mismatch'); return;
  }
  if (spec.enum && !spec.enum.includes(value)) {
    errors.push(path + ': value not permitted'); return;
  }
  if (spec.type === 'object') {
    if (scalarType(value) !== 'object') { errors.push(path + ': expected object'); return; }
    const keys = Object.keys(value);
    for (const name of Object.keys(spec.properties || {})) {
      if (!Object.prototype.hasOwnProperty.call(value, name)) errors.push(path + '/' + name + ': missing');
      else walk(value[name], spec.properties[name], path + '/' + name, errors);
    }
    if (spec.additionalProperties === false) {
      for (const name of keys) {
        if (!Object.prototype.hasOwnProperty.call(spec.properties, name))
          errors.push(path + '/' + name + ': unexpected');
      }
    }
  } else if (spec.type === 'array') {
    if (!Array.isArray(value)) { errors.push(path + ': expected list'); return; }
    if (value.length < (spec.minItems ?? 0) || value.length > (spec.maxItems ?? Infinity))
      errors.push(path + ': list outside bounds');
    value.forEach((item, i) => walk(item, spec.items, path + '/' + i, errors));
  } else if (spec.type === 'string') {
    if (typeof value !== 'string') { errors.push(path + ': expected text'); return; }
    if (value.length < (spec.minLength ?? 0) || value.length > (spec.maxLength ?? Infinity))
      errors.push(path + ': text length outside bounds');
    if (spec.pattern && !(new RegExp(spec.pattern)).test(value))
      errors.push(path + ': identifier format mismatch');
  } else if (spec.type === 'integer') {
    if (!Number.isSafeInteger(value)) { errors.push(path + ': expected integer'); return; }
    if (value < (spec.minimum ?? -Infinity) || value > (spec.maximum ?? Infinity))
      errors.push(path + ': number outside bounds');
  }
}
export function validateDraft(draft) {
  const errors = [];
  walk(draft, schema, 'mission', errors);
  if (draft && Array.isArray(draft.candidates)) {
    const ids = draft.candidates.map(c => c?.id);
    if (ids.some((id, i) => id !== 'H' + (i + 1)))
      errors.push('mission/candidates: expected unique sequential identifiers H1..H4');
    draft.candidates.forEach((c, i) => {
      if (typeof c?.prediction === 'string' && typeof c?.falsifier === 'string' &&
          c.prediction.trim().toLowerCase() === c.falsifier.trim().toLowerCase())
        errors.push('mission/candidates/' + i + ': prediction and falsifier must differ');
    });
  }
  if (typeof draft?.evaluation?.success_criterion === 'string' &&
      typeof draft?.evaluation?.failure_criterion === 'string' &&
      draft.evaluation.success_criterion.trim().toLowerCase() === draft.evaluation.failure_criterion.trim().toLowerCase())
    errors.push('mission/evaluation: success and failure criteria must differ');
  return { ok: errors.length === 0, errors };
}
export const formatDraft = draft => JSON.stringify(draft, null, 2) + '\n';
