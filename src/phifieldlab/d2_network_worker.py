"""Internal fixed worker for D2. Direct invocation is NOT operator approval."""
import json
from .d2_network_sim import run_batch


def main():
    print(json.dumps(run_batch(), sort_keys=True, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
