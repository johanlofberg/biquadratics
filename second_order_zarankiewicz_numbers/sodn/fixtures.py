"""Explicit manuscript supports and generated chain/incidence witnesses."""
from itertools import combinations
from .reference import chain_instance,p3_incidence_instance
from .io import ROOT,write_json,witness,verify

def export_fixtures():
    results={}
    def save(name,m,n,e1,e2,criterion='RW3+'):
        flat=lambda c:(c[0]-1)*n+c[1]-1
        data=witness(m,n,[flat(c) for c in e1],
                    [(flat(a),flat(b)) for a,b in e2],criterion,
                    {'algorithm':'explicit manuscript construction','name':name})
        results[name]=verify(data)
        write_json(ROOT/'witnesses'/(name+'.json'),data)
    e1=[(1,2),(1,3),(1,4),(2,1),(2,2),(3,4),(4,1),(4,4),(5,1),(5,3)]
    e2=[((3,1),(4,2)),((5,2),(3,3)),((4,3),(2,4))]
    save('paper_5x4',5,4,e1,e2,'RW3')
    e1=[(1,1),(1,2),(2,1),(2,3),(3,2),(3,3)]+[(i,1) for i in range(4,9)]+[(9,2),(10,2)]
    e2=[((10,3),(9,1)),((4,2),(4,3)),((5,3),(2,2)),((1,3),(6,2)),
        ((3,1),(9,3)),((7,2),(6,3)),((5,2),(8,3))]
    save('paper_10x3',10,3,e1,e2,'RW3')
    e1=[(1,1),(1,2),(2,1),(2,3),(3,2),(3,3)]+[(i,1) for i in range(4,9)]+[(i,2) for i in range(9,13)]+[(13,3)]
    e2=[((1,3),(6,2)),((2,2),(5,3)),((3,1),(9,3)),((4,2),(4,3)),
        ((5,2),(8,3)),((6,3),(7,2)),((9,1),(10,3)),((11,1),(12,3)),
        ((11,3),(12,1)),((13,1),(13,2))]
    for m in (13,14,15):
        if m==14:
            e1.append((14,3));e2.pop()
            e2.extend([((13,1),(14,2)),((13,2),(14,1))])
        elif m==15:e1.append((15,2));e2.append(((10,1),(15,3)))
        save(f'paper_{m}x3',m,3,e1,e2)
    for m in range(3,51):
        e1,e2=chain_instance(m)
        save(f'chain_{m}x3',m,3,e1,e2,'RW3')
    e1,e2,_=p3_incidence_instance()
    save('incidence_p3',15,6,e1,e2,'SD')
    oldrows=list(combinations(range(1,7),2))
    for n in (7,8,9,10):
        rows=list(combinations(range(1,n+1),2));lookup={r:i+1 for i,r in enumerate(rows)}
        e1n=[(lookup[r],c) for r in rows for c in r]
        e2n=[tuple((lookup[oldrows[i-1]],j) for i,j in pair) for pair in e2]
        save(f'padded_p3_N{n}',len(rows),n,e1n,e2n,'SD')
    write_json(ROOT/'results'/'explicit_verification.json',results)
    return results
