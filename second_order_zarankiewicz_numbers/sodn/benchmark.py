"""Complete weak 7x7 enumeration and exact extension verification."""
from itertools import combinations
from .search import fano_base
from .bases import automorphisms
from .weak import weak_check
from .core import Geometry
from .io import ROOT,write_json,witness,verify,unpack
import json

class FixedWeak:
    """Bit-mask implementation independent of weak.py's cross-cell loops."""
    def __init__(self,e1,n,edges):
        self.n=n;self.base=sum(1<<c for c in e1);self.edges=edges
        self.masks=[sum(1<<c for c in e) for e in edges]
        self.rows=[{c//n for c in e} for e in edges]
        self.cols=[{c%n for c in e} for e in edges]
        self.opposite=[];self.requirements=[]
        for q,(a,b) in enumerate(edges):
            self.opposite.append((1<<(a//n*n+b%n))|(1<<(b//n*n+a%n)))
            req=[]
            for c in e1:
                r,j=divmod(c,n)
                if r in self.rows[q] or j in self.cols[q]:continue
                cells={i*n+j for i in self.rows[q]}|{r*n+l for l in self.cols[q]}
                req.append(sum(1<<c for c in cells)&~self.base)
            self.requirements.append(req)
        self.cross={}
        for a,b in combinations(range(len(edges)),2):
            if self.rows[a]&self.rows[b] or self.cols[a]&self.cols[b]:continue
            cells={r*n+c for r in self.rows[a] for c in self.cols[b]}|{
                   r*n+c for r in self.rows[b] for c in self.cols[a]}
            self.cross[a,b]=sum(1<<c for c in cells)&~self.base

    def check(self,selected,mask):
        for q in selected:
            if any(mask&req==req for req in self.requirements[q]):return False
        for a,b in combinations(selected,2):
            key=(min(a,b),max(a,b))
            req=self.cross.get(key)
            if req is not None and mask&req==req:return False
        allmask=mask|self.base;k=len(selected);parent=list(range(k))
        def find(x):
            while parent[x]!=x:x=parent[x]
            return x
        for i,j in combinations(range(k),2):
            if self.opposite[selected[i]]==self.masks[selected[j]]:
                parent[find(i)]=find(j)
        adj={find(i):set() for i in range(k)}
        for i,a in enumerate(selected):
            if allmask&self.opposite[a]!=self.opposite[a]:continue
            for j,b in enumerate(selected):
                if i!=j and self.opposite[a]&self.masks[b]:
                    x,y=find(i),find(j)
                    if x!=y:adj[x].add(y)
        indegree={i:0 for i in adj}
        for targets in adj.values():
            for b in targets:indegree[b]+=1
        todo=[i for i,d in indegree.items() if d==0];done=0
        while todo:
            a=todo.pop();done+=1
            for b in adj[a]:
                indegree[b]-=1
                if indegree[b]==0:todo.append(b)
        return done==len(adj)

def weak77_upper(save=True):
    e1=fano_base();free=tuple(c for c in range(49) if c not in e1)
    edges=[e for e in combinations(free,2) if weak_check(7,7,e1,[e])]
    rows=[sum(1<<(c%7) for c in e1 if c//7==r) for r in range(7)]
    maps=automorphisms(rows,7)
    orbit={tuple(sorted((mp[edges[0][0]],mp[edges[0][1]]))) for mp in maps}
    if orbit!=set(edges):raise AssertionError('Single-pair normalization is not exhaustive')
    checker=FixedWeak(e1,7,edges)
    counts=[0]*9;trials=0;sevens=[];eights=[]
    def visit(prefix,start,mask):
        nonlocal trials
        k=len(prefix);counts[k]+=1
        if k==7:sevens.append([list(edges[q]) for q in prefix])
        if k==8:eights.append([list(edges[q]) for q in prefix]);return
        for q in range(start,len(edges)):
            if mask&checker.masks[q]:continue
            trial=prefix+[q];trials+=1
            if checker.check(trial,mask|checker.masks[q]):
                visit(trial,q+1,mask|checker.masks[q])
    visit([0],1,checker.masks[0])
    report={'single_pairs':len(edges),'normalized_pair':list(edges[0]),
            'fixed_pair_accepted_prefix_counts':counts,'predicate_calls':trials,
            'first_seven':sevens[0] if sevens else [],
            'all_normalized_sevens':sevens,'total29_exists':bool(eights),
            'automorphism_count':len(maps)}
    if save:
        write_json(ROOT/'results'/'weak77_upper_python.json',report)
        write_json(ROOT/'certificates'/'fano_symmetry.json',
                   {'rows':rows,'automorphisms':maps,'valid_single_pairs':edges,'normalized_pair':edges[0]})
    if eights:raise AssertionError('The claimed weak upper bound is false')
    return report

def extensions(data,save=True):
    m,n,e1,e2=unpack(data);geo=Geometry(m,n)
    verify(data)
    occupied=set(e1)|{c for e in e2 for c in e}
    free=[c for c in range(m*n) if c not in occupied]
    decisions=[];number=0
    for edge in combinations(free,2):
        trial=list(e2)+[edge]
        filt=weak_check(m,n,e1,trial,explain=True,w3=False)
        rw=geo.check(e1,trial,False)
        accepted=filt['accepted'] and rw
        decisions.append({'edge':list(edge),'filter':filt,'rw3':rw,'accepted':accepted})
        if accepted:
            number+=1
            if save:
                extension=witness(m,n,e1,trial,'RW3',
                       {'algorithm':'all_disjoint_extensions','extension':list(edge),
                        'filter':"S,W2,W2prime,RW3"})
                verify(extension)
                write_json(ROOT/'witnesses'/f'RW3_7x7_total29_extension{number}.json',extension)
    report={'starting_witness':'weak_7x7_total28.json','candidates':len(decisions),
            'accepted_count':number,'decisions':decisions}
    if save:write_json(ROOT/'results'/'benchmark77_extensions.json',report)
    return report
