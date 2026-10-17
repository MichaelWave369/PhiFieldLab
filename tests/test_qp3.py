"""QP3 numerical consistency, QP2 replay, and control/claim-firewall tests."""
import json
import tempfile
import unittest
from pathlib import Path

from phifieldlab.qp3 import (
    ANISOTROPY, LENGTHS, PROTOCOL, fingerprint, reference,
    verify_reference, write_reference,
)
from phifieldlab.qp2 import string_correlator


class QP3Tests(unittest.TestCase):
    def test_matched_hamiltonian_zero_anisotropy_replays_qp2(self):
        for n in LENGTHS:
            old = string_correlator(n, "open")
            new = fingerprint(n, 0)
            self.assertAlmostEqual(new["string_zz"], old["string_zz"], delta=1e-7)
            self.assertAlmostEqual(new["two_point_zz"], old["two_point_zz"], delta=1e-7)
            self.assertAlmostEqual(new["ground_energy_sector_m0"],
                                   old["lowest_sector_energy"], delta=1e-7)

    def test_matched_large_d_shifts_to_product_state(self):
        for n in LENGTHS:
            normal = fingerprint(n, 0)
            large = fingerprint(n, 12)
            self.assertGreater(large["all_zero_product_overlap"],
                               normal["all_zero_product_overlap"])
            self.assertLess(large["mean_local_sz_squared"],
                            normal["mean_local_sz_squared"])
            self.assertGreater(large["all_zero_product_overlap"], .85)
            self.assertLess(large["eigenpair_residual"],1e-7)
            self.assertLess(normal["eigenpair_residual"],1e-7)

    def test_twelve_matched_rows_and_claim_caveats(self):
        r = reference()
        self.assertEqual(r["protocol"],PROTOCOL)
        self.assertEqual((r["origin"],r["authority"],r["attested"]),
                         ("SIMULATED","NONE",False))
        self.assertEqual(len(r["rows"]),len(ANISOTROPY)*len(LENGTHS))
        self.assertEqual({(q["n"],q["anisotropy_d"]) for q in r["rows"]},
                         {(n,d) for n in LENGTHS for d in ANISOTROPY})
        for q in r["rows"]:
            self.assertEqual(q["probe_sites_zero_based"],[0,q["n"]-2])
            self.assertEqual(q["magnetization_sector"],0)
            self.assertEqual(q["boundary"],"open")
            self.assertTrue(0<=q["all_zero_product_overlap"]<=1)
            self.assertTrue(0<=q["mean_local_sz_squared"]<=1)
        self.assertTrue(any("thermodynamic" in q for q in r["caveats"]))

    def test_strict_replay_tamper_and_create_only(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)/"result.json"
            write_reference(dest)
            self.assertTrue(verify_reference(dest)["ok"])
            with self.assertRaises(FileExistsError):
                write_reference(dest)
            raw=json.loads(dest.read_text())
            raw["rows"][0]["mean_local_sz_squared"]+=.001
            dest.write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError,"numeric mismatch"):
                verify_reference(dest)

    def test_reject_nonfrozen_or_boolean_inputs(self):
        for n,d in ((2,0),(9,0),(4,-1),(4,99),(True,0),(4,False),(4,1.0)):
            with self.assertRaises(ValueError):
                fingerprint(n,d)


if __name__ == "__main__":
    unittest.main()
