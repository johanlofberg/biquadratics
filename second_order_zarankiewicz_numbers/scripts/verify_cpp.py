"""Compile and independently verify the complete weak 7x7 search."""
import json,random,subprocess,sys
from pathlib import Path
from itertools import combinations
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root))
from sodn.search import fano_base
from sodn.weak import weak_check
from sodn.benchmark import weak77_upper
from sodn.io import unpack,write_json
work=root/'runs'/'cpp';work.mkdir(parents=True,exist_ok=True)
exe=work/('weak77.exe' if sys.platform=='win32' else 'weak77')
subprocess.run(['g++','-std=c++17','-O3',str(root/'scripts'/'weak77.cpp'),'-o',str(exe)],check=True)
cpp=json.loads(subprocess.check_output([str(exe)],text=True))
python=weak77_upper(save=False)
for key,value in cpp.items():
    if python[key]!=value:raise AssertionError('Complete C++ enumeration differs: '+key)
rng=random.Random(182);e1=fano_base();free=[c for c in range(49) if c not in e1]
cases=[]
for _ in range(5000):
    shuffled=free[:];rng.shuffle(shuffled);k=rng.randrange(1,10)
    cases.append(list(zip(shuffled[:2*k:2],shuffled[1:2*k:2])))
for name in ('weak_7x7_total28.json','RW3_7x7_total31.json'):
    _,_,_,pairs=unpack(json.loads((root/'witnesses'/name).read_text()))
    for k in range(1,len(pairs)+1):
        cases.extend(combinations(pairs,k))
path=work/'predicate_cases.txt'
path.write_text('\n'.join(str(len(case))+' '+' '.join(f'{a} {b}' for a,b in case) for case in cases)+'\n')
answers=[int(x) for x in subprocess.check_output([str(exe),'--check',str(path)],text=True).split()]
expected=[int(weak_check(7,7,e1,case)) for case in cases]
if answers!=expected:raise AssertionError('C++ and Python weak predicates differ')
report={'predicate_cases':len(cases),'accepted_cases':sum(expected),'all_agree':True,
        'complete_enumeration_counts_agree':True,
        'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0]}
write_json(work/'verification.json',report)
write_json(work/'complete_enumeration.json',cpp)
print(json.dumps(report,indent=2))
