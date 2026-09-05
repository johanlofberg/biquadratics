"""An independent integer implementation of the exact RW3/RW3+ closure.

Cells are flattened zero-based integers r*n+c. A rectangle contributes one
component for the *knowledge* of either diagonal's prescribed value.
Line pairs and rectangles with holes are grounded. Resolving a selected
two-edge merges the knowledge components for its two representatives.
No parity/odd-cycle inference is performed: this is exactly RW3(+), not SD.
"""
from itertools import combinations

def validate(m,n,e1,e2):
    e1=tuple(e1); e2=tuple(tuple(e) for e in e2)
    allcells=list(e1)+[c for e in e2 for c in e]
    if any(len(e)!=2 for e in e2) or len(set(allcells))!=len(allcells):
        raise ValueError("The selected supports are not simple")
    if any(not isinstance(c,int) or c<0 or c>=m*n for c in allcells):
        raise ValueError("Cell outside grid")
    return e1,e2

def c4_free(n,e1):
    rows={}
    for c in e1:
        r,j=divmod(c,n); rows[r]=rows.get(r,0)|(1<<j)
    return all((a&b).bit_count()<=1 for a,b in combinations(rows.values(),2))

class Geometry:
    def __init__(self,m,n):
        self.m,self.n,self.size=m,n,m*n
        self.component=[[0]*(m*n) for _ in range(m*n)]
        self.rectangles=[]
        for i,k in combinations(range(m),2):
            for j,l in combinations(range(n),2):
                a,b,c,d=i*n+j,k*n+l,i*n+l,k*n+j
                self.rectangles.append((a,b,c,d))
                t=len(self.rectangles)
                self.component[a][b]=self.component[b][a]=t
                self.component[c][d]=self.component[d][c]=t
        self.rect_masks=[sum(1<<c for c in rect) for rect in self.rectangles]
        self.allmask=(1<<(m*n))-1

    def check(self,e1,e2,plus=True,details=False):
        # Enumeration supplies validated disjoint matchings. External callers
        # must call validate; witness verification does so unconditionally.
        occupied=list(e1)+[c for e in e2 for c in e]
        mask=sum(1<<c for c in occupied)
        parent=[0]+[0 if rm&mask!=rm else i for i,rm in enumerate(self.rect_masks,1)]
        component=self.component
        edges=[(a,b,component[a][b]) for a,b in e2]
        if plus:
            seen=set()
            for a,b,t in edges:
                if t in seen: parent[t]=0
                seen.add(t)
        def find(x):
            while parent[x]!=x:
                parent[x]=parent[parent[x]]
                x=parent[x]
            return x
        pending=list(range(len(edges))); resolved=[]
        while pending:
            todo=[q for q in pending if find(edges[q][2])==0]
            if not todo: break
            done=set(todo); pending=[q for q in pending if q not in done]
            for q in todo:
                a,b,t=edges[q]; resolved.append(q)
                for c in occupied:
                    if c==a or c==b:continue
                    ra,rb=find(component[a][c]),find(component[b][c])
                    if ra!=rb:
                        if ra>rb:ra,rb=rb,ra
                        parent[rb]=ra
        residual={find(t) for t in range(1,len(parent))}-{0}
        accepted=not pending and not residual
        if not details:return accepted
        return {'accepted':accepted,'resolved':not pending,
                'unresolved_edges':pending,'resolution_order':resolved,
                'residual_components':len(residual),
                'criterion':'RW3+' if plus else 'RW3'}
