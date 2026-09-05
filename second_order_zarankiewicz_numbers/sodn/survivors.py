"""Export every canonical Gram-kernel survivor, with exact distributions."""
from collections import Counter
from .bases import enumerate_bases,cells_from_rows,matchings,automorphisms,canonical_pairing
from .gram import kernel_dimension
from .io import ROOT,write_json

def enumerate_survivors(save=True):
    bases=enumerate_bases(5,4,10);records=[];all_survivors={13:[],14:[],15:[]}
    for bidx,rows in enumerate(bases['representatives']):
        e1=cells_from_rows(rows,4);free=tuple(c for c in range(20) if c not in e1)
        maps=automorphisms(rows,4)
        for total in (15,14,13):
            histogram=Counter();orbits=set()
            for pairs in matchings(free,total-10):
                polynomials=[(divmod(c,4),) for c in e1]+[
                             (divmod(a,4),divmod(b,4)) for a,b in pairs]
                d=kernel_dimension(polynomials);histogram[d]+=1
                if d==0:orbits.add(canonical_pairing(pairs,maps))
            rec={'base':bidx,'row_masks':rows,'total':total,
                 'automorphisms':len(maps),'kernel_dimensions':dict(sorted(histogram.items())),
                 'zero_kernel_candidates':histogram[0],'zero_kernel_classes':len(orbits)}
            records.append(rec)
            for pairs in sorted(orbits):
                all_survivors[total].append({'base':bidx,'e2':[list(e) for e in pairs]})
            print('Gram survivors',total,'base',bidx,'classes',len(orbits),flush=True)
    result={'m':5,'n':4,'cell_encoding':'zero-based row*4+column',
            'bases':bases['representatives'],'records':records,
            'classes':all_survivors,
            'interpretation':'Zero displayed-basis kernel does not certify irreducibility without universal resolution.'}
    if save:write_json(ROOT/'results'/'gram_survivors.json',result)
    return result
