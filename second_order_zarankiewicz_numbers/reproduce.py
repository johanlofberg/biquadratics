"""One entry point; generated outputs never overwrite release baselines by default."""
import argparse,json,os
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'runs'/'latest',
                   help='Generated output root (default: runs/latest)')
    sub=p.add_subparsers(dest='command',required=True)
    for name in ('enumerate','discover'):
        q=sub.add_parser(name)
        q.add_argument('m',type=int);q.add_argument('n',type=int);q.add_argument('z',type=int)
        q.add_argument('total',type=int)
        q.add_argument('--criterion',choices=['RW3','RW3+','weak','benchmark'],default='RW3+')
        if name=='enumerate':q.add_argument('--engine',choices=['fast','reference'],default='fast')
        if name=='discover':
            q.add_argument('--seed',type=int,default=20260905)
            q.add_argument('--restarts',type=int,default=10000)
    sub.add_parser('benchmark77')
    sub.add_parser('verify');sub.add_parser('survivors');sub.add_parser('research')
    q=sub.add_parser('all');q.add_argument('--reference',action='store_true');q.add_argument('--research',action='store_true')
    a=p.parse_args()
    os.environ['SODN_OUTPUT_DIR']=str(a.output.resolve())
    from sodn.search import exhaustive,greedy
    from sodn import tasks
    if a.command=='enumerate':
        if a.criterion=='benchmark':p.error('Use benchmark77 for the benchmark filter')
        result=exhaustive(a.m,a.n,a.z,a.total-a.z,a.criterion,engine=a.engine)
        print('Accepted:',result['accepted_total'])
    elif a.command=='discover':
        result=greedy(a.m,a.n,a.z,a.total,a.criterion,a.seed,a.restarts)
        if result.get('found') is False:raise SystemExit('No witness found within the restart limit')
        print('Verified total:',result['total'])
    elif a.command=='benchmark77':print(json.dumps(tasks.run_benchmark(),indent=2))
    elif a.command=='verify':print(json.dumps(tasks.verify_release(),indent=2))
    elif a.command=='survivors':
        from sodn.survivors import enumerate_survivors
        r=enumerate_survivors()
        print({k:len(v) for k,v in r['classes'].items()})
    elif a.command=='research':print(json.dumps(tasks.research(),indent=2))
    elif a.command=='all':print(json.dumps(tasks.all_checks(a.reference,a.research),indent=2))
if __name__=='__main__':main()
