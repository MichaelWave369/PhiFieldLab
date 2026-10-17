import argparse
import json
from pathlib import Path
from .core import train, verify

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
    a = parser.parse_args()
    if a.action == 'train':
        r = train(seed=a.seed, epochs=a.epochs, train_count=a.train_count,
                  val_count=a.val_count, test_count=a.test_count,
                  device=a.device, out=a.out)
        print(json.dumps({'run': str(a.out), 'heldout_test': r['heldout_test']}, indent=2))
    else:
        print(json.dumps(verify(a.out, device=a.device), indent=2))

if __name__ == '__main__':
    main()
