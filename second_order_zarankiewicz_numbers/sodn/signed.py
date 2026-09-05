from itertools import combinations
from collections import defaultdict, deque
from dataclasses import dataclass

class DSU:
    def __init__(self, xs): self.p={x:x for x in xs}; self.r={x:0 for x in xs}
    def find(self,x):
        p=self.p[x]
        if p!=x:self.p[x]=self.find(p)
        return self.p[x]
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a==b:return False
        if self.r[a]<self.r[b]:a,b=b,a
        self.p[b]=a
        if self.r[a]==self.r[b]:self.r[a]+=1
        return True

def signed_deviation(m,n,e1,e2, trace=False):
    e1=[tuple(x) for x in e1]; e2=[(tuple(a),tuple(b)) for a,b in e2]
    occupied=set(e1)
    for a,b in e2:
        if a in occupied or b in occupied or a==b: raise ValueError('not simple')
        occupied.add(a);occupied.add(b)
    selected={frozenset((a,b)) for a,b in e2}
    dsu=DSU(occupied)
    # line-degenerate 2-edges are immediately resolved
    for a,b in e2:
        if a[0]==b[0] or a[1]==b[1]: dsu.union(a,b)

    def build():
        roots=sorted({dsu.find(x) for x in occupied})
        rid={r:i for i,r in enumerate(roots)}
        members=defaultdict(list)
        for x in occupied: members[dsu.find(x)].append(x)
        nodes={}
        pairroots=[]
        for a,b in combinations(roots,2):
            nodes[frozenset((a,b))]=len(pairroots); pairroots.append((a,b))
        adj=[[] for _ in pairroots]; ground=set(); ineq=set()
        # line grounds: any support representatives share row/col => deviation zero
        for k,(ra,rb) in enumerate(pairroots):
            if any(x[0]==y[0] or x[1]==y[1] for x in members[ra] for y in members[rb]):
                ground.add(k)
        # unresolved E2 inequalities / degenerate grounds
        unresolved=[]
        for a,b in e2:
            ra,rb=dsu.find(a),dsu.find(b)
            if ra==rb: continue
            key=frozenset((ra,rb)); k=nodes[key]; unresolved.append((a,b,k))
            ineq.add(k)
            if a[0]==b[0] or a[1]==b[1]: ground.add(k)
        def diag_node(p,q):
            if p not in occupied or q not in occupied: return None
            rp,rq=dsu.find(p),dsu.find(q)
            if rp==rq:return None
            return nodes[frozenset((rp,rq))]
        # rectangle equations d_A + d_B=0
        for i,k in combinations(range(1,m+1),2):
            for j,l in combinations(range(1,n+1),2):
                a=diag_node((i,j),(k,l)); b=diag_node((i,l),(k,j))
                if a is None and b is None: continue
                if a is None: ground.add(b)
                elif b is None: ground.add(a)
                elif a==b: ground.add(a)
                else:
                    adj[a].append(b);adj[b].append(a)
        # parity components
        parity={}; forced=set(); comps=[]
        for start in range(len(pairroots)):
            if start in parity:continue
            parity[start]=0; q=deque([start]); comp=[]; odd=False
            while q:
                v=q.popleft();comp.append(v)
                for w in adj[v]:
                    want=parity[v]^1
                    if w not in parity: parity[w]=want;q.append(w)
                    elif parity[w]!=want: odd=True
            g=any(v in ground for v in comp)
            ip={parity[v] for v in comp if v in ineq}
            both=(0 in ip and 1 in ip)
            if odd or g or both: forced.update(comp)
            comps.append((comp,odd,g,both))
        return roots,pairroots,ground,ineq,forced,unresolved,comps,parity

    rounds=0
    while True:
        rounds+=1
        roots,pairs,ground,ineq,forced,unresolved,comps,parity=build()
        changed=False
        for a,b,k in unresolved:
            if k in forced:
                changed |= dsu.union(a,b)
        if trace:
            print('round',rounds,'roots',len(roots),'unresE2',len(unresolved),'nodes',len(pairs),'forced',len(forced),'changed',changed)
        if not changed: break
        if rounds>len(e2)+2: raise RuntimeError('loop')
    allresolved=all(dsu.find(a)==dsu.find(b) for a,b in e2)
    roots,pairs,ground,ineq,forced,unresolved,comps,parity=build()
    free=[c for c in comps if not (c[1] or c[2] or c[3])]
    return {'all_e2_resolved':allresolved,'roots':len(roots),'nodes':len(pairs),'forced':len(forced),'free_components':len(free),'accepted':allresolved and len(forced)==len(pairs),'rounds':rounds,'unresolved_e2':len(unresolved)}

