"""E1 graph generalization: deterministic synthetic tests and tamper controls."""
import tempfile
import unittest
from pathlib import Path
import torch
from phifieldlab.e1 import (
    TRAIN_FAMILIES, TEST_FAMILIES, RouteMPNN, dataset, baseline,
    reachable, train, verify, resolve_device
)

class E1Tests(unittest.TestCase):
    def test_reachability_bridge_and_cycle(self):
        edges=[(0,1),(1,2),(2,0),(2,3)]
        self.assertTrue(reachable(4,edges[:-1],0,2))
        self.assertFalse(reachable(4,edges[:-1],2,3))
        self.assertFalse(reachable(4,[(0,1),(1,2)],0,2,max_hops=1))
        self.assertTrue(reachable(4,[(0,1),(1,2)],0,2,max_hops=2))

    def test_isolated_holdout_and_balanced_labels(self):
        self.assertFalse(set(TRAIN_FAMILIES)&set(TEST_FAMILIES))
        for split in ("train","validation","test"):
            data=dataset(60,123,split)
            self.assertEqual(data["y"].sum().item(),30)
            self.assertEqual(len(data["families"]),60)
            self.assertEqual(baseline(data,None)["overall"]["accuracy"],1.)
            self.assertEqual(baseline(data,1)["overall"]["accuracy"],.5)
            self.assertEqual(data["sha256"],dataset(60,123,split)["sha256"])
            self.assertNotEqual(data["sha256"],dataset(60,124,split)["sha256"])

    def test_graph_padding_and_explicit_markers(self):
        data=dataset(60,369,"test")
        for i in range(60):
            n=int(data["node_mask"][i].sum())
            e=int(data["edge_mask"][i].sum())
            self.assertTrue(5<=n<=12)
            self.assertTrue(0<e<=20)
            self.assertEqual(data["node"][i,:n,0].sum().item(),1)
            self.assertEqual(data["node"][i,:n,1].sum().item(),1)
            self.assertEqual(data["edge_mask"][i,e:].sum().item(),0)

    def test_actual_neighbor_gradients(self):
        torch.manual_seed(123)
        model=RouteMPNN(width=8,rounds=2)
        sample=dataset(6,369,"train")
        batch={k:v for k,v in sample.items() if torch.is_tensor(v)}
        output=model(batch)
        self.assertEqual(tuple(output.shape),(6,))
        torch.nn.BCEWithLogitsLoss()(output,sample["y"]).backward()
        grad=model.message[0].weight.grad
        self.assertIsNotNone(grad)
        self.assertGreater(grad.abs().sum().item(),0.)

    def test_train_replay_tamper_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"trial"
            result=train(out,seed=369,epochs=2,train_count=36,validation_count=12,
                         test_count=18,width=8,rounds=2,device="cpu")
            self.assertIn("learned",result["comparison"]["test"])
            self.assertTrue(verify(out)["ok"])
            with self.assertRaises(FileExistsError):
                train(out,seed=369,epochs=1,train_count=6,validation_count=6,test_count=6)
            path=out/"report.json"
            path.write_bytes(path.read_bytes()+b" ")
            with self.assertRaisesRegex(ValueError,"SHA-256 mismatch"):
                verify(out)

    def test_cuda_explicit_request(self):
        if not torch.cuda.is_available():
            with self.assertRaisesRegex(RuntimeError,"CUDA explicitly requested"):
                resolve_device("cuda")
        self.assertEqual(resolve_device("cpu"),"cpu")

if __name__=="__main__":
    unittest.main()
