"""Deterministic exhaustive searches and seeded witness discovery."""
from itertools import combinations
from math import factorial
from collections import Counter
import random
from .bases import enumerate_bases,cells_from_rows,matchings
from .core import Geometry
from .weak import weak_check
from .io import ROOT,write_json,witness,verify

def matching_count(n,k):
    return 0 if k<0 or 2*k>n else factorial(n)//factorial(n-2*k)//(2**k*factorial(k))

def exhaustive(m,n,z,k,criterion='RW3+',save=True,engine='fast'):
    bases=enumerate_bases(m,n,z); geo=Geometry(m,n)
    reports=[]; allwitnesses=[]
    for bidx,rows in enumerate(bases['representatives']):
        e1=cells_from_rows(rows,n);free=tuple(c for c in range(m*n) if c not in e1)
        accepted=[]; rejected_prefixes=[]; stats=Counter()
        def predicate(pairs):
            if criterion=='weak':return weak_check(m,n,e1,pairs)
            if engine=='reference':
                from .reference import closure_check
                one=lambda c:(c//n+1,c%n+1)
                return closure_check(m,n,[one(c) for c in e1],
                       [(one(a),one(b)) for a,b in pairs],
                       complementary_rule=criterion!='RW3')['accepted']
            return geo.check(e1,pairs,criterion!='RW3')
        def visit(items,need,prefix):
            if need==0:
                stats['accepted']+=1
                accepted.append(prefix)
                return
            if len(items)<2*need:return
            a=items[0]
            if len(items)>2*need:visit(items[1:],need,prefix)
            for j in range(1,len(items)):
                tail=items[1:j]+items[j+1:]
                trial=prefix+((a,items[j]),)
                stats['predicate_calls']+=1
                if predicate(trial):
                    visit(tail,need-1,trial)
                else:
                    stats['pruned_branches']+=1
                    stats['rejected']+=matching_count(len(tail),need-1)
                    rejected_prefixes.append([list(e) for e in trial])
        visit(free,k,())
        total=matching_count(len(free),k)
        if stats['accepted']+stats['rejected']!=total:
            raise AssertionError('Exhaustive coverage accounting failure')
        reports.append({'base':bidx,'row_masks':rows,'candidates':total,'rejected_prefixes':rejected_prefixes,**dict(stats)})
        for pairs in accepted:
            allwitnesses.append({'base':bidx,'e2':[list(e) for e in pairs]})
        if accepted and save:
            data=witness(m,n,e1,accepted[0],criterion,
                         {'algorithm':'exhaustive','base':bidx,'k':k})
            verify(data)
            write_json(ROOT/'witnesses'/f'{criterion.replace("+","plus")}_{m}x{n}_total{z+k}_base{bidx}.json',data)
        print(f'{m}x{n} {criterion} total={z+k} base={bidx}: {dict(stats)}',flush=True)
    report={'m':m,'n':n,'e1_total':z,'e2_total':k,'criterion':criterion,'engine':engine,
            'method':'exhaustive matching tree with hereditary rejection pruning',
            'bases':bases,'counts':reports,
            'accepted_total':sum(r.get('accepted',0) for r in reports),
            'accepted_augmentations':allwitnesses}
    if save:write_json(ROOT/'results'/f'exhaustive_{criterion.replace("+","plus")}_{m}x{n}_total{z+k}{"_reference" if engine=="reference" else ""}.json',report)
    return report

def greedy(m,n,z,target,criterion='RW3+',seed=20260905,restarts=10000):
    if (m,n,z)==(7,7,21):
        e1=fano_base()
        rows=[sum(1<<(c%7) for c in e1 if c//7==r) for r in range(7)]
        bases={'representatives':[rows]}
    else:bases=enumerate_bases(m,n,z)
    geo=Geometry(m,n);rng=random.Random(seed)
    best=0
    for attempt in range(restarts):
        bidx=attempt%len(bases['representatives'])
        e1=cells_from_rows(bases['representatives'][bidx],n)
        pairs=[];free=[c for c in range(m*n) if c not in e1]
        while True:
            candidates=list(combinations(free,2));rng.shuffle(candidates)
            picked=None
            for edge in candidates:
                trial=pairs+[edge]
                if criterion=='weak':ok=weak_check(m,n,e1,trial)
                elif criterion=='benchmark':
                    ok=weak_check(m,n,e1,trial,w3=False) and geo.check(e1,trial,False)
                else:ok=geo.check(e1,trial,criterion!='RW3')
                if ok:picked=edge;break
            if picked is None:break
            pairs.append(picked);free=[c for c in free if c not in picked]
            if len(pairs)>best:
                best=len(pairs)
                print(f'{m}x{n} {criterion}: best total {z+best}, restart {attempt}',flush=True)
            if z+len(pairs)>=target:
                label='RW3' if criterion=='benchmark' else criterion
                data=witness(m,n,e1,pairs,label,
                             {'algorithm':'seeded_greedy','seed':seed,'restart':attempt,
                              'filter':criterion,'base':bidx})
                verify(data)
                write_json(ROOT/'witnesses'/f'{label.replace("+","plus")}_{m}x{n}_total{target}.json',data)
                return data
    return {'found':False,'best_total':z+best,'restarts':restarts,'seed':seed}

def fano_base():
    return tuple(sorted(r*7+(r+d)%7 for r in range(7) for d in (0,1,3)))

def benchmark77(seed=20260905,restarts=20000):
    m=n=7;e1=fano_base();geo=Geometry(7,7);rng=random.Random(seed)
    weakrecord=None; totalrecord=None;best=0
    for attempt in range(restarts):
        pairs=[];free=[c for c in range(49) if c not in e1]
        weakmode=(attempt%2==0 and weakrecord is None)
        while True:
            candidates=list(combinations(free,2));rng.shuffle(candidates)
            pick=None
            for edge in candidates:
                trial=pairs+[edge]
                if weakmode:
                    ok=weak_check(7,7,e1,trial)
                else:
                    ok=weak_check(7,7,e1,trial,w3=False) and geo.check(e1,trial,False)
                if ok:pick=edge;break
            if pick is None:break
            pairs.append(pick);free=[c for c in free if c not in pick]
            if len(pairs)>best:
                best=len(pairs);print('7x7 best total',21+best,'restart',attempt,flush=True)
            if weakmode and len(pairs)==7:
                all_extra=list(combinations(free,2));accepted=[];decisions=[]
                for extra in all_extra:
                    f=weak_check(7,7,e1,pairs+[extra],explain=True,w3=False)
                    rw=geo.check(e1,pairs+[extra],False)
                    ok=f['accepted'] and rw
                    decisions.append({'edge':list(extra),'filter':f,'rw3':rw,'accepted':ok})
                    if ok:accepted.append(extra)
                print('7x7 weak total 28; extension count',len(accepted),'restart',attempt,flush=True)
                if len(accepted)==7 or weakrecord is None:
                    data=witness(7,7,e1,pairs,'weak',
                                 {'algorithm':'seeded_greedy','seed':seed,'restart':attempt})
                    verify(data)
                    write_json(ROOT/'witnesses'/'weak_7x7_total28.json',data)
                    report={'starting_witness':'weak_7x7_total28.json','candidates':len(all_extra),
                            'accepted_count':len(accepted),'decisions':decisions}
                    write_json(ROOT/'results'/'benchmark77_extensions.json',report)
                    weakrecord=report
                break
            if not weakmode and len(pairs)>=10:
                data=witness(7,7,e1,pairs,'RW3',
                             {'algorithm':'seeded_greedy','seed':seed,'restart':attempt,
                              'filter':"S,W2,W2prime,RW3"})
                verify(data);write_json(ROOT/'witnesses'/'RW3_7x7_total31.json',data)
                totalrecord=data
                break
        if weakrecord and totalrecord:
            return {'weak_extensions':weakrecord['accepted_count'],'total31':True}
    return {'weak_extensions':None if weakrecord is None else weakrecord['accepted_count'],
            'total31':totalrecord is not None,'best_total':21+best}
