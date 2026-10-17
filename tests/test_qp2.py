"""QP2 finite spin-chain observables and negative-interpretation controls."""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from phifieldlab.qp2 import (
    PROTOCOL, ODD, EVEN, edge_profile, string_correlator,
    reference, write_reference, verify_reference, lowest_state
)
from phifieldlab.spin_chain import chain_spectrum


class QP2Tests(unittest.TestCase):
    def test_odd_open_edge_profile_and_spin_conservation(self):
        for n in ODD:
            p=edge_profile(n)
            m=np.array(p["site_magnetization"])
            self.assertAlmostEqual(float(m.sum()),1.,places=7)
            self.assertTrue(np.allclose(m,m[::-1],atol=1e-7,rtol=0))
            self.assertGreater(p["edge_absolute_fraction"],p["uniform_fraction_reference"])
            self.assertLess(p["eigenpair_residual"],1e-7)
            self.assertAlmostEqual(p["lowest_sector_energy"],
                                   chain_spectrum(n)["ground_energy"],places=7)
        self.assertTrue(np.allclose(edge_profile(3)["site_magnetization"],
                                    [.75,-.5,.75],atol=1e-7))

    def test_even_nonlocal_string_distinct_from_local_two_point(self):
        for n in EVEN:
            for boundary in ("open","periodic"):
                p=string_correlator(n,boundary)
                self.assertEqual(p["probe_sites_zero_based"],[0,n-2])
                self.assertGreater(p["string_zz"],0)
                self.assertLess(p["two_point_zz"],0)
                self.assertGreater(abs(p["string_zz"]-p["two_point_zz"]),.1)
                self.assertAlmostEqual(p["endpoint_string_minus_endpoint_two_point"],0,places=9)
                self.assertEqual(p["all_zero_product_state_string"],0.)
                self.assertLess(p["eigenpair_residual"],1e-7)
                self.assertAlmostEqual(p["lowest_sector_energy"],
                                       chain_spectrum(n,boundary)["ground_energy"],places=7)

    def test_periodic_is_not_a_null_control(self):
        for n in EVEN:
            open_data=string_correlator(n,"open")
            ring_data=string_correlator(n,"periodic")
            self.assertGreater(ring_data["string_zz"],0)
            self.assertNotAlmostEqual(open_data["string_zz"],ring_data["string_zz"],places=3)

    def test_reference_metadata(self):
        r=reference()
        self.assertEqual(r["protocol"],PROTOCOL)
        self.assertEqual((r["origin"],r["authority"],r["attested"]),
                         ("SIMULATED","NONE",False))
        self.assertEqual([p["n"] for p in r["open_odd_edge_profiles"]],list(ODD))
        self.assertEqual([p["n"] for p in r["even_string_open"]],list(EVEN))
        self.assertIn("NOT_LAB",r["data_kind"])

    def test_create_only_replay_and_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"qp2.json"
            summary=write_reference(p)
            self.assertEqual(summary["protocol"],PROTOCOL)
            self.assertTrue(verify_reference(p)["ok"])
            with self.assertRaises(FileExistsError):
                write_reference(p)
            data=json.loads(p.read_text())
            data["even_string_open"][0]["string_zz"]+=.1
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"numeric mismatch"):
                verify_reference(p)

    def test_rejected_size_and_boundaries(self):
        for n in (2,4,6,8,9):
            with self.assertRaises(ValueError):
                edge_profile(n)
        for n in (3,5,7,9):
            with self.assertRaises(ValueError):
                string_correlator(n,"open")
        with self.assertRaises(ValueError):
            string_correlator(4,"torus")
        with self.assertRaises(ValueError):
            lowest_state(9,0,"open")


if __name__=="__main__":
    unittest.main()
