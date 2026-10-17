"""E1 candidate: message passing on synthetic alternate-route graphs.

SIMULATED / authority NONE. Not a physics finding or an NBG proof.
No pretrained or third-party model weights are used.
"""
from __future__ import annotations
import argparse, hashlib, json, random
from collections import deque
from pathlib import Path
import numpy as np
import torch
from torch import nn
from safetensors.torch import save_file, load_file

PROTOCOL = "PHIFIELD_E1_ALTERNATE_ROUTE_V1"
ORIGIN = "SIMULATED"
TRAIN_FAMILIES = ("ring_tail", "barbell", "chord_tail")
TEST_FAMILIES = ("ladder_tail", "wheel_tail", "double_square")
MAX_NODES, MAX_EDGES = 12, 20

def freeze_seed(seed: int) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)

def edges_for_family(name: str, gen: np.random.Generator):
    if name == "ring_tail":
        n = int(gen.integers(5, 8))
        edges = [(i, (i+1)%n) for i in range(n)]
        tail = int(gen.integers(1, 3))
        edges.append((0,n))
        if tail == 2:
            edges.append((n,n+1))
        return n+tail, edges
    if name == "barbell":
        a = int(gen.integers(3,5)); b = int(gen.integers(3,5))
        edges = ([(i,(i+1)%a) for i in range(a)] +
                 [(a+i,a+(i+1)%b) for i in range(b)] + [(0,a)])
        return a+b, edges
    if name == "chord_tail":
        n = int(gen.integers(5,8))
        return n+1, [(i,(i+1)%n) for i in range(n)] + [(0,n//2),(1,n)]
    if name == "ladder_tail":
        r = int(gen.integers(3,5)); n = 2*r
        edges = ([(i,i+1) for i in range(r-1)] +
                 [(r+i,r+i+1) for i in range(r-1)] +
                 [(i,r+i) for i in range(r)] + [(0,n)])
        return n+1, edges
    if name == "wheel_tail":
        rim = int(gen.integers(5,8)); hub = rim
        return rim+2, ([(i,(i+1)%rim) for i in range(rim)] +
                       [(hub,i) for i in range(rim)] + [(hub,hub+1)])
    if name == "double_square":
        return 8, ([(i,(i+1)%4) for i in range(4)] +
                   [(4+i,4+(i+1)%4) for i in range(4)] + [(0,4)])
    raise ValueError("unknown graph family: " + str(name))

def reachable(n: int, edges: list[tuple[int,int]], source: int, target: int, max_hops: int|None=None) -> bool:
    adjacent = [[] for _ in range(n)]
    for u,v in edges:
        adjacent[u].append(v); adjacent[v].append(u)
    queue = deque([(source,0)]); seen={source}
    while queue:
        u, distance = queue.popleft()
        if u==target:
            return True
        if max_hops is not None and distance>=max_hops:
            continue
        for v in adjacent[u]:
            if v not in seen:
                seen.add(v); queue.append((v,distance+1))
    return False

def dataset(count: int, seed: int, split: str):
    if split not in {"train","validation","test"}:
        raise ValueError("invalid split")
    if not 1<=count<=100000:
        raise ValueError("count out of bounds")
    gen=np.random.default_rng(seed)
    families=TRAIN_FAMILIES if split!="test" else TEST_FAMILIES
    src=np.zeros((count,MAX_EDGES),dtype=np.int64); dst=np.zeros_like(src)
    values=np.zeros((count,MAX_EDGES,1),dtype=np.float32)
    edge_mask=np.zeros((count,MAX_EDGES),dtype=np.float32)
    nodes=np.zeros((count,MAX_NODES,3),dtype=np.float32)
    node_mask=np.zeros((count,MAX_NODES),dtype=np.float32)
    labels=np.zeros(count,dtype=np.float32); identifiers=[]
    for i in range(count):
        family=families[i%len(families)]; n,topology=edges_for_family(family,gen)
        if n>MAX_NODES or len(topology)>MAX_EDGES:
            raise AssertionError("template exceeds padding limits")
        requested=(i//len(families))%2
        candidates=[]
        for j,(u,v) in enumerate(topology):
            others=topology[:j]+topology[j+1:]
            if int(reachable(n,others,u,v))==requested:
                candidates.append(j)
        if not candidates:
            raise AssertionError("no candidate for requested class")
        removed=int(gen.choice(candidates))
        a,b=topology[removed]
        remaining=topology[:removed]+topology[removed+1:]
        permutation=gen.permutation(n)
        a,b=int(permutation[a]),int(permutation[b])
        if gen.integers(0,2):
            a,b=b,a
        permuted=[(int(permutation[u]),int(permutation[v])) for u,v in remaining]
        gen.shuffle(permuted)
        potentials=gen.uniform(-1,1,size=n)
        for j,(u,v) in enumerate(permuted):
            if int(gen.integers(0,2)):
                u,v=v,u
            src[i,j]=u; dst[i,j]=v
            values[i,j,0]=np.float32(potentials[v]-potentials[u]+gen.normal(0,.015))
            edge_mask[i,j]=1.
        nodes[i,:n,2]=1.; nodes[i,a,0]=1.; nodes[i,b,1]=1.
        node_mask[i,:n]=1.; labels[i]=requested; identifiers.append(family)
        if reachable(n,[(int(permutation[u]),int(permutation[v])) for u,v in remaining],a,b)!=bool(requested):
            raise AssertionError("graph label construction failed")
    tensors=(src,dst,values,edge_mask,nodes,node_mask,labels)
    h=hashlib.sha256()
    for item in tensors:
        h.update(str(item.shape).encode()); h.update(str(item.dtype).encode()); h.update(item.tobytes(order="C"))
    h.update(json.dumps(identifiers,separators=(",",":")).encode())
    return {"src":torch.from_numpy(src),"dst":torch.from_numpy(dst),
            "edge_value":torch.from_numpy(values),"edge_mask":torch.from_numpy(edge_mask),
            "node":torch.from_numpy(nodes),"node_mask":torch.from_numpy(node_mask),
            "y":torch.from_numpy(labels),"families":identifiers,"sha256":h.hexdigest()}

class RouteMPNN(nn.Module):
    """Real shared graph-neighbor messages; padded nonedges carry zero message."""
    def __init__(self,width: int=32,rounds: int=7):
        super().__init__()
        self.width=width; self.rounds=rounds
        self.encoder=nn.Linear(3,width)
        self.message=nn.Sequential(nn.Linear(width+1,width),nn.ReLU(),nn.Linear(width,width))
        self.update=nn.GRUCell(width,width)
        self.head=nn.Sequential(nn.Linear(width,width),nn.ReLU(),nn.Linear(width,1))
    def forward(self,batch):
        x=batch["node"]; edge=batch["edge_value"]
        src=batch["src"]; dst=batch["dst"]; mask=batch["edge_mask"]
        B,V,_=x.shape; W=self.width
        h=torch.tanh(self.encoder(x))
        si=src[...,None].expand(-1,-1,W); di=dst[...,None].expand(-1,-1,W)
        degrees=torch.zeros((B,V,1),dtype=h.dtype,device=h.device)
        degrees.scatter_add_(1,src[...,None],mask[...,None])
        degrees.scatter_add_(1,dst[...,None],mask[...,None])
        for _ in range(self.rounds):
            hs=h.gather(1,si); hd=h.gather(1,di)
            fm=self.message(torch.cat([hs,edge],-1))*mask[...,None]
            bm=self.message(torch.cat([hd,-edge],-1))*mask[...,None]
            agg=torch.zeros_like(h)
            agg.scatter_add_(1,di,fm); agg.scatter_add_(1,si,bm)
            h=self.update((agg/degrees.clamp(min=1)).reshape(-1,W),h.reshape(-1,W)).reshape(B,V,W)
            h=h*batch["node_mask"][...,None]
        target=batch["node"][:,:,1].argmax(dim=1)
        return self.head(h[torch.arange(B,device=h.device),target]).flatten()

def packed(batch,indices,device):
    return {key:v[indices].to(device) for key,v in batch.items() if torch.is_tensor(v)}

def metrics(pred,label,families):
    def score(index):
        a=np.asarray(index,dtype=int);p=pred[a];y=label[a]
        return {"n":int(len(a)),"accuracy":float((p==y).mean()),
                "tp":int((p&y).sum()),"tn":int((~p&~y).sum()),
                "fp":int((p&~y).sum()),"fn":int((~p&y).sum())}
    return {"overall":score(range(len(label))),
            "by_family":{name:score([i for i,f in enumerate(families) if f==name])
                         for name in sorted(set(families))}}

def evaluate(model,data,device):
    model.eval(); predictions=[]
    with torch.no_grad():
        for start in range(0,len(data["y"]),64):
            idx=torch.arange(start,min(start+64,len(data["y"])))
            predictions.extend((torch.sigmoid(model(packed(data,idx,device)))>=.5).cpu().tolist())
    return metrics(np.array(predictions,dtype=bool),data["y"].numpy().astype(bool),data["families"])

def baseline(data,max_hops):
    pred=[]
    for i in range(len(data["y"])):
        n=int(data["node_mask"][i].sum()); e=int(data["edge_mask"][i].sum())
        edges=list(zip(data["src"][i,:e].tolist(),data["dst"][i,:e].tolist()))
        a=int(data["node"][i,:,0].argmax());b=int(data["node"][i,:,1].argmax())
        pred.append(reachable(n,edges,a,b,max_hops=max_hops))
    return metrics(np.array(pred,dtype=bool),data["y"].numpy().astype(bool),data["families"])

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def resolve_device(requested):
    if requested=="cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA explicitly requested but unavailable")
    return "cuda" if requested=="cuda" or (requested=="auto" and torch.cuda.is_available()) else "cpu"

def train(out: Path, *, seed=369, epochs=30, train_count=960, validation_count=240,
          test_count=360,width=32,rounds=7,device="cpu"):
    out=Path(out)
    if out.exists():
        raise FileExistsError("refusing to overwrite prior experiment directory: "+str(out))
    for count in (train_count,validation_count,test_count):
        if count<6 or count>100000 or count%6:
            raise ValueError("dataset count must be multiple of six, 6..100000")
    if not 1<=epochs<=300 or not 4<=width<=256 or not 1<=rounds<=16:
        raise ValueError("hyperparameter outside supported range")
    dev=resolve_device(device);freeze_seed(seed)
    samples={split:dataset(count,seed+offset,split) for split,count,offset in
             (("train",train_count,101),("validation",validation_count,202),("test",test_count,303))}
    model=RouteMPNN(width,rounds).to(dev)
    optimizer=torch.optim.AdamW(model.parameters(),lr=.004,weight_decay=.0001)
    criterion=nn.BCEWithLogitsLoss()
    best_loss=float("inf"); best_weights=None;history=[]
    for epoch in range(epochs):
        model.train(); indices=torch.randperm(train_count);running=0.
        for idx in indices.split(48):
            batch=packed(samples["train"],idx,dev)
            optimizer.zero_grad(set_to_none=True)
            loss=criterion(model(batch),batch["y"])
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);optimizer.step()
            running+=float(loss.item())*len(idx)
        model.eval()
        with torch.no_grad():
            valid=0.
            for start in range(0,validation_count,48):
                idx=torch.arange(start,min(start+48,validation_count))
                batch=packed(samples["validation"],idx,dev)
                valid+=float(criterion(model(batch),batch["y"]).item())*len(idx)
        valid/=validation_count
        history.append({"epoch":epoch+1,"train_loss":running/train_count,"validation_loss":valid})
        if valid<best_loss:
            best_loss=valid
            best_weights={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
    model.load_state_dict(best_weights)
    comparison={}
    for split in ("train","validation","test"):
        data=samples[split]
        comparison[split]={"dataset_sha256":data["sha256"],"learned":evaluate(model,data,dev),
                           "one_hop":baseline(data,1),"two_hop":baseline(data,2),
                           "exact_bfs":baseline(data,None)}
    test=comparison["test"]
    promotion=(test["learned"]["overall"]["accuracy"]>=.8 and
               test["learned"]["overall"]["accuracy"]>=test["two_hop"]["overall"]["accuracy"]+.05 and
               all(v["accuracy"]>=.7 for v in test["learned"]["by_family"].values()))
    config={"protocol":PROTOCOL,"seed":seed,"epochs":epochs,"width":width,"rounds":rounds,
            "train_count":train_count,"validation_count":validation_count,"test_count":test_count,
            "train_families":TRAIN_FAMILIES,"test_families":TEST_FAMILIES,"device":dev}
    report={"protocol":PROTOCOL,"origin":ORIGIN,"authority":"NONE","independent_attestation":False,
            "claim":"Synthetic graph alternate-route classification only. Not NBG empirical evidence.",
            "families_held_out":True,"best_validation_loss":best_loss,
            "test_promotion_gate":"PASS" if promotion else "FAIL_OR_INCONCLUSIVE",
            "comparison":comparison,"train_history":history}
    out.mkdir(parents=True,exist_ok=False)
    save_file({k:v.contiguous() for k,v in best_weights.items()},str(out/"model.safetensors"))
    (out/"config.json").write_text(json.dumps(config,indent=2,sort_keys=True)+"\n")
    (out/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    manifest={"protocol":PROTOCOL,"origin":ORIGIN,"authority":"NONE","attested":False,
              "sha256":{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    return report

def verify(out: Path, *, device="cpu"):
    out=Path(out)
    manifest=json.loads((out/"manifest.json").read_text())
    config=json.loads((out/"config.json").read_text())
    report=json.loads((out/"report.json").read_text())
    if any(obj["protocol"]!=PROTOCOL for obj in (manifest,config,report)):
        raise ValueError("wrong protocol")
    if manifest.get("origin")!=ORIGIN or manifest.get("authority")!="NONE" or manifest.get("attested") is not False:
        raise ValueError("unsupported provenance claim")
    if set(manifest["sha256"])!={"model.safetensors","config.json","report.json"}:
        raise ValueError("artifact set mismatch")
    for name,expected in manifest["sha256"].items():
        if sha(out/name)!=expected:
            raise ValueError("SHA-256 mismatch: "+name)
    dev=resolve_device(device);freeze_seed(int(config["seed"]))
    model=RouteMPNN(int(config["width"]),int(config["rounds"]))
    model.load_state_dict(load_file(str(out/"model.safetensors"),device="cpu"))
    model=model.to(dev)
    for split,count,offset in (("train",int(config["train_count"]),101),
                               ("validation",int(config["validation_count"]),202),
                               ("test",int(config["test_count"]),303)):
        data=dataset(count,int(config["seed"])+offset,split)
        if data["sha256"]!=report["comparison"][split]["dataset_sha256"]:
            raise ValueError("dataset reproducibility failure: "+split)
        new=evaluate(model,data,dev);old=report["comparison"][split]["learned"]
        if new!=old:
            raise ValueError("checkpoint replay mismatch: "+split)
        for key,hops in (("one_hop",1),("two_hop",2),("exact_bfs",None)):
            if baseline(data,hops)!=report["comparison"][split][key]:
                raise ValueError("baseline mismatch: "+split+"/"+key)
    return {"ok":True,"protocol":PROTOCOL,"origin":ORIGIN,"authority":"NONE",
            "test_accuracy":report["comparison"]["test"]["learned"]["overall"]["accuracy"],
            "test_promotion_gate":report["test_promotion_gate"],
            "hash_verified":True,"checkpoint_replayed":True}

def main():
    parser=argparse.ArgumentParser(description="PhiField E1 alternative-route graph lab")
    commands=parser.add_subparsers(dest="action",required=True)
    t=commands.add_parser("train")
    t.add_argument("--out",type=Path,required=True)
    for name,default in (("seed",369),("epochs",30),("train-count",960),
                         ("validation-count",240),("test-count",360),("width",32),("rounds",7)):
        t.add_argument("--"+name,type=int,default=default)
    t.add_argument("--device",choices=["auto","cpu","cuda"],default="cpu")
    v=commands.add_parser("verify")
    v.add_argument("--out",type=Path,required=True)
    v.add_argument("--device",choices=["auto","cpu","cuda"],default="cpu")
    args=parser.parse_args()
    if args.action=="train":
        r=train(args.out,seed=args.seed,epochs=args.epochs,train_count=args.train_count,
                validation_count=args.validation_count,test_count=args.test_count,
                width=args.width,rounds=args.rounds,device=args.device)
        print(json.dumps({"run":str(args.out),"test":r["comparison"]["test"],
                          "gate":r["test_promotion_gate"]},indent=2))
    else:
        print(json.dumps(verify(args.out,device=args.device),indent=2))

if __name__=="__main__":
    main()
