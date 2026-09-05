"""Release reproduction tasks and expected mathematical results."""
import json,hashlib,platform,time
from pathlib import Path
from .io import ROOT,PROJECT_ROOT,write_json,verify,witness
from .bases import enumerate_bases,fano_classification
from .search import exhaustive,greedy,fano_base
from .benchmark import weak77_upper,extensions
from .survivors import enumerate_survivors
from .fixtures import export_fixtures

SPECS=[
 (4,4,9,12,'RW3+',0),(4,4,9,11,'RW3+',0),(4,4,9,10,'RW3+',6),
 (5,4,10,15,'RW3+',0),(5,4,10,14,'RW3+',0),(5,4,10,13,'RW3+',124),
 (6,4,12,18,'RW3+',0),(6,4,12,17,'RW3+',0),(6,4,12,16,'RW3+',6),
 (5,5,12,18,'RW3+',0),(5,5,12,17,'RW3+',4),
 (7,4,13,20,'RW3+',0),(7,4,13,19,'RW3+',18),
 (4,4,9,11,'weak',0),(4,4,9,10,'weak',6),
 (5,4,10,13,'weak',0),(5,4,10,12,'weak',120),
 (6,4,12,15,'weak',0),(6,4,12,14,'weak',108),
 (5,5,12,17,'weak',0),(5,5,12,16,'weak',3),
 (7,4,13,18,'weak',0),(7,4,13,17,'weak',33)]
def base_proofs():
    report={}
    for m,n,z in [(4,4,9),(5,4,10),(6,4,12),(5,5,12),(7,4,13)]:
        at=enumerate_bases(m,n,z);above=enumerate_bases(m,n,z+1)
        if not at['representatives'] or above['representatives']:
            raise AssertionError('Classical base extremality check failed')
        report[f'{m}x{n}']={'at_extremum':at,'one_above':above}
    report['7x7']=fano_classification()
    if len(report['7x7']['representatives'])!=1 or report['7x7']['fixed_column_row_sets']!=30:
        raise AssertionError('Fano classification failed')
    write_json(ROOT/'results'/'base_extremality.json',report)
    return report

def run_enumerations(reference=False):
    results={}
    for m,n,z,total,criterion,expected in SPECS:
        engine='reference' if reference and criterion!='weak' else 'fast'
        r=exhaustive(m,n,z,total-z,criterion,engine=engine)
        if reference and criterion!='weak':
            baseline=PROJECT_ROOT/'results'/f'exhaustive_RW3plus_{m}x{n}_total{total}.json'
            if baseline.exists():
                b=json.loads(baseline.read_text())
                if r['counts']!=b['counts'] or r['accepted_augmentations']!=b['accepted_augmentations']:
                    raise AssertionError('Reference and fast search records disagree')
        if r['accepted_total']!=expected:
            raise AssertionError((m,n,total,criterion,r['accepted_total'],expected))
        results[f'{m}x{n}:{criterion}:{total}']=r['accepted_total']
    return results

def run_benchmark():
    upper=weak77_upper()
    expected=[0,1,98,2305,12715,10920,681,2,0]
    if upper['fixed_pair_accepted_prefix_counts']!=expected:raise AssertionError('7x7 prefix counts changed')
    data=witness(7,7,fano_base(),upper['first_seven'],'weak',
                 {'algorithm':'complete_fixed_pair_weak_enumeration'})
    verify(data);write_json(ROOT/'witnesses'/'weak_7x7_total28.json',data)
    ext=extensions(data)
    if (ext['candidates'],ext['accepted_count'])!=(91,7):raise AssertionError('7x7 extensions changed')
    lower=greedy(7,7,21,31,'benchmark',restarts=1000)
    if lower.get('total')!=31:raise AssertionError('7x7 total-31 discovery failed')
    return {'weak_upper':28,'extensions':7,'recursive_lower':31}

def verify_release():
    results={}
    paths=sorted((PROJECT_ROOT/'witnesses').glob('*.json'))
    if not paths:raise AssertionError('No release witnesses')
    for path in paths:
        results[path.name]=verify(json.loads(path.read_text(encoding='utf-8')))
    # Recompute all 91 decisions for the saved benchmark.
    data=json.loads((PROJECT_ROOT/'witnesses'/'weak_7x7_total28.json').read_text(encoding='utf-8'))
    current=extensions(data,save=False)
    recorded=json.loads((PROJECT_ROOT/'results'/'benchmark77_extensions.json').read_text(encoding='utf-8'))
    if current!=recorded:raise AssertionError('Benchmark decision record changed')
    write_json(ROOT/'results'/'release_verification.json',results)
    return {'verified_witness_files':len(results),'benchmark_candidates':91}

def research():
    from .signed import signed_deviation
    from .bases import cells_from_rows,matchings
    output={}
    for k in (5,4,3):
        agg={'total':0,'accepted':0,'allresolved_free':0,'unresolved':0}
        for rows in enumerate_bases(5,4,10)['representatives']:
            e1=cells_from_rows(rows,4);free=tuple(c for c in range(20) if c not in e1)
            one=lambda c:(c//4+1,c%4+1)
            for pairs in matchings(free,k):
                r=signed_deviation(5,4,[one(c) for c in e1],[(one(a),one(b)) for a,b in pairs])
                agg['total']+=1
                key='accepted' if r['accepted'] else 'allresolved_free' if r['all_e2_resolved'] else 'unresolved'
                agg[key]+=1
        expected = {
            13: {'total':9450,'accepted':124,'allresolved_free':1701,'unresolved':7625},
            14: {'total':14175,'accepted':0,'allresolved_free':676,'unresolved':13499},
            15: {'total':2835,'accepted':0,'allresolved_free':9,'unresolved':2826},
        }
        if agg != expected[10+k]:
            raise AssertionError(('Signed scan changed',10+k,agg))
        output[str(10+k)]=agg
    write_json(ROOT/'results'/'signed_scan.json',output)
    return output

def all_checks(reference=False,include_research=False):
    started=time.monotonic()
    print('Checking classical base extrema and classification',flush=True);base_proofs()
    print('Checking explicit and generated witnesses',flush=True);export_fixtures()
    print('Running exhaustive finite searches',flush=True);run_enumerations(reference)
    print('Reproducing complete 7x7 benchmark',flush=True);run_benchmark()
    print('Exporting every Gram-kernel survivor',flush=True);survivors=enumerate_survivors()
    if [len(survivors['classes'][k]) for k in (13,14,15)]!=[1139,1052,119]:
        raise AssertionError('Survivor counts changed')
    print('Checking appendix formulas and rational ranks',flush=True)
    from .appendix import main as appendix
    a=appendix()
    from .reference import check_p3_words,p3_transfer_graph
    a['exceptional_p3_words']=check_p3_words()
    a['exceptional_p3_transfer_graph']=p3_transfer_graph()
    write_json(ROOT/'results'/'appendix_verification.json',a)
    if sum(a['appendix_words_checked_by_prime'].values())!=2767800:raise AssertionError('Appendix count changed')
    if include_research:research()
    paper=PROJECT_ROOT/'paper'/'SODN_reproducible.tex'
    metadata={'python':platform.python_version(),'all_required_computations_passed':True,
              'reference_enumerations':reference,'research_scan':include_research,
              'paper_sha256':hashlib.sha256(paper.read_bytes()).hexdigest() if paper.exists() else None,
              'elapsed_seconds':round(time.monotonic()-started,3)}
    write_json(ROOT/'results'/'run_metadata.json',metadata)
    return metadata
