"""Discovery D0 acceptance, permissions, tampering and QP5 replay tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from phifieldlab.discovery import (
    ADAPTER, PROTOCOL, load_mission, plan, run_mission, verify_report
)

MISSION = Path(__file__).resolve().parents[1] / "missions" / "qp5-d0-matched-controls.json"


class DiscoveryD0Tests(unittest.TestCase):
    def test_plan_is_read_only_and_explicitly_unapproved(self):
        mission, digest = load_mission(MISSION)
        result = plan(MISSION)
        self.assertEqual(result["status"], "AWAITING_EXPLICIT_LOCAL_APPROVAL")
        self.assertEqual(result["mission_sha256"], digest)
        self.assertEqual(result["adapter"], ADAPTER)
        self.assertEqual(result["protocol"], PROTOCOL)
        self.assertEqual((mission["origin"], mission["authority"], mission["attested"]),
                         ("SIMULATED", "NONE", False))
        self.assertFalse(any(result["actions"].values()))

    def test_reject_missing_approval_without_creating_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.json"
            with self.assertRaises(PermissionError):
                run_mission(MISSION, out)
            self.assertFalse(out.exists())

    def test_reject_permission_escalation_and_unregistered_hypotheses(self):
        spec = json.loads(MISSION.read_text())
        cases = []
        x = copy.deepcopy(spec)
        x["approval"]["network"] = True
        cases.append(x)
        x = copy.deepcopy(spec)
        x["approval"]["code_changes"] = True
        cases.append(x)
        x = copy.deepcopy(spec)
        x["limits"]["maximum_rows"] = 1_000_000
        cases.append(x)
        x = copy.deepcopy(spec)
        x["candidates"][0]["test"] = "ALWAYS_TRUE"
        cases.append(x)
        x = copy.deepcopy(spec)
        x["candidates"].append(copy.deepcopy(x["candidates"][1]))
        cases.append(x)
        x = copy.deepcopy(spec)
        x["origin"] = "OBSERVED"
        cases.append(x)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mission.json"
            for tampered in cases:
                path.write_text(json.dumps(tampered))
                with self.assertRaises(ValueError):
                    load_mission(path)

    def test_qp5_mission_run_verify_negative_control_and_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.json"
            run_info = run_mission(MISSION, out, approve_local=True)
            report = json.loads(out.read_text())
            self.assertEqual(run_info["status"], "SIMULATED_REPLAYABLE_NOT_ATTESTED")
            self.assertEqual(report["evidence"]["rows_audited"], 48)
            self.assertEqual(report["evidence"]["matched_comparisons"], 12)
            self.assertEqual(report["evidence"]["qp4_independent_solver_energy_checks"], 48)
            self.assertLessEqual(report["evidence"]["maximum_energy_difference"], 1e-7)
            by_id = {c["candidate_id"]: c for c in report["candidates"]}
            self.assertEqual(by_id["C1_HIGH_D_REDUCES_ENTROPY"]["verdict"],
                             "SUPPORTED_IN_SIMULATION")
            self.assertEqual(by_id["C2_D_INVARIANT_NULL"]["verdict"],
                             "FALSIFIED_IN_SIMULATION")
            self.assertTrue(report["adversarial_review"]["null_candidate_falsified"])
            self.assertEqual(report["governance"]["scientific_promotion"], "BLOCKED")
            self.assertFalse(report["attested"])
            self.assertTrue(verify_report(MISSION, out)["ok"])
            with self.assertRaises(FileExistsError):
                run_mission(MISSION, out, approve_local=True)
            report["candidates"][0]["verdict"] = "SCIENTIFICALLY_PROVEN"
            out.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, "mismatch"):
                verify_report(MISSION, out)

    def test_mission_hash_binds_report_to_exact_specification(self):
        with tempfile.TemporaryDirectory() as tmp:
            changed = json.loads(MISSION.read_text())
            changed["question"] += " This edits the mission without changing its test."
            path = Path(tmp) / "modified.json"
            path.write_text(json.dumps(changed))
            self.assertNotEqual(plan(path)["mission_sha256"],
                                plan(MISSION)["mission_sha256"])


if __name__ == "__main__":
    unittest.main()
