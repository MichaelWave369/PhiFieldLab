import argparse
import json
from pathlib import Path
from .core import train, verify
from .parity import PROTOCOL as PARITY_PROTOCOL, ladder as parity_ladder

def main():
    parser = argparse.ArgumentParser(prog='python -m phifieldlab')
    sub = parser.add_subparsers(dest='action', required=True)
    t = sub.add_parser('train', help='train from random initialization; never overwrite results')
    t.add_argument('--out', type=Path, required=True)
    t.add_argument('--seed', type=int, default=369)
    t.add_argument('--epochs', type=int, default=35)
    t.add_argument('--train-count', type=int, default=4096)
    t.add_argument('--val-count', type=int, default=512)
    t.add_argument('--test-count', type=int, default=512)
    t.add_argument('--device', choices=['auto','cpu','cuda'], default='auto')
    v = sub.add_parser('verify', help='verify manifest hashes and replay scores')
    v.add_argument('--out', type=Path, required=True)
    v.add_argument('--device', choices=['auto','cpu','cuda'], default='cpu')
    p = sub.add_parser('parity', help='simulate QP0 two-edge-spin parity toy and negative control')
    p.add_argument('--start', type=int, default=3)
    p.add_argument('--stop', type=int, default=16)
    p.add_argument('--amplitude', type=float, default=1.)
    p.add_argument('--decay-length', type=float, default=4.)
    s = sub.add_parser('spinchain', help='compute QP1 finite spin-1 chain spectra (SciPy optional extra)')
    s.add_argument('--start', type=int, default=3)
    s.add_argument('--stop', type=int, default=8)
    s.add_argument('--write', type=Path, help='exclusively create a reproducible JSON snapshot; no overwrite')
    a = parser.parse_args()
    if a.action == 'train':
        r = train(seed=a.seed, epochs=a.epochs, train_count=a.train_count,
                  val_count=a.val_count, test_count=a.test_count,
                  device=a.device, out=a.out)
        print(json.dumps({'run': str(a.out), 'heldout_test': r['heldout_test']}, indent=2))
    elif a.action == 'verify':
        print(json.dumps(verify(a.out, device=a.device), indent=2))
    elif a.action == 'parity':
        payload = {
            'protocol': PARITY_PROTOCOL,
            'origin': 'SIMULATED', 'authority': 'NONE', 'attested': False,
            'disclaimer': 'Toy edge exchange only, without measured spectra or superconducting bath',
            'inputs': {'start': a.start, 'stop': a.stop, 'amplitude': a.amplitude, 'decay_length': a.decay_length},
            'results': parity_ladder(a.start, a.stop, a.amplitude, a.decay_length),
            'negative_control': parity_ladder(a.start, a.stop, a.amplitude, a.decay_length, True),
        }
        print(json.dumps(payload, indent=2))
    elif a.action == 'spinchain':
        # Lazy import preserves E0 and QP0 installations without SciPy.
        from .spin_chain import reference_ladder, write_reference
        if a.write:
            write_reference(a.write, a.start, a.stop)
            print(json.dumps({'file': str(a.write), 'origin': 'SIMULATED', 'authority': 'NONE', 'attested': False}))
        else:
            print(json.dumps(reference_ladder(a.start, a.stop), indent=2))

if __name__ == '__main__':
    main()
