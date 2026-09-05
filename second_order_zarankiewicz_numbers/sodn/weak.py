"""Literal weak admissibility, with complementary pairs contracted."""
from itertools import combinations
from .core import validate,c4_free

def weak_check(m,n,e1,e2,explain=False,w3=True):
    validate(m,n,e1,e2)
    def result(ok,reason):
        return {'accepted':ok,'reason':reason} if explain else ok
    if not c4_free(n,e1):return result(False,'W1')
    occupied=set(e1)|{c for e in e2 for c in e}
    incidence=set(e1); count=len(e2)
    rows=[{c//n for c in e} for e in e2]
    cols=[{c%n for c in e} for e in e2]
    nd=[i for i in range(count) if len(rows[i])==len(cols[i])==2]
    opposite={}
    for i in nd:
        a,b=e2[i]; opposite[i]={(a//n)*n+b%n,(b//n)*n+a%n}
        if opposite[i]<=incidence:return result(False,"W2'")
    parent=list(range(count))
    def find(a):
        while parent[a]!=a:
            parent[a]=parent[parent[a]];a=parent[a]
        return a
    for i,j in combinations(nd,2):
        if set(e2[j])==opposite[i]:parent[find(i)]=find(j)
    adj={find(i):set() for i in nd}
    for i in nd:
        if opposite[i]<=occupied:
            for j in nd:
                if i!=j and opposite[i]&set(e2[j]):
                    a,b=find(i),find(j)
                    if a!=b:adj[a].add(b)
    visiting=set();visited=set()
    def cycle(a):
        if a in visiting:return True
        if a in visited:return False
        visiting.add(a)
        if any(cycle(b) for b in adj[a]):return True
        visiting.remove(a);visited.add(a)
        return False
    if any(cycle(a) for a in adj):return result(False,'W2')
    if w3:
        supports=[(c,) for c in e1]+list(e2)
        rs=[{c//n for c in e} for e in supports]
        cs=[{c%n for c in e} for e in supports]
        for i,j in combinations(range(len(supports)),2):
            if len(supports[i])==len(supports[j])==1:continue
            if rs[i]&rs[j] or cs[i]&cs[j]:continue
            if all(r*n+c in occupied for r in rs[i] for c in cs[j]) and all(
                   r*n+c in occupied for r in rs[j] for c in cs[i]):
                return result(False,'W3')
    return result(True,'accepted')
