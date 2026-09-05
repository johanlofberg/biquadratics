import unittest,random,json,subprocess,tempfile
from pathlib import Path
from itertools import combinations
from sodn.core import Geometry,validate
from sodn.reference import closure_check,p3_incidence_instance
from sodn.weak import weak_check
from sodn.benchmark import FixedWeak
from sodn.search import fano_base,exhaustive
from sodn.bases import enumerate_bases,cells_from_rows,matchings
from sodn.io import witness,unpack

class VerifierTests(unittest.TestCase):
    def test_independent_closures_on_random_simple_supports(self):
        rng=random.Random(20260905)
        for m,n in ((2,2),(3,3),(4,4),(5,4),(6,4),(5,5),(7,7)):
            geo=Geometry(m,n)
            for _ in range(120):
                cells=list(range(m*n));rng.shuffle(cells)
                s=rng.randrange(len(cells)+1);k=rng.randrange((len(cells)-s)//2+1)
                e1=cells[:s];e2=list(zip(cells[s:s+2*k:2],cells[s+1:s+2*k:2]))
                one=lambda c:(c//n+1,c%n+1)
                for plus in (False,True):
                    a=geo.check(e1,e2,plus,True)
                    b=closure_check(m,n,[one(c) for c in e1],[(one(x),one(y)) for x,y in e2],complementary_rule=plus)
                    self.assertEqual((a['accepted'],a['resolved']),(b['accepted'],b['resolved']))
    def test_complementary_pair_rule(self):
        geo=Geometry(2,2)
        self.assertFalse(geo.check([],[(0,3),(1,2)],False))
        self.assertTrue(geo.check([],[(0,3),(1,2)],True))
    def test_odd_cycles_are_not_ordinary_closure(self):
        e1,e2,_=p3_incidence_instance()
        flat=lambda c:(c[0]-1)*6+c[1]-1
        r=Geometry(15,6).check([flat(c) for c in e1],[(flat(a),flat(b)) for a,b in e2],True,True)
        self.assertTrue(r['resolved']);self.assertFalse(r['accepted'])
    def test_pruning_against_unpruned_enumeration(self):
        for m,n,z,ks in ((4,4,9,(1,2,3)),(5,4,10,(3,4,5)),(6,4,12,(6,))):
            bases=enumerate_bases(m,n,z);geo=Geometry(m,n)
            for k in ks:
                brute=0
                for rows in bases['representatives']:
                    e1=cells_from_rows(rows,n);free=tuple(c for c in range(m*n) if c not in e1)
                    brute+=sum(geo.check(e1,pairs) for pairs in matchings(free,k))
                self.assertEqual(exhaustive(m,n,z,k,save=False)['accepted_total'],brute)
    def test_weak_bit_checker_independently(self):
        e1=fano_base();free=[c for c in range(49) if c not in e1]
        edges=[e for e in combinations(free,2) if weak_check(7,7,e1,[e])]
        fast=FixedWeak(e1,7,edges);rng=random.Random(731)
        for _ in range(2500):
            ids=list(range(len(edges)));rng.shuffle(ids);selected=[];mask=0
            for q in ids:
                if mask&fast.masks[q]:continue
                selected.append(q);mask|=fast.masks[q]
                slow=weak_check(7,7,e1,[edges[j] for j in selected])
                self.assertEqual(fast.check(selected,mask),slow)
                if len(selected)>=8 or (not slow and rng.random()<0.8):break
        saved=json.loads(Path('witnesses/weak_7x7_total28.json').read_text())
        _,_,_,pairs=unpack(saved);idx={e:i for i,e in enumerate(edges)}
        for k in range(8):
            for subset in combinations(pairs,k):
                selected=[idx[tuple(sorted(e))] for e in subset]
                mask=sum(fast.masks[q] for q in selected)
                self.assertTrue(fast.check(selected,mask))
    def test_invalid_witnesses_are_rejected(self):
        with self.assertRaises(ValueError):validate(2,2,[0],[(0,1)])
        data=witness(2,2,[0],[],'RW3',{})
        data['e1']=[[0,2]]
        with self.assertRaises(ValueError):unpack(data)

if __name__=='__main__':unittest.main()
