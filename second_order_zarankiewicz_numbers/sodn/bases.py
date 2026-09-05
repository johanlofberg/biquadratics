"""Exhaustive C4-free bases modulo row and column permutations."""
from collections import Counter
from itertools import combinations,permutations
from math import factorial

def row_sequences(m,n,total):
    choices=range(1<<n)
    degrees=[s.bit_count() for s in choices]
    pairbits={}
    pairs=list(combinations(range(n),2))
    for s in choices:
        pairbits[s]=sum(1<<k for k,(a,b) in enumerate(pairs)
                        if s>>a&1 and s>>b&1)
    def visit(prefix,minimum,left,used):
        count=m-len(prefix)
        if not count:
            if left==0:yield tuple(prefix)
            return
        if left<0 or left>count*n:return
        for s in range(minimum,1<<n):
            d=degrees[s]
            if d>left or pairbits[s]&used:continue
            yield from visit(prefix+[s],s,left-d,used|pairbits[s])
    yield from visit([],0,total,0)

def enumerate_bases(m,n,total):
    cps=list(permutations(range(n)))
    maps=[[sum(1<<cp[j] for j in range(n) if s>>j&1)
           for s in range(1<<n)] for cp in cps]
    reps=set(); labeled=0; sequences=0
    for rows in row_sequences(m,n,total):
        sequences+=1
        weight=factorial(m)
        for mult in Counter(rows).values():weight//=factorial(mult)
        labeled+=weight
        reps.add(min(tuple(sorted(mp[r] for r in rows)) for mp in maps))
    return {'m':m,'n':n,'total':total,'labeled_count':labeled,
            'sorted_row_sequences':sequences,'representatives':[list(r) for r in sorted(reps)]}

def cells_from_rows(rows,n):
    return tuple(i*n+j for i,r in enumerate(rows) for j in range(n) if r>>j&1)

def matchings(items,k):
    def perfect(seq):
        if not seq:
            yield ()
            return
        a=seq[0]
        for i in range(1,len(seq)):
            for tail in perfect(seq[1:i]+seq[i+1:]):
                yield ((a,seq[i]),)+tail
    for subset in combinations(items,2*k):
        yield from perfect(subset)

def automorphisms(rows,n):
    e1=set(cells_from_rows(rows,n)); m=len(rows); result=[]
    # Used only for the small survivor/classification tasks.
    for cp in permutations(range(n)):
        permrows=[sum(1<<cp[j] for j in range(n) if row>>j&1) for row in rows]
        candidates=[[i for i,r in enumerate(rows) if r==s] for s in permrows]
        def assign(prefix,used):
            if len(prefix)==m:
                yield tuple(prefix)
                return
            for r in candidates[len(prefix)]:
                if r not in used:yield from assign(prefix+[r],used|{r})
        for rp in assign([],set()):
            result.append(tuple(rp[i]*n+cp[j] for i in range(m) for j in range(n)))
    return result

def canonical_pairing(e2,maps):
    return min(tuple(sorted(tuple(sorted((mp[a],mp[b]))) for a,b in e2)) for mp in maps)


def fano_classification():
    """Equality in the pair bound forces seven triples; enumerate exact covers."""
    triples=list(combinations(range(7),3))
    pairs=list(combinations(range(7),2)); index={p:i for i,p in enumerate(pairs)}
    tm=[sum(1<<index[p] for p in combinations(t,2)) for t in triples]
    target=(1<<21)-1;solutions=[]
    def visit(used,chosen):
        if used==target:
            solutions.append(tuple(sorted(sum(1<<c for c in triples[t]) for t in chosen)))
            return
        first=next(i for i in range(21) if not used>>i&1)
        for t,bits in enumerate(tm):
            if bits>>first&1 and not bits&used:visit(used|bits,chosen+[t])
    visit(0,[])
    cps=list(permutations(range(7)))
    reps=set()
    for rows in solutions:
        reps.add(min(tuple(sorted(sum(1<<cp[j] for j in range(7) if r>>j&1)
                                 for r in rows)) for cp in cps))
    return {'m':7,'n':7,'total':21,'fixed_column_row_sets':len(solutions),
            'labeled_count':len(solutions)*factorial(7),
            'representatives':[list(r) for r in sorted(reps)],
            'upper_bound_proof':'sum binom(d,2)<=21 and binom(d,2)>=3*d-6 imply sum d<=21; equality forces d=3.'}
