"""Generate manuscript tables and benchmark supports from released results."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent.parent

def load(name):return json.loads((root/'results'/name).read_text(encoding='utf-8-sig'))
def table(criterion):
    results=[]
    for path in (root/'results').glob('exhaustive_'+criterion+'_*.json'):
        if path.stem.endswith('_reference'):continue
        r=json.loads(path.read_text())
        results.append((r['m'],r['n'],r['e1_total']+r['e2_total'],sum(c['candidates'] for c in r['counts']),r['accepted_total']))
    lines=[r'\begin{center}',r'\begin{tabular}{ccrr}',r'\toprule',
           r'Grid & Total & Candidates & Accepted\\',r'\midrule']
    for m,n,total,count,accepted in sorted(results):
        grid='$'+str(m)+r'\times'+str(n)+'$'
        lines.append(f'{grid} & {total} & {count} & {accepted}'+r'\\')
    lines += [r'\bottomrule',r'\end{tabular}',r'\end{center}']
    return '\n'.join(lines)
(root/'paper'/'computational_data.tex').write_text(
    'The exhaustive $(RW3^+)$ results are:\n'+table('RW3plus')+
    '\nThe exhaustive weak-admissibility results are:\n'+table('weak')+'\n',encoding='utf-8',newline='\n')
def edges_tex(pairs):
    return [f'({a[0]},{a[1]};{b[0]},{b[1]})' for a,b in pairs]
def display(name,items,width=3):
    rows=[',\\ '.join(items[i:i+width]) for i in range(0,len(items),width)]
    return '\\[\n'+name+r'=\left\{\begin{gathered}'+'\n'+',\\\\\n'.join(rows)+'\n'+r'\end{gathered}\right\}.'+'\n\\]\n'
weak=json.loads((root/'witnesses'/'weak_7x7_total28.json').read_text())
strong=json.loads((root/'witnesses'/'RW3_7x7_total31.json').read_text())
strong32=json.loads((root/'witnesses'/'RW3_7x7_total32.json').read_text(encoding='utf-8'))
extra=load('benchmark77_extensions.json')
extras=[[divmod(e['edge'][0],7),divmod(e['edge'][1],7)] for e in extra['decisions'] if e['accepted']]
text='A weak-optimal augmentation is\n'+display(r'E_2^{\mathrm{wk}}',edges_tex(weak['e2']))
text+='Its seven accepted extra two-edges are\n'+display(r'\mathcal E_{\mathrm{extra}}',edges_tex(extras))
text+='A total-31 recursive witness on the same base uses\n'+display(r'E_2^{31}',edges_tex(strong['e2']))
text+='An improved total-32 recursive witness on the same base uses\n'+display(r'E_2^{32}',edges_tex(strong32['e2']))
(root/'paper'/'benchmark_data.tex').write_text(text,encoding='utf-8',newline='\n')
print('Regenerated manuscript tables and explicit 7x7 supports.')
