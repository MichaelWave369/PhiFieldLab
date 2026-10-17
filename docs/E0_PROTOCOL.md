# E0: Frozen cycle-transport training benchmark

## Status
**SIMULATED / authority NONE.** This test is an ML pipeline and weight artifact proof-of-work, not a physics claim, not validation of NBG mathematics, not a general graph-network implementation, and not a replacement for independent scientific observation.

## Question
Can independently trained weights approximate a signed cycle-transport residual when evaluated on longer cycles than appear in training? Can that output classify an injected additive defect using a predeclared threshold?

## Deterministic construction
For a directed cycle of size n, choose hidden scalar potentials p_i in [-0.8, 0.8]. Let each oriented edge transport be t_i = p_(i+1) - p_i + Gaussian(0, 0.025), with wraparound. Every other example has one randomly located additional signed defect of magnitude 0.9 to 1.5. Shuffled edge entries preserve permutation invariance. Zero pad to 12 values with masks. The directly observable residual is R = sum_i t_i. Binary injected-defect label is 1 for the injected examples, 0 otherwise. A classification rule using abs(predicted signed R) > 0.4 is **locked before training**.

## Splits
- Train: length n in {3,4,5,6}; RNG seed+11; 50/50 injection labels.
- Validation: same lengths, independent seed+22; used for checkpoint selection.
- Held-out test: length n in {7,8,9,10}; independent seed+33; never used for checkpoint selection.
- The test withholds **cycle sizes**, not distinct fundamental graph topologies. It does not establish graph-family generalization.

## Model
`EdgePoolNet`: original small per-edge trainable MLP using tanh, masked sum-pooling, linear scalar readout. Network predicts signed R via mean squared error and is trained from random initialization (Adam). This is a permutation-invariant edge-set learner, NOT a general message-passing GNN.

## Baselines and negative controls
- Exact residual: `abs(sum observed transports) > 0.4`. This is a privileged deterministic arithmetic baseline and should be near perfect by construction. The neural model is **not expected to beat it**.
- Single-edge rule: `abs(first visible transport)>0.4`. Intentionally weak control.
- Evaluation records accuracy, TP, TN, FP, FN, signed-residue MAE, dataset hashes. No cherry-picked results, no empirical claim.

## Release gates
- Train with fixed seed, produce real safetensors weights; do not overwrite runs.
- Verify SHA-256 manifest and replay test scores on a fresh read.
- Test labels, withheld cycle lengths, permutation invariance, and tampering.
- Record training environment. Hashes prove file consistency, **not independent execution, ownership, or scientific truth**.
- Do not publish an improvement claim if the model merely approximates exact arithmetic.

## Known limitations
Synthetic only; edge orientation is supplied; learned pooling encodes additivity as an inductive bias; no missing-edge or hidden-variable reconstruction; held-out cycle length can differ from train sizes but topology remains one directed ring. CPU deterministic seed reproducibility can be affected by different library/hardware versions; CUDA determinism is not independently verified. Model training costs, speed, and GPU acceleration are unmeasured beyond explicit local runs.

## Digest semantics
The manifest includes both SHA-256 of the exact safetensors **file bytes** and a stable SHA-256 of sorted tensor names, shapes, dtypes, and numeric bytes. The latter permits tensor-level comparisons across runs even if safetensors header metadata ordering yields different container bytes. Reproducible numerical tensors are not proof of scientific generalization.
