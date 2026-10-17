"""QP4 finite many-body gap and independent-control tests."""
import json
import tempfile
import unittest
from pathlib import Path

from phifieldlab.qp3 import fingerprint as qp3
from phifieldlab.qp4 import (
    ANISOTROPY, BOUNDS, LENGTHS, PROTOCOL,
    spectrum, reference, write_reference, verify_reference
)
from phifieldlab.spin_chain import chain_spectrum


class QP4Tests(unittest.TestCase):
    def test_zero_anisotropy_reproduces_qp1_gaps_for_all_geometries(self):
        for n in LENGTHS:
            for boundary in BOUNDS:
                calculated=spectrum(n,0,boundary)
                qp1=chain_spectrum(n,boundary)
                self.assertAlmostEqual(calculated["lowest_m0_energy"],
                                       qp1["ground_energy"],delta=1e-7)
                self.assertAlmostEqual(calculated["first_excitation_gap"],
                                       qp1["lowest_excitation_gap"],delta=1e-7)

    def test_open_ground_energies_match_independent_qp3_at_all_d(self):
        for n in LENGTHS:
            for d in ANISOTROPY:
                self.assertAlmostEqual(spectrum(n,d,"open")["lowest_m0_energy"],
                                       qp3(n,d)["ground_energy_sector_m0"],delta=1e-7)

    def test_conservation_and_finite_positive_level_gaps(self):
        for row in reference()["rows"]:
            self.assertTrue(row["global_ground_is_m0"])
            self.assertGreater(row["first_excitation_gap"],0)
            self.assertGreater(row["neutral_m0_gap"],0)
            self.assertGreater(row["magnetization_changing_gap"],0)
            self.assertEqual(sorted(int(m) for m in row["magnetization_sector_minima"]),
                             list(range(row["n"]+1)))
            self.assertTrue(all(v>=row["lowest_m0_energy"]-1e-7
                                for v in row["magnetization_sector_minima"].values()))
            self.assertAlmostEqual(row["first_excitation_gap"],
                                   min(row["neutral_m0_gap"],
                                       row["magnetization_changing_gap"]),delta=1e-7)

    def test_metadata_and_complete_grid(self):
        payload=reference()
        self.assertEqual(payload["protocol"],PROTOCOL)
        self.assertEqual((payload["origin"],payload["authority"],payload["attested"]),
                         ("SIMULATED","NONE",False))
        self.assertEqual(len(payload["rows"]),len(LENGTHS)*len(BOUNDS)*len(ANISOTROPY))
        self.assertEqual({(r["n"],r["boundary"],r["d_over_j"]) for r in payload["rows"]},
                         {(n,b,d) for n in LENGTHS for b in BOUNDS for d in ANISOTROPY})
        self.assertTrue(any("NOT a phase" in s for s in payload["caveats"]))

    def test_report_create_only_replay_and_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"qp4.json"
            write_reference(path)
            self.assertTrue(verify_reference(path)["ok"])
            with self.assertRaises(FileExistsError):
                write_reference(path)
            raw=json.loads(path.read_text())
            raw["rows"][0]["first_excitation_gap"]+=.01
            path.write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError,"numeric mismatch"):
                verify_reference(path)

    def test_strict_validation_before_cached_values(self):
        for n,d,b in ((True,0,"open"),(4,1.0,"open"),(4,False,"open"),
                      (9,0,"open"),(4,-1,"open"),(4,0,"closed"),(4,0,True)):
            with self.assertRaises(ValueError):
                spectrum(n,d,b)


if __name__=="__main__":
    unittest.main()
