"""D3 cleanroom refusal suite. CI never needs Docker to test the gate."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phifieldlab import discovery_d3 as d3
from phifieldlab.d2_network_sim import run_batch

ROOT = Path(__file__).resolve().parents[1]
MISSION = ROOT / "missions" / "d1-examples" / "network-switch-latency.json"
IMAGE = "sha256:" + "a" * 64
NAME = "phifield-d3-0123456789abcdef"


class D3Tests(unittest.TestCase):
    def test_preexecution_plan_has_no_runtime_grant(self):
        p = d3.plan(MISSION)
        self.assertEqual(p["status"], "AWAITING_LOCAL_OPERATOR_APPROVAL_AND_CONTAINER_PREFLIGHT")
        self.assertFalse(p["execution_authorized"])
        self.assertFalse(p["runtime_checked"])
        self.assertEqual(p["origin"], "SIMULATED")
        self.assertFalse(p["attested"])

    def test_frozen_policy_and_docker_flags(self):
        policy, digest = d3.policy()
        self.assertEqual(policy["protocol"], d3.CONTRACT)
        self.assertEqual(len(digest), 64)
        cmd = d3.command(IMAGE, name=NAME)
        for item in ["--network", "none", "--read-only", "--cap-drop", "ALL",
                     "--pids-limit", "32", "--memory", "128m", "--memory-swap",
                     "--cpus", "--ipc", "--security-opt", "no-new-privileges:true",
                     "--user", "65534:65534", "--pull", "never", "--tmpfs"]:
            self.assertIn(item, cmd)
        self.assertEqual(cmd[-1], IMAGE)
        for forbidden in ["-v", "--volume", "--mount", "--privileged",
                          "--publish", "--device", "--entrypoint", "--env-file"]:
            self.assertNotIn(forbidden, cmd)

    def test_bad_image_ids_and_names_are_refused(self):
        for bad in ["python:latest", "sha256:" + "z"*64,
                    "--privileged", "sha256:" + "b"*63, "x"*80, None]:
            with self.assertRaises(d3.CleanroomRefusal):
                d3.command(bad, name=NAME)
        with self.assertRaises(d3.CleanroomRefusal):
            d3.command(IMAGE, name="../bad")

    def test_missing_docker_and_external_endpoint_fail_closed(self):
        with patch("phifieldlab.discovery_d3.shutil.which", return_value=None):
            with patch.dict("os.environ", {}, clear=True):
                with self.assertRaises(d3.CleanroomRefusal):
                    d3.preflight(IMAGE)
        with patch.dict("os.environ", {"DOCKER_HOST": "tcp://example.com:2376"}):
            with self.assertRaises(d3.CleanroomRefusal):
                d3.preflight(IMAGE)

    def test_preflight_rejects_remote_context_missing_seccomp_and_bad_image(self):
        local = {"Endpoints": {"docker": {"Host": "npipe:////./pipe/docker_engine"}}}
        engine = {"OSType": "linux", "MemoryLimit": True, "PidsLimit": True,
                  "CpuCfsQuota": True, "SecurityOptions": ["name=seccomp,profile=builtin"]}
        image = {"Id": IMAGE, "Config": {
            "Labels": {"org.phifieldlab.contract": d3.CONTRACT,
                       "org.phifieldlab.adapter": "SYNTHETIC_QUEUE_V1"},
            "Entrypoint": d3.ENTRYPOINT, "User": "65534:65534", "WorkingDir": "/tmp"}}
        with patch.dict("os.environ", {}, clear=True), patch("phifieldlab.discovery_d3.shutil.which", return_value="/usr/bin/docker"):
            with patch("phifieldlab.discovery_d3._json_command", side_effect=[local, engine, image]):
                self.assertTrue(d3.preflight(IMAGE)["local_docker_endpoint"])
            remote = copy.deepcopy(local)
            remote["Endpoints"]["docker"]["Host"] = "ssh://other-host"
            with patch("phifieldlab.discovery_d3._json_command", return_value=remote):
                with self.assertRaises(d3.CleanroomRefusal):
                    d3.preflight(IMAGE)
            weak = copy.deepcopy(engine)
            weak["SecurityOptions"] = []
            with patch("phifieldlab.discovery_d3._json_command", side_effect=[local, weak]):
                with self.assertRaises(d3.CleanroomRefusal):
                    d3.preflight(IMAGE)
            forged = copy.deepcopy(image)
            forged["Config"]["User"] = "root"
            with patch("phifieldlab.discovery_d3._json_command", side_effect=[local, engine, forged]):
                with self.assertRaises(d3.CleanroomRefusal):
                    d3.preflight(IMAGE)

    def test_approval_and_path_refusal_before_worker(self):
        digest = d3.plan(MISSION)["mission_sha256"]
        d3.repo_root().joinpath("artifacts", "local").mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=d3.repo_root() / "artifacts" / "local") as tmp:
            out = Path(tmp) / "receipt.json"
            with patch("phifieldlab.discovery_d3._run_container") as worker:
                for approved, expected in [(False, digest), (True, "b"*64)]:
                    with self.assertRaises(PermissionError):
                        d3.run(MISSION, out, approve_local=approved,
                               expect_sha256=expected, image_id=IMAGE)
                worker.assert_not_called()
            with self.assertRaises(ValueError):
                d3.run(MISSION, ROOT / "README.json", approve_local=True,
                       expect_sha256=digest, image_id=IMAGE)

    def test_mocked_container_run_replay_and_tamper_rejection(self):
        digest = d3.plan(MISSION)["mission_sha256"]
        sample = run_batch()
        runtime = {
            "backend": "DOCKER_LINUX_CONTAINER", "image_id": IMAGE,
            "local_docker_endpoint": True, "linux_engine": True,
            "seccomp_enabled": True, "quotas_supported": True,
            "warning": "Image provenance and host hardening require independent operator review. No VM-level boundary."
        }
        d3.repo_root().joinpath("artifacts", "local").mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=d3.repo_root() / "artifacts" / "local") as tmp:
            file = Path(tmp) / "receipt.json"
            with patch("phifieldlab.discovery_d3._run_container", return_value=(sample, runtime)):
                receipt = d3.run(MISSION, file, approve_local=True,
                                 expect_sha256=digest, image_id=IMAGE)
                self.assertTrue(receipt["ok"])
                self.assertTrue(d3.verify(MISSION, file, approve_local=True,
                                          expect_sha256=digest, image_id=IMAGE)["ok"])
                with self.assertRaises(FileExistsError):
                    d3.run(MISSION, file, approve_local=True,
                           expect_sha256=digest, image_id=IMAGE)
                data = json.loads(file.read_text())
                data["scientific_promotion"] = "VERIFIED"
                file.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaises(d3.CleanroomRefusal):
                    d3.verify(MISSION, file, approve_local=True,
                              expect_sha256=digest, image_id=IMAGE)

    def test_policy_gate_rejects_modified_mission_without_docker(self):
        with self.assertRaises(ValueError):
            d3.plan(ROOT / "missions" / "d1-examples" / "music-arrangement-listener-study.json")


if __name__ == "__main__":
    unittest.main()
