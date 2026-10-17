"""QP5 physical trace, Schmidt, matched-D and tamper controls."""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from phifieldlab.qp5 import (
    ANISOTROPY, BOUNDS, LENGTHS, PROTOCOL,
    audit, reference, write_reference, verify_reference
)
from phifieldlab.qp4 import spectrum


class QP5Tests(unittest.TestCase):
    def test_all_rows_are_normalized_finite_reduced_states(self):
        rows=reference()["rows"]
        self.assertEqual(len(rows),48)
        for row in rows:
            self.assertEqual(row["probability_trace"],1.)
            self.assertEqual(row["magnetization_sector"],0)
            self.assertLess(row["eigenpair_residual"],1e-7)
            self.assertLessEqual(0,row["entropy_von_neumann_nats"])
            self.assertLessEqual(0,row["schmidt_pair_split"])
            self.assertLessEqual(row["largest_schmidt_probability"],1.)
            self.assertTrue(0<row["purity"]<=1.)
            self.assertEqual(len(row["schmidt_probabilities_top6"]),6)
            self.assertTrue(all(0<=x<=1 for x in row["schmidt_probabilities_top6"]))
            self.assertEqual(row["cut_after_site"] in (1,row["n"]//2),True)
            self.assertTrue(all(a>=b-1e-10 for a,b in zip(
                row["schmidt_probabilities_top6"],
                row["schmidt_probabilities_top6"][1:])))

    def test_single_site_probabilities_sum_to_one(self):
        for n in LENGTHS:
            for boundary in BOUNDS:
                for d in ANISOTROPY:
                    row=audit(n,d,boundary,1)
                    self.assertAlmostEqual(
                        sum(row["schmidt_probabilities_top6"]),1.,delta=2e-8)
                    self.assertLessEqual(row["entropy_von_neumann_nats"],
                                         np.log(3)+1e-7)

    def test_high_d_has_smaller_entropy_and_dominant_schmidt_weight(self):
        for n in LENGTHS:
            for boundary in BOUNDS:
                for cut in (1,n//2):
                    start=audit(n,0,boundary,cut)
                    high=audit(n,12,boundary,cut)
                    self.assertLess(
                        high["entropy_von_neumann_nats"],
                        start["entropy_von_neumann_nats"])
                    self.assertGreater(
                        high["largest_schmidt_probability"],
                        start["largest_schmidt_probability"])
                    self.assertGreater(high["largest_schmidt_probability"],.85)

    def test_qp4_energies_and_distinct_cut_geometry(self):
        for n in LENGTHS:
            for boundary in BOUNDS:
                for d in ANISOTROPY:
                    expected=spectrum(n,d,boundary)["lowest_m0_energy"]
                    for cut in (1,n//2):
                        row=audit(n,d,boundary,cut)
                        self.assertAlmostEqual(row["ground_energy_m0"],
                                               expected,delta=1e-7)
                    self.assertEqual(audit(n,d,boundary,1)["left_dimension"],3)
                    self.assertEqual(audit(n,d,boundary,n//2)["left_dimension"],
                                     3**(n//2))

    def test_frozen_provenance_and_claim_boundaries(self):
        data=reference()
        self.assertEqual(data["protocol"],PROTOCOL)
        self.assertEqual((data["origin"],data["authority"],data["attested"]),
                         ("SIMULATED","NONE",False))
        self.assertEqual(data["entropy_units"],"nats (natural logarithm)")
        self.assertTrue(any("TWO bonds" in text for text in data["caveats"]))
        self.assertTrue(any("do NOT establish" in text for text in data["caveats"]))

    def test_write_is_create_only_and_tampering_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"qp5.json"
            write_reference(path)
            self.assertTrue(verify_reference(path)["ok"])
            with self.assertRaises(FileExistsError):
                write_reference(path)
            contents=json.loads(path.read_text())
            contents["rows"][0]["entropy_von_neumann_nats"]+=.01
            path.write_text(json.dumps(contents))
            with self.assertRaisesRegex(ValueError,"numeric mismatch"):
                verify_reference(path)

    def test_validate_types_before_cache(self):
        for n,d,b,c in [
            (True,0,"open",1),(4,0.0,"open",1),(4,False,"open",1),
            (6,0,"torus",1),(6,0,"open",True),(6,0,"open",3.0),
            (8,0,"open",7),(9,0,"open",1)
        ]:
            with self.assertRaises(ValueError):
                audit(n,d,b,c)


if __name__=="__main__":
    unittest.main()
