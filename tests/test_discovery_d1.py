"""Discovery D1 contract tests. Draft validation must not execute any research."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from phifieldlab.discovery_d1 import (
    MissionValidationError, PROTOCOL, load_mission, load_schema, validate_mission
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "missions" / "d1-examples"


class DiscoveryD1Tests(unittest.TestCase):
    def fixtures(self):
        return sorted(EXAMPLES.glob("*.json"))

    def sample(self):
        return json.loads((EXAMPLES / "network-switch-latency.json").read_text(encoding="utf-8"))

    def test_examples_are_valid_and_never_authorize_execution(self):
        self.assertGreaterEqual(len(self.fixtures()), 3)
        self.assertEqual(load_schema()["properties"]["protocol"]["const"], PROTOCOL)
        domains = set()
        for path in self.fixtures():
            report = load_mission(path)
            self.assertTrue(report["ok"])
            self.assertEqual(report["protocol"], PROTOCOL)
            self.assertEqual(report["status"], "PROPOSAL_ONLY")
            self.assertFalse(report["execution_authorized"])
            self.assertFalse(report["attested"])
            self.assertEqual(report["review"], "REQUIRED_BEFORE_ANY_EXECUTION")
            self.assertEqual(len(report["sha256"]), 64)
            domains.add(report["domain"])
        self.assertEqual(domains, {"networking", "creative", "science"})

    def test_fail_closed_on_escalation_and_schema_tampering(self):
        spec = self.sample()
        variants = []
        for key, value in [
            ("network_access", True), ("local_execution", True),
            ("repository_writes", True), ("publication", True),
            ("external_spend", True), ("operator_approval_required", False)
        ]:
            x = copy.deepcopy(spec)
            x["permissions"][key] = value
            variants.append(x)
        x = copy.deepcopy(spec)
        x["resources"]["max_external_cost_usd"] = 0.01
        variants.append(x)
        x = copy.deepcopy(spec)
        x["provenance"]["attested"] = True
        variants.append(x)
        x = copy.deepcopy(spec)
        x["status"] = "APPROVED"
        variants.append(x)
        x = copy.deepcopy(spec)
        x["domain"] = "finance"
        variants.append(x)
        x = copy.deepcopy(spec)
        x["hidden_command"] = "shell injection"
        variants.append(x)
        x = copy.deepcopy(spec)
        x["evaluation"]["method"] = ""
        variants.append(x)
        x = copy.deepcopy(spec)
        x["resources"]["max_runtime_minutes"] = True
        variants.append(x)
        x = copy.deepcopy(spec)
        x["resources"]["max_compute_units"] = 999999
        variants.append(x)
        x = copy.deepcopy(spec)
        x["candidates"].append(copy.deepcopy(x["candidates"][1]))
        variants.append(x)
        x = copy.deepcopy(spec)
        x["candidates"][1]["id"] = "H1"
        variants.append(x)
        x = copy.deepcopy(spec)
        x["candidates"][0]["falsifier"] = x["candidates"][0]["prediction"]
        variants.append(x)
        x = copy.deepcopy(spec)
        x["evaluation"]["failure_criterion"] = x["evaluation"]["success_criterion"]
        variants.append(x)
        for bad in variants:
            with self.subTest(bad=bad):
                with self.assertRaises(MissionValidationError):
                    validate_mission(bad)

    def test_strict_json_reading_budgets_duplicates_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "draft.json"
            original = (EXAMPLES / "network-switch-latency.json").read_text()
            target.write_text('{"protocol":1,"protocol":2}', encoding="utf-8")
            with self.assertRaisesRegex(MissionValidationError, "duplicate"):
                load_mission(target)
            target.write_text(original.replace('"max_compute_units": 5', '"max_compute_units": NaN'))
            with self.assertRaisesRegex(MissionValidationError, "nonfinite"):
                load_mission(target)
            target.write_bytes(b" " * (128 * 1024 + 1))
            with self.assertRaisesRegex(MissionValidationError, "128 KiB"):
                load_mission(target)
            target.write_text(original)
            self.assertTrue(load_mission(target)["ok"])

    def test_d0_does_not_accept_d1_proposals_as_an_execution_mission(self):
        from phifieldlab.discovery import load_mission as load_d0
        with self.assertRaises(ValueError):
            load_d0(EXAMPLES / "network-switch-latency.json")


if __name__ == "__main__":
    unittest.main()
