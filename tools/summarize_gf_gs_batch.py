#!/usr/bin/env python3
"""Summarize the 700-case GF/Guosen batch, including file artifacts and quota states."""
from __future__ import annotations

import csv, json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'04_测试结果'/'广发国信联合benchmark'
ART=BASE/'artifacts'

def collect(case_id):
    out=[]; d=ART/case_id
    if not d.exists(): return out
    for p in sorted(d.rglob('*')):
        if p.is_file():
            item={'path':str(p).replace('\\','/'),'bytes':p.stat().st_size}
            if p.suffix.lower() in {'.txt','.json','.csv','.md'}:
                item['text']=p.read_text(encoding='utf-8',errors='replace')[:200000]
            out.append(item)
    return out

def main():
    rows=[json.loads(x) for x in (BASE/'results.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    for r in rows:
        arts=collect(r['case_id']); r['artifacts']=arts
        text='\n'.join((x.get('stdout') or '')+'\n'+(x.get('stderr') or '') for x in r.get('results',[]))
        for a in arts: text+='\n'+a.get('text','')
        count=r.get('result_count',0)
        m=re.search(r'ETF数量:\s*(\d+)',text); m2=re.search(r'对比基金数量:\s*(\d+)',text); m3=len(re.findall(r'结果 #',text))
        if m: count=max(count,int(m.group(1)))
        if m2: count=max(count,int(m2.group(1)))
        if m3: count=max(count,m3)
        r['result_count_final']=count
        original=r.get('status','')
        if '超过日限额' in text:
            final='quota_limited'
        elif arts and all(x.get('returncode')==0 for x in r.get('results',[])):
            final='success'
        elif original in {'success','empty','error'}:
            final=original
        else:
            final='error'
        r['status_final']=final
    (BASE/'results.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n',encoding='utf-8')
    summary=[]
    for r in rows:
        summary.append({'case_id':r['case_id'],'institution':r['institution'],'skill':r['skill'],'question':r['question'],'status_original':r.get('status',''),'status_final':r['status_final'],'result_count':r.get('result_count',0),'result_count_final':r['result_count_final'],'artifact_count':len(r.get('artifacts',[])),'command_returncode':r.get('returncode',0)})
    with (BASE/'summary.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0].keys())); w.writeheader(); w.writerows(summary)
    agg=[]
    for inst,skill in sorted(set((r['institution'],r['skill']) for r in rows)):
        g=[r for r in rows if r['institution']==inst and r['skill']==skill]; c=Counter(r['status_final'] for r in g)
        agg.append({'institution':inst,'skill':skill,'cases':len(g),'success':c.get('success',0),'empty':c.get('empty',0),'error':c.get('error',0),'quota_limited':c.get('quota_limited',0),'cases_with_artifacts':sum(1 for r in g if r['artifacts']),'cases_with_results':sum(1 for r in g if r['result_count_final']>0)})
    with (BASE/'skill_summary.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(agg[0].keys())); w.writeheader(); w.writerows(agg)
    (BASE/'skill_summary.json').write_text(json.dumps({'total_cases':len(rows),'overall_status':dict(Counter(r['status_final'] for r in rows)),'skills':agg},ensure_ascii=False,indent=2),encoding='utf-8')
    print('updated',len(rows))
    for x in agg: print(x['institution'],x['skill'],x)

if __name__=='__main__': main()