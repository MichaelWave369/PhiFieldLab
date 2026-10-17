import math
import unittest
import numpy as np

from phifieldlab.parity import DOT, PROTOCOL, TOTAL_S2, edge_spectrum, ladder


class QuantumParityToyTests(unittest.TestCase):
    def test_spin_operator_spectrum(self):
        self.assertTrue(np.allclose(np.linalg.eigvalsh(DOT), [-.75, .25, .25, .25]))
        self.assertTrue(np.allclose(np.linalg.eigvalsh(TOTAL_S2), [0, 2, 2, 2]))

    def test_odd_even_ground_states(self):
        for n in range(3, 17):
            r = edge_spectrum(n)
            self.assertEqual(r["ground_total_spin"], 1 if n % 2 else 0)
            self.assertEqual(r["origin"], "SIMULATED")
            self.assertEqual(r["authority"], "NONE")
            self.assertEqual(r["protocol"], PROTOCOL)
            self.assertAlmostEqual(sum(r["eigenvalues"]), 0, places=11)
            j = r["exchange"]
            self.assertTrue(np.allclose(r["eigenvalues"], sorted([-.75 * j, .25 * j, .25 * j, .25 * j])))
            self.assertAlmostEqual(r["excitation_gap"], abs(r["exchange"]), places=12)

    def test_negative_control_never_switches(self):
        self.assertTrue(all(r["ground_total_spin"] == 0 for r in ladder(parity_blind=True)))

    def test_strength_and_decay(self):
        gaps = [r["excitation_gap"] for r in ladder(3, 16)]
        self.assertTrue(all(a > b for a, b in zip(gaps, gaps[1:])))
        self.assertAlmostEqual(edge_spectrum(5, 1.5, 3)["excitation_gap"], 1.5 * math.exp(-1))

    def test_input_safety(self):
        for args in ((0, 1, 4), (2.1, 1, 4), (4, 0, 4), (4, 1, float("nan"))):
            with self.assertRaises(ValueError):
                edge_spectrum(*args)
        with self.assertRaises(ValueError):
            ladder(7, 3)


if __name__ == "__main__":
    unittest.main()
