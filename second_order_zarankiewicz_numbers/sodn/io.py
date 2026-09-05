"""Deterministic public witness and result format."""
import json
import os
from pathlib import Path
from .core import validate,c4_free,Geometry
from .reference import closure_check
from .weak import weak_check
PROJECT_ROOT=Path(__file__).resolve().parent.parent
ROOT=Path(os.environ.get('SODN_OUTPUT_DIR', str(PROJECT_ROOT)))

def write_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')

def witness(m,n,e1,e2,criterion,provenance):
    validate(m,n,e1,e2)
    return {'schema':1,'m':m,'n':n,'coordinate_system':'zero-based [row,column]',
            'e1':[list(divmod(c,n)) for c in sorted(e1)],
            'e2':[[list(divmod(a,n)),list(divmod(b,n))]
                  for a,b in sorted(tuple(sorted(e)) for e in e2)],
            'total':len(e1)+len(e2),'criterion':criterion,'provenance':provenance}

def unpack(data):
    m,n=data['m'],data['n']
    if type(m) is not int or type(n) is not int or m<1 or n<1:raise ValueError('Invalid grid')
    if data.get('coordinate_system')!='zero-based [row,column]':raise ValueError('Unknown coordinate convention')
    if data.get('criterion') not in ('RW3','RW3+','weak','SD'):raise ValueError('Unknown criterion')
    for cell in list(data['e1'])+[c for edge in data['e2'] for c in edge]:
        if len(cell)!=2 or any(type(x) is not int for x in cell):raise ValueError('Invalid cell')
        r,c=cell
        if not (0<=r<m and 0<=c<n):raise ValueError('Cell outside grid')
    if any(len(e)!=2 for e in data['e2']):raise ValueError('Invalid two-edge')
    e1=tuple(r*n+c for r,c in data['e1'])
    e2=tuple(tuple(r*n+c for r,c in e) for e in data['e2'])
    validate(m,n,e1,e2)
    if not c4_free(n,e1):raise ValueError('E1 is not C4-free')
    if data['total']!=len(e1)+len(e2):raise ValueError('Wrong total')
    return m,n,e1,e2

def verify(data):
    m,n,e1,e2=unpack(data)
    criterion=data['criterion']; plus=criterion!='RW3'
    fast=Geometry(m,n).check(e1,e2,plus=plus,details=True)
    one=lambda c:(c//n+1,c%n+1)
    slow=closure_check(m,n,[one(c) for c in e1],
                       [(one(a),one(b)) for a,b in e2],complementary_rule=plus)
    if fast['accepted']!=slow['accepted']:raise AssertionError('Independent closures disagree')
    if criterion=='weak':
        ok=weak_check(m,n,e1,e2)
        if ok and not fast['accepted']:raise AssertionError('Weak inclusion in RW3+ failed')
    elif criterion=='SD':
        from .signed import signed_deviation
        ok=signed_deviation(m,n,[one(c) for c in e1],[(one(a),one(b)) for a,b in e2])['accepted']
    else:ok=fast['accepted']
    if not ok:raise AssertionError('Witness does not satisfy '+criterion)
    return {'total':data['total'],'criterion':criterion,'verified':True,
            'fast':fast,'reference':slow}
