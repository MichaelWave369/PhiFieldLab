"""D2 admission, fixed-worker results, approval, timeout and receipt replay."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phifieldlab.discovery_d2 import (
    ADAPTER, D2Refusal, PROTOCOL, _check_result, _policy, local_artifacts_dir,
    plan, run, verify
)
from phifieldlab.d2_network_sim import SEEDS, evaluate, make_trace, run_batch

ROOT = Path(__file__).resolve().parents[1]
MISSION = ROOT / "missions" / "d1-examples" / "network-switch-latency.json"


class DiscoveryD2Tests(unittest.TestCase):
    def test_only_known_d1_mission_is_admitted(self):
        outcome = plan(MISSION)
        self.assertEqual(outcome["protocol"], PROTOCOL)
        self.assertEqual(outcome["adapter"], ADAPTER)
        self.assertEqual(outcome["status"], "AWAITING_EXPLICIT_LOCAL_APPROVAL")
        self.assertFalse(outcome["execution_authorized"])
        self.assertEqual(outcome["expected_trials"], 5)
        self.assertEqual(len(outcome["mission_sha256"]), 64)
        self.assertFalse(outcome["network_or_production_access"])
        self.assertEqual(_policy()[0]["max_wall_seconds"], 30)

        for name in ("music-arrangement-listener-study", "spin-chain-scaling-question"):
            with self.assertRaises(D2Refusal):
                plan(ROOT / "missions" / "d1-examples" / (name + ".json"))

    def test_modified_or_escalated_mission_is_refused(self):
        original = json.loads(MISSION.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "mission.json"
            variants = []
            x = copy.deepcopy(original)
            x["permissions"]["network_access"] = True
            variants.append(x)
            x = copy.deepcopy(original)
            x["question"] = x["question"] + " Extra text changes the approved evidence question."
            variants.append(x)
            x = copy.deepcopy(original)
            x["mission_id"] = "arbitrary-mission"
            variants.append(x)
            for candidate in variants:
                target.write_text(json.dumps(candidate))
                with self.assertRaises(ValueError):
                    plan(target)

    def test_refuse_without_approval_or_matching_digest(self):
        digest = plan(MISSION)["mission_sha256"]
        with tempfile.TemporaryDirectory(dir=local_artifacts_dir().parent) as temp:
            # Outside the artifacts/local/ allowlist must be refused, even if approved.
            outside = Path(temp) / "network.json"
            with self.assertRaises(D2Refusal):
                run(MISSION, outside, approve_local=True, expect_sha256=digest)
        with tempfile.TemporaryDirectory(dir=local_artifacts_dir()) as temp:
            out = Path(temp) / "network.json"
            for allow, expected in ((False, digest), (True, "0" * 64)):
                with self.assertRaises(PermissionError):
                    run(MISSION, out, approve_local=allow, expect_sha256=expected)
            self.assertFalse(out.exists())

    def test_frozen_trace_and_paired_sham_control(self):
        self.assertEqual(len(SEEDS), 5)
        trace = make_trace(SEEDS[0])
        self.assertEqual(trace, make_trace(SEEDS[0]))
        result = evaluate(trace, "fifo")
        self.assertEqual(result, evaluate(trace, "fifo"))
        self.assertEqual(result["offered_packets"],
                         result["delivered_packets"] + result["dropped_packets"])
        with self.assertRaises(ValueError):
            evaluate(trace, "real_switch")
        with self.assertRaises(ValueError):
            make_trace(999)

    def test_run_and_replay_and_tamper_refusal(self):
        digest = plan(MISSION)["mission_sha256"]
        local_artifacts_dir().mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=local_artifacts_dir()) as temp:
            target = Path(temp) / "network.json"
            saved = run(MISSION, target, approve_local=True, expect_sha256=digest)
            self.assertTrue(saved["ok"])
            receipt = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(receipt["protocol"], PROTOCOL)
            self.assertEqual(receipt["origin"], "SIMULATED")
            self.assertFalse(receipt["attested"])
            self.assertFalse(receipt["runtime_gate"]["os_network_and_filesystem_sandbox"])
            rows = receipt["result"]["rows"]
            self.assertEqual([r["seed"] for r in rows], list(SEEDS))
            self.assertTrue(all(r["sham_equals_baseline"] for r in rows))
            self.assertTrue(all(r["baseline"]["offered_packets"] ==
                                r["candidate"]["offered_packets"] for r in rows))
            self.assertTrue(verify(MISSION, target, approve_local=True,
                                   expect_sha256=digest)["ok"])
            with self.assertRaises(FileExistsError):
                run(MISSION, target, approve_local=True, expect_sha256=digest)
            with self.assertRaises(PermissionError):
                verify(MISSION, target, expect_sha256=digest)
            receipt["result"]["rows"][0]["sensitive_p95_reduction_percent"] = 999.0
            target.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaises(D2Refusal):
                verify(MISSION, target, approve_local=True, expect_sha256=digest)

    def test_worker_rejects_fabricated_promotions_and_bad_data(self):
        result = run_batch()
        policy, _ = _policy()
        _check_result(result, policy)
        variants = []
        x = copy.deepcopy(result)
        x["attested"] = True
        variants.append(x)
        x = copy.deepcopy(result)
        x["review"]["scientific_promotion"] = "VERIFIED"
        variants.append(x)
        x = copy.deepcopy(result)
        x["rows"][0]["baseline"]["delivered_packets"] -= 1
        variants.append(x)
        x = copy.deepcopy(result)
        x["rows"][0]["sham_equals_baseline"] = False
        variants.append(x)
        for bad in variants:
            with self.assertRaises(D2Refusal):
                _check_result(bad, policy)


if __name__ == "__main__":
    unittest.main()
