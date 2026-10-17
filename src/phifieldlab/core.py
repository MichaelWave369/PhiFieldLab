"""Frozen v0.1 synthetic directed-cycle transport benchmark.

This is a software/reproducibility exercise, NOT evidence that NBG describes nature.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch import nn
from safetensors.torch import save_file, load_file

MAX_EDGES = 12
THRESHOLD = 0.4
PROTOCOL = "PHIFIELD_E0_CYCLE_TRANSPORT_V1"


def freeze_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)


@dataclass(frozen=True)
class Dataset:
    edges: torch.Tensor  # (N, MAX_EDGES, 1) oriented edge measurements, zero padded
    mask: torch.Tensor   # (N, MAX_EDGES, 1), 1 valid and 0 pad
    residue: torch.Tensor  # (N,1) signed observed cycle transport
    label: torch.Tensor  # (N,1) 1 = deliberately injected residue, else 0
    sizes: torch.Tensor  # (N,) cycle lengths

    def sha256(self) -> str:
        h = hashlib.sha256()
        for t in (self.edges, self.mask, self.residue, self.label, self.sizes):
            a = t.contiguous().numpy()
            h.update(str(a.shape).encode())
            h.update(str(a.dtype).encode())
            h.update(a.tobytes())
        return h.hexdigest()


def make_dataset(count: int, seed: int, split: str) -> Dataset:
    if split not in ("train", "validation", "test"):
        raise ValueError("unknown split")
    if count <= 0 or count > 100_000:
        raise ValueError("sample count must be in 1..100000")
    gen = np.random.default_rng(seed)
    lengths = [3, 4, 5, 6] if split != "test" else [7, 8, 9, 10]
    edges = np.zeros((count, MAX_EDGES, 1), dtype="float32")
    mask = np.zeros((count, MAX_EDGES, 1), dtype="float32")
    residues = np.zeros((count, 1), dtype="float32")
    labels = np.zeros((count, 1), dtype="float32")
    sizes = np.zeros((count,), dtype="int64")
    for i in range(count):
        n = int(gen.choice(lengths))
        p = gen.uniform(-0.8, 0.8, size=n)
        # Oriented edge transport p_(i+1)-p_i on one directed cycle.
        vals = np.roll(p, -1) - p
        vals += gen.normal(0, 0.025, size=n)
        injected = int(i % 2 == 1)
        if injected:
            idx = int(gen.integers(0, n))
            vals[idx] += float(gen.choice([-1, 1])) * gen.uniform(0.9, 1.5)
        gen.shuffle(vals)  # edge input is permutation invariant, not index dependent
        edges[i, :n, 0] = vals.astype("float32")
        mask[i, :n, 0] = 1.0
        residues[i, 0] = np.float32(vals.sum())
        labels[i, 0] = injected
        sizes[i] = n
    return Dataset(*[torch.from_numpy(a) for a in (edges, mask, residues, labels, sizes)])


class EdgePoolNet(nn.Module):
    """Original 2-layer edge encoder, invariant sum pool, scalar learned head.

    A small neural network trained FROM RANDOM INITIALIZATION. It is a
    permutation-invariant edge-set learner, not a general graph neural network.
    """

    def __init__(self, width: int = 24):
        super().__init__()
        self.width = width
        self.edge_encoder = nn.Sequential(
            nn.Linear(1, width, bias=False), nn.Tanh(),
            nn.Linear(width, width, bias=False),
        )
        self.readout = nn.Linear(width, 1, bias=False)

    def forward(self, edge_values: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        return self.readout((self.edge_encoder(edge_values) * mask).sum(dim=1))


def weights_tensor_sha256(state: dict) -> str:
    """Stable semantic hash independent of safetensors header field ordering."""
    h = hashlib.sha256()
    for name in sorted(state):
        t = state[name].detach().cpu().contiguous().numpy()
        h.update(name.encode('utf-8'))
        h.update(str(t.dtype).encode('ascii'))
        h.update(json.dumps(t.shape).encode('ascii'))
        h.update(t.tobytes())
    return h.hexdigest()


def score(model: EdgePoolNet, data: Dataset, device: str) -> dict:
    model.eval()
    with torch.no_grad():
        yhat = model(data.edges.to(device), data.mask.to(device)).cpu()
    label = data.label.numpy().ravel().astype(bool)
    predicted = (yhat.abs().numpy().ravel() > THRESHOLD)
    baseline = (data.residue.abs().numpy().ravel() > THRESHOLD)
    baseline_wrong = (data.edges[:, 0, 0].abs().numpy() > THRESHOLD)
    def metrics(p):
        tp = int((p & label).sum()); tn = int((~p & ~label).sum())
        fp = int((p & ~label).sum()); fn = int((~p & label).sum())
        return {"accuracy": float((p == label).mean()), "tp": tp, "tn": tn, "fp": fp, "fn": fn}
    return {
        "n": len(data.sizes),
        "residue_mae": float((yhat - data.residue).abs().mean()),
        "learned": metrics(predicted),
        "exact_closure_rule": metrics(baseline),
        "single_edge_negative_control": metrics(baseline_wrong),
        "dataset_sha256": data.sha256(),
        "size_range": [int(data.sizes.min()), int(data.sizes.max())],
    }


def train(*, seed: int, epochs: int, train_count: int, val_count: int, test_count: int, device: str, out: Path) -> dict:
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("output directory must not already contain files")
    if not (1 <= epochs <= 1000):
        raise ValueError("epochs must be in 1..1000")
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA explicitly requested but unavailable; refusing fallback")
    freeze_seed(seed)
    dtrain = make_dataset(train_count, seed + 11, "train")
    dval = make_dataset(val_count, seed + 22, "validation")
    dtest = make_dataset(test_count, seed + 33, "test")
    model = EdgePoolNet().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.008)
    g = torch.Generator().manual_seed(seed + 44)
    best_val = float("inf")
    best_state = None
    for _ in range(epochs):
        model.train()
        for idx in torch.randperm(train_count, generator=g).split(128):
            edges = dtrain.edges[idx].to(device)
            mask = dtrain.mask[idx].to(device)
            targets = dtrain.residue[idx].to(device)
            prediction = model(edges, mask)
            loss = torch.mean((prediction - targets).square())
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            val_loss = float(torch.mean((model(dval.edges.to(device), dval.mask.to(device)) - dval.residue.to(device)).square()).cpu())
        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.detach().cpu().contiguous().clone() for k, v in model.state_dict().items()}
    assert best_state is not None
    model.load_state_dict(best_state)
    out.mkdir(parents=True, exist_ok=True)
    weights = out / "model.safetensors"
    save_file(best_state, str(weights), metadata={"protocol": PROTOCOL, "origin": "SIMULATED"})
    config = {
        "protocol": PROTOCOL, "architecture": "EdgePoolNet", "architecture_width": model.width,
        "seed": seed, "epochs": epochs, "n_train": train_count, "n_validation": val_count,
        "n_test": test_count, "training_device": device,
        "threshold": THRESHOLD,
        "train_cycle_lengths": [3,4,5,6], "test_cycle_lengths": [7,8,9,10],
        "noise_sigma": 0.025, "injected_residue_range": [0.9, 1.5],
    }
    (out / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    report = {
        "protocol": PROTOCOL,
        "origin": "SIMULATED", "authority": "NONE", "independent_attestation": False,
        "description": "Synthetic oriented cycle transport, not empirical physics; prediction of signed residual and defect classification",
        "best_validation_mse": best_val,
        "train": score(model, dtrain, device),
        "validation": score(model, dval, device),
        "heldout_test": score(model, dtest, device),
        "limitation": "No real-world data; exact arithmetic is a known optimal baseline under this task construction.",
    }
    (out / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    manifest = {
        "protocol": PROTOCOL, "origin": "SIMULATED", "authority": "NONE",
        "training_origin": "LOCAL_TRAINED_WEIGHTS", "attested": False,
        "weights_tensor_sha256": weights_tensor_sha256(best_state),
        "python_libraries": {"torch": torch.__version__, "numpy": np.__version__},
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (weights, out / 'config.json', out / 'report.json')},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return report


def verify(out: Path, *, device="cpu") -> dict:
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA explicitly requested but unavailable; refusing fallback")
    manifest = json.loads((out / 'manifest.json').read_text())
    if manifest['protocol'] != PROTOCOL or manifest['authority'] != 'NONE':
        raise ValueError('manifest protocol or authority mismatch')
    required_files = {"model.safetensors", "config.json", "report.json"}
    if set(manifest.get("sha256", {})) != required_files:
        raise ValueError("manifest must enumerate exactly the three frozen artifacts")
    for f, digest in manifest['sha256'].items():
        if hashlib.sha256((out / f).read_bytes()).hexdigest() != digest:
            raise ValueError('SHA-256 mismatch for ' + f)
    config = json.loads((out / 'config.json').read_text())
    if config['protocol'] != PROTOCOL or config['architecture'] != 'EdgePoolNet' or config['architecture_width'] != 24 or config['threshold'] != THRESHOLD:
        raise ValueError('config is incompatible')
    m = EdgePoolNet()
    loaded_state = load_file(str(out / 'model.safetensors'), device='cpu')
    if weights_tensor_sha256(loaded_state) != manifest.get('weights_tensor_sha256'):
        raise ValueError('learned weight tensor digest mismatch')
    m.load_state_dict(loaded_state, strict=True)
    m.to(device)
    report = json.loads((out / 'report.json').read_text())
    for split, count, offset in (("train", config['n_train'], 11), ("validation", config['n_validation'], 22), ("test", config['n_test'], 33)):
        d = make_dataset(count, config['seed'] + offset, split)
        now = score(m, d, device)
        recorded = report["heldout_test" if split == "test" else split]
        if now['dataset_sha256'] != recorded['dataset_sha256']:
            raise ValueError("dataset drift: " + split)
        if abs(now['residue_mae'] - recorded['residue_mae']) > 1e-4:
            raise ValueError("numerical replay divergence: " + split)
        for key in ('learned', 'exact_closure_rule', 'single_edge_negative_control'):
            if any(now[key][k] != recorded[key][k] for k in ('tp','tn','fp','fn')):
                raise ValueError("score drift: " + split + '/' + key)
    return {'protocol': PROTOCOL, 'sha256_verified': True, 'replay_verified': True, 'attested': False, 'authority': 'NONE'}
