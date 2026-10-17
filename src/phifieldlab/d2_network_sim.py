"""D2 synthetic queue laboratory: deterministic model, NOT real switch telemetry.

No sockets, filesystem I/O, third-party packages, external model loading,
arbitrary expressions or dynamic plugins. Called by an allowlisted child worker.
"""
from __future__ import annotations

import hashlib
import json
import math
import random

PROTOCOL = "PHIFIELD_D2_SYNTHETIC_QUEUE_V1"
SEEDS = (101, 103, 107, 109, 113)
SLOTS = 1200
MAX_QUEUE = 64
POLICIES = ("fifo", "fair")
FLOW_NAMES = ("latency", "bulk")


def make_trace(seed: int):
    if type(seed) is not int or seed not in SEEDS:
        raise ValueError("unregistered seed")
    rng = random.Random(seed)
    trace = []
    sequence = 0
    for tick in range(SLOTS):
        flows = []
        if rng.random() < .42:
            flows.append("latency")
        if rng.random() < .7:
            flows.append("bulk")
        if rng.random() < .12:
            flows.extend(["bulk"] * 3)
        for flow in flows:
            trace.append((sequence, tick, flow))
            sequence += 1
    return tuple(trace)


def percentile95(samples):
    if not samples:
        return None
    numbers = sorted(samples)
    return numbers[math.ceil(.95 * len(numbers)) - 1]


def evaluate(trace, policy: str):
    if policy not in POLICIES:
        raise ValueError("unregistered scheduling policy")
    waiting = []
    drops = {"latency": 0, "bulk": 0}
    delays = {"latency": [], "bulk": []}
    submitted = {"latency": 0, "bulk": 0}
    index = 0
    served_last = "bulk"
    for tick in range(SLOTS + MAX_QUEUE + 1):
        while index < len(trace) and trace[index][1] == tick:
            packet = trace[index]
            index += 1
            flow = packet[2]
            submitted[flow] += 1
            if len(waiting) == MAX_QUEUE:
                drops[flow] += 1
            else:
                waiting.append(packet)
        if waiting:
            if policy == "fifo":
                chosen = 0
            else:
                target = "latency" if served_last == "bulk" else "bulk"
                chosen = next((i for i, packet in enumerate(waiting) if packet[2] == target), 0)
            _, timestamp, flow = waiting.pop(chosen)
            served_last = flow
            delays[flow].append(tick - timestamp + 1)
        if tick >= SLOTS and not waiting:
            break
    if index != len(trace) or waiting:
        raise ArithmeticError("queue drain incomplete")
    total_submitted = sum(submitted.values())
    total_drops = sum(drops.values())
    delivered = [delay for flow in FLOW_NAMES for delay in delays[flow]]
    return {
        "policy": policy,
        "offered_packets": total_submitted,
        "delivered_packets": len(delivered),
        "dropped_packets": total_drops,
        "loss_rate": round(total_drops / total_submitted, 9),
        "latency_p95_ms": percentile95(delays["latency"]),
        "bulk_p95_ms": percentile95(delays["bulk"]),
        "overall_p95_ms": percentile95(delivered),
    }


def run_batch():
    rows = []
    for seed in SEEDS:
        trace = make_trace(seed)
        trace_digest = hashlib.sha256(json.dumps(trace, separators=(",", ":")).encode()).hexdigest()
        baseline = evaluate(trace, "fifo")
        candidate = evaluate(trace, "fair")
        sham = evaluate(trace, "fifo")
        if sham != baseline or baseline["offered_packets"] != candidate["offered_packets"]:
            raise ArithmeticError("matched control failed")
        if baseline["latency_p95_ms"] is None or candidate["latency_p95_ms"] is None:
            raise ArithmeticError("no latency packets delivered")
        reduction = round(100 * (baseline["latency_p95_ms"] - candidate["latency_p95_ms"])
                          / baseline["latency_p95_ms"], 6)
        rows.append({
            "seed": seed, "trace_sha256": trace_digest,
            "baseline": baseline, "candidate": candidate,
            "sham_equals_baseline": True,
            "sensitive_p95_reduction_percent": reduction,
            "loss_not_worse": candidate["dropped_packets"] <= baseline["dropped_packets"]
        })
    success = all(row["sensitive_p95_reduction_percent"] >= 10 and row["loss_not_worse"]
                  for row in rows)
    return {
        "protocol": PROTOCOL,
        "origin": "SIMULATED", "authority": "NONE", "attested": False,
        "workload": {
            "unit": "synthetic one-millisecond slots",
            "ticks_per_seed": SLOTS, "queue_capacity_packets": MAX_QUEUE,
            "seeds": list(SEEDS), "policies": list(POLICIES),
            "primary_metric": "latency-class p95 delay, not overall p95 or real switch latency"
        },
        "rows": rows,
        "review": {
            "baseline_repeated_as_sham": True,
            "same_trace_per_policy": True,
            "per_seed_minimum_reduction_percent": 10,
            "no_increased_total_packet_drops": True,
            "verdict": "MEETS_DECLARED_TOY_THRESHOLD" if success else "DOES_NOT_MEET_DECLARED_TOY_THRESHOLD",
            "scientific_promotion": "BLOCKED",
            "limitations": [
                "Invented two-class queue model, not real networking equipment or a validated physical model.",
                "Sham control and replay use the same source code, not independent scientific attestation.",
                "No confidence interval, device variance, real traffic, switch firmware, or actual network telemetry."
            ]
        }
    }
