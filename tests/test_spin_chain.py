"""QP1 physics invariants: independent of QP0's edge parity assumption."""
import json
import unittest
from pathlib import Path
import numpy as np
from numpy.testing import assert_allclose
from phifieldlab.spin_chain import sector_hamiltonian, chain_spectrum, browser_reference

class FiniteSpin1Tests(unittest.TestCase):
    def test_known_two_site_spectrum(self):
        h = sector_hamiltonian(2, 0).toarray()
        assert_allclose(np.linalg.eigvalsh(h), [-2., -1., 1.], atol=1e-12)

    def test_hermiticity(self):
        for boundary in ('open', 'periodic'):
            for m in (0, 1, 2):
                h = sector_hamiltonian(4, m, boundary=boundary)
                diff = h - h.T
                self.assertEqual(diff.nnz == 0 or abs(diff).max() < 1e-12, True)

    def test_open_parity_emerges_from_H(self):
        for n in range(3, 9):
            result = chain_spectrum(n)
            self.assertEqual(result['ground_total_spin'], n % 2)
            self.assertGreater(result['lowest_excitation_gap'], 0)
            self.assertEqual(result['origin'], 'SIMULATED')
            self.assertEqual(result['authority'], 'NONE')

    def test_periodic_control(self):
        open_triangle = chain_spectrum(3, 'open')
        ring_triangle = chain_spectrum(3, 'periodic')
        self.assertEqual(open_triangle['ground_total_spin'], 1)
        self.assertEqual(ring_triangle['ground_total_spin'], 0)
        self.assertNotEqual(open_triangle['sector_minima']['1'],
                            ring_triangle['sector_minima']['1'])
        self.assertEqual([chain_spectrum(n, 'periodic')['ground_total_spin']
                          for n in range(3, 9)], [0] * 6)

    def test_frozen_browser_data_replays_within_tolerance(self):
        artifact = Path(__file__).resolve().parents[1] / 'web/src/data/qp1-reference.json'
        saved = json.loads(artifact.read_text(encoding='utf-8'))
        computed = browser_reference()
        self.assertEqual(saved['origin'], 'SIMULATED')
        self.assertEqual(saved['authority'], 'NONE')
        self.assertFalse(saved['attested'])
        for boundary in ('open', 'periodic_negative_control'):
            for actual, replay in zip(saved[boundary], computed[boundary]):
                self.assertEqual(actual['n'], replay['n'])
                self.assertEqual(actual['ground_total_spin'], replay['ground_total_spin'])
                self.assertEqual(actual['sector_dimensions'], replay['sector_dimensions'])
                for field in ('ground_energy', 'lowest_excitation_gap'):
                    self.assertLess(abs(actual[field] - replay[field]), 1e-7)
                for sector in ('0','1','2'):
                    self.assertLess(abs(actual['sector_minima'][sector] -
                                        replay['sector_minima'][sector]), 1e-7)

    def test_reject_bad_inputs(self):
        for kw in ({'n': 9}, {'n': 0}, {'n': True}, {'n': 4, 'coupling': 0},
                   {'n': 3, 'boundary': 'invalid'}, {'n': 2, 'boundary': 'periodic'},
                   {'n': 3, 'magnetization': 9}):
            with self.assertRaises(ValueError):
                sector_hamiltonian(**kw)
        with self.assertRaises(ValueError):
            browser_reference(9, 10)

if __name__ == '__main__':
    unittest.main()
