import tempfile
import unittest
from pathlib import Path
import torch
from phifieldlab.core import EdgePoolNet, make_dataset, freeze_seed, score, train, verify

class SyntheticProtocolTests(unittest.TestCase):
    def test_separated_size_families(self):
        a = make_dataset(64, 100, 'train'); b = make_dataset(64, 100, 'test')
        self.assertLessEqual(int(a.sizes.max()), 6)
        self.assertGreaterEqual(int(b.sizes.min()), 7)
        self.assertNotEqual(a.sha256(), b.sha256())

    def test_generator_is_deterministic(self):
        self.assertEqual(make_dataset(32, 12, 'train').sha256(), make_dataset(32, 12, 'train').sha256())

    def test_closure_baseline_and_controls(self):
        d = make_dataset(512, 369, 'test')
        pred = (d.residue.abs().numpy().ravel() > 0.4)
        self.assertTrue((pred == d.label.numpy().ravel().astype(bool)).all())

    def test_permutation_invariance_and_mask(self):
        freeze_seed(100)
        m = EdgePoolNet().eval()
        d = make_dataset(3, 17, 'train')
        with torch.no_grad():
            a = m(d.edges, d.mask)
            idx = torch.randperm(12)
            b = m(d.edges[:,idx], d.mask[:,idx])
            self.assertTrue(torch.allclose(a, b, atol=1e-6))

    def test_training_checkpoint_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'trial'
            train(seed=369, epochs=5, train_count=96, val_count=32, test_count=32, device='cpu', out=out)
            self.assertTrue(verify(out)['replay_verified'])
            with self.assertRaises(FileExistsError):
                train(seed=369, epochs=5, train_count=96, val_count=32, test_count=32, device='cpu', out=out)
            with open(out/'report.json','a') as f: f.write('tamper')
            with self.assertRaises(ValueError): verify(out)

if __name__ == '__main__':
    unittest.main()
