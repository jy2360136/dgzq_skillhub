#!/usr/bin/env python3
"""Batch-test all available GF and Guosen Skills without calling MX MCP."""
from __future__ import annotations

import argparse, csv, hashlib, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
GF=ROOT/'01_竞品Skills'/'广发证券'/'extracted'
GS=ROOT/'01_竞品Skills'/'国信证券'/'extracted'
OUT=ROOT/'04_测试结果'/'广发国信联合benchmark'
CASES=500
GS_API_KEY_PLACEHOLDER='<GS_API_KEY>'

STOCKS=[('600519','SH'),('000001','SZ'),('300750','SZ'),('600036','SH'),('601318','SH'),('000333','SZ'),('000858','SZ'),('002594','SZ'),('600900','SH'),('601166','SH'),('600030','SH'),('000776','SZ'),('300059','SZ'),('601899','SH'),('688981','SH'),('600276','SH'),('600309','SH'),('601398','SH'),('601288','SH'),('601988','SH'),('601857','SH'),('600028','SH'),('600887','SH'),('600104','SH'),('600050','SH'),('601668','SH'),('601888','SH'),('603259','SH'),('688036','SH'),('688111','SH'),('688012','SH'),('600690','SH'),('600809','SH'),('601012','SH'),('600585','SH'),('601088','SH'),('600438','SH'),('002415','SZ'),('000568','SZ'),('002714','SZ'),('300760','SZ'),('300124','SZ'),('002475','SZ'),('002352','SZ'),('000651','SZ'),('000725','SZ'),('000063','SZ'),('000338','SZ'),('002142','SZ'),('300274','SZ')]
DATES=['20261113','20261112','20261111','20261110','20261109','20261106','20261105','20261104','20261103','20261102','20261030','20261029','20261028','20261027','20261026','20261023','20261022','20261021','20261020','20261019','20261016','20261015','20261014','20261013','20261012']
FUND_CODES=['000001','001643','010068','519002','161039','018956','110022','005827','003745','000011','000248','001938','003095','004746','006327','007300','008087','012414','013308','014193','015599','016670','017090','018147','019073','020602','021457','022364','023031','024070','025083','026098','027409','029383','100038','110011','161725','163406','166009','180012','202001','213006','260108','270002','320007','400015','519674','519066','000478','002190']

def case(cid, inst, skill, question, commands, output_dir=None):
    return {'case_id':cid,'institution':inst,'skill':skill,'question':question,'commands':commands,'output_dir':str(output_dir) if output_dir else None}

def gf_etf_rank():
    out=[]; types=[1,2,3,4,12,13]; sizes=[5,10,20,50,80]; i=1
    for typ in types:
        for size in sizes:
            extra=['--same-index-filter','1'] if (typ+i)%3==0 else []
            if typ in (1,2) and i%4==0: extra += ['--continue-rise-limit','3']
            q=f'查询广发ETF榜单类型{typ}前{size}只，返回代码、名称、涨跌幅、近5日涨幅、换手率、成交额和规模。'
            out.append(case(f'GF-ETFRANK-{i:03d}','广发证券','ETF榜单',q,[['python',str(GF/'gf-etf-rank'/'scripts'/'cli.py'),'--type',str(typ),'--size',str(size),'--page',str(i%3)]+extra])); i+=1
    for j in range(20):
        typ=types[j%len(types)]; q=f'分页查询ETF榜单类型{typ}，第{j%3+1}页，每页{10 if j%2 else 20}只，并排除重复跟踪指数。'
        out.append(case(f'GF-ETFRANK-{i:03d}','广发证券','ETF榜单',q,[['python',str(GF/'gf-etf-rank'/'scripts'/'cli.py'),'--type',str(typ),'--size',str(10 if j%2 else 20),'--page',str(j%3),'--same-index-filter','1']])); i+=1
    return out[:50]

def gf_etf_search():
    specs=[
      ['--trak-type','行业','--roc1m','5~','--sort','-roc1m'],['--trak-type','行业','--roc1y','10~','--sort','-roc1y'],
      ['--trak-type','行业','--return1y','5~','--sort','-return1y'],['--trak-type','行业','--return3y','10~'],
      ['--trak-type','行业','--max-drawdown1y','~20'],['--trak-type','行业','--sharp-ratio1y','1~','--sort','-sharpRatio1y'],
      ['--trak-type','行业','--valuation-result','1'],['--trak-type','行业','--valuation-result','2'],['--trak-type','行业','--valuation-result','3'],
      ['--trak-type','行业','--index-temp-type','low'],['--trak-type','行业','--index-temp-type','ord'],['--trak-type','行业','--index-temp-type','high'],
      ['--trak-type','行业','--asset-scale','50~','--sort','-assetScale'],['--trak-type','行业','--trade-t0','1'],['--trak-type','行业','--margin-trade','1'],
      ['--trak-type','行业','--roc1m','5~','--asset-scale','10~','--sort','-roc1m'],['--trak-type','行业','--trade-t0','1','--roc1m','3~'],
      ['--trak-type','行业','--margin-trade','1','--asset-scale','20~'],['--trak-type','行业','--max-drawdown1y','~15','--return1y','0~'],
      ['--trak-type','行业','--sharp-ratio1y','0.5~','--max-drawdown1y','~25']]
    out=[]; i=1
    for j in range(50):
        spec=specs[j%len(specs)][:]; limit=5 if j%3==0 else (10 if j%3==1 else 20); spec += ['--limit',str(limit)]
        q=f'筛选ETF，条件为{"，".join(spec)}，返回代码、名称、跟踪指数、近1月涨幅、近1年涨幅、最大回撤、夏普、规模和估值分位。'
        out.append(case(f'GF-ETFSEARCH-{i:03d}','广发证券','ETF筛选',q,[['python',str(GF/'gf-etf-search'/'scripts'/'cli.py')]+spec])); i+=1
    return out

def gf_super_fund():
    types=['大幅流入','大幅流出','持续流入','持续流出']; out=[]
    for i in range(50):
        typ=types[i%4]; q=f'查询ETF{typ}异动，返回代码、名称、净流入金额、资金强度和近14日资金明细。'
        out.append(case(f'GF-SUPERFUND-{i+1:03d}','广发证券','ETF资金异动',q,[['python',str(GF/'gf-etf-super-fund'/'scripts'/'cli.py'),'--type',typ]]))
    return out

def gf_fund_detail():
    out=[]
    for i in range(50):
        code=FUND_CODES[i%len(FUND_CODES)]; q=f'查询基金{code}的单位净值、累计净值、风险等级、基金规模、基金管理人、申购赎回状态和阶段收益。'
        out.append(case(f'GF-FUNDDETAIL-{i+1:03d}','广发证券','基金详情',q,[['python',str(GF/'gf-fund-detail'/'scripts'/'cli.py'),'--code',code]]))
    return out

def gf_fund_invest():
    out=[]
    for i in range(50):
        code=FUND_CODES[i%10]; strat=i%6; rate=i%4; balance=[500,1000,2000][i%3]; start=['20200101','20220101','20240101'][i%3]; end='20261112'
        q=f'基金{code}从{start}到{end}，每期定投{balance}元，扣款频率{rate}，策略{strat}，计算累计投入、累计收益、定投收益率和最高收益率。'
        out.append(case(f'GF-FUNDINVEST-{i+1:03d}','广发证券','基金定投',q,[['python',str(GF/'gf-fund-invest'/'scripts'/'cli.py'),'--code',code,'--balance',str(balance),'--start',start,'--end',end,'--rate',str(rate),'--strategy',str(strat),'--expect-income-ratio','0.2','--back-rate','0.1']]))
    return out

def gf_lhb():
    out=[]; i=1
    for d in DATES:
        for market in ['sh','sz']:
            q=f'查询{d} {market.upper()}市场龙虎榜全部股票，返回代码、名称、涨跌幅、收盘价、成交额和上榜原因。'
            out.append(case(f'GF-LHB-{i:03d}','广发证券','龙虎榜',q,[['python',str(GF/'gf-lhb-list'/'scripts'/'cli.py'),'--date',d,'--market',market]])); i+=1
    return out

def gf_f10():
    out=[]
    for i,(code,mkt) in enumerate(STOCKS,1):
        q=f'查询{code}.{mkt}公司全称、上市日期、所属行业、主营范围、管理层和公司概况。'
        out.append(case(f'GF-F10-{i:03d}','广发证券','股票F10',q,[['python',str(GF/'gf-stock-f10'/'scripts'/'cli.py'),'--code',code,'--market',mkt]]))
    return out

def gf_valuation():
    out=[]; cli=str(GF/'gf-stock-valuation'/'scripts'/'cli.py')
    for i in range(25):
        code,mkt=STOCKS[i]; q=f'查询{mkt}{code}的PE、PB、总市值、行业估值、PE历史百分位和PB历史百分位。'
        out.append(case(f'GF-VALUATION-{i+1:03d}','广发证券','股票估值',q,[['python',cli,'valuation',mkt+code]]))
    for j in range(25):
        c1=STOCKS[(j*2)%len(STOCKS)]; c2=STOCKS[(j*2+1)%len(STOCKS)]; rt=[12,9,6,1][j%4]
        q=f'对比{c1[1]}{c1[0]}和{c2[1]}{c2[0]}的ROE、营业收入、净利润、现金流、负债率和成长性，财报期{j%4+1}。'
        out.append(case(f'GF-VALUATION-{26+j:03d}','广发证券','股票估值',q,[['python',cli,'compare','--codes',c1[1]+c1[0],c2[1]+c2[0],'--year','2025','--report-type',str(rt)]]))
    return out

def gs_economy():
    metrics=['中国GDP增速','中国CPI同比','中国PPI同比','中国制造业PMI','中国M2同比','中国社会融资规模','中国工业增加值同比','中国社会消费品零售总额同比','中国固定资产投资同比','中国出口同比','中国进口同比','美国CPI同比','美国核心CPI同比','美联储基准利率','美元兑人民币汇率','黄金价格','布伦特原油价格','LME铜价','螺纹钢价格','碳酸锂价格','多晶硅价格','中国十年期国债收益率','欧元区GDP增速','日本CPI同比','韩国出口同比']
    periods=['最新值','近5年走势','近10年走势','今年','上个月']
    out=[]; n=0
    for p in periods:
        for m in metrics:
            if n>=50: break
            q=f'查询{m}{p}，并简要说明指标口径。'
            out.append(case(f'GS-ECON-{n+1:03d}','国信证券','宏观经济数据',q,[['python',str(ROOT/'tools'/'guosen_economy_wrapper.py'),q]])); n+=1
        if n>=50: break
    return out

def gs_etf_filter():
    out=[]; cli=str(GS/'gs-etf-filter'/'scripts'/'get_data.py'); prof=[(1,11),(1,13),(2,21),(2,22),(2,23),(2,24),(2,25),(3,31),(3,32)]
    for i,(c,l) in enumerate(prof):
        q=f'查询国信ETF专业榜单{l}，返回产品代码、名称、实时涨跌、5日涨幅、成交额、规模和T+0信息。'
        out.append(case(f'GS-ETF-{i+1:03d}','国信证券','ETF筛选',q,[['python',cli,'--class-id',str(c),'--list-id',str(l),'--output-dir',str(OUT/'artifacts'/f'GS-ETF-{i+1:03d}')]]))
    specs=[
      ['--class1','1'],['--class1','2'],['--class1','3'],['--class1','4'],['--class1','5'],['--class1','6'],['--class1','7'],
      ['--class1','1','--is-t0'],['--class1','1','--is-rzrq'],['--class1','2','--endamt','10,100'],['--class1','3','--endamt','50,100000'],
      ['--class1','1','--tgfandglf','0,0.5'],['--class1','1','--profitrank','profit1yrank:25'],['--class1','1','--drawback','drawback1y:20'],
      ['--class1','1','--sharpe','sharpe1yrank:25'],['--class1','1','--profit','profit1m:5,20'],['--class1','1','--pricerange','range5d:3,20'],
      ['--class1','2','--temper-region','3'],['--class1','2','--diviendyield','2,10'],['--class1','3','--hotrank','100']]
    for j in range(41):
        spec=specs[j%len(specs)] + ['--order-col','nowrange','--order-type',str(j%2)]
        q=f'筛选ETF，使用条件{"，".join(spec)}，按实时涨跌排序，返回产品代码、名称、最新价、成交额、规模、T+0和融资融券字段。'
        cid=f'GS-ETF-{10+j:03d}'; out.append(case(cid,'国信证券','ETF筛选',q,[['python',cli]+spec+['--output-dir',str(OUT/'artifacts'/cid)]]))
    return out

def gs_fund_compare():
    out=[]; cli=str(GS/'gs-fund-compare'/'scripts'/'get_data.py')
    valid_funds=['000001','001643','010068','519002','161039']
    for i in range(50):
        codes=[valid_funds[(i+j)%len(valid_funds)] for j in range(2+(i%2))]
        q=f'对比基金{"、".join(codes)}的业绩走势、风险控制、基金经理、规模和资产配置，并输出差异摘要。'
        cid=f'GS-FUND-{i+1:03d}'; out.append(case(cid,'国信证券','基金对比',q,[['python',cli,'--funds',','.join(codes),'--output',str(OUT/'artifacts'/cid)]]))
    return out

def gs_smart_stock():
    queries=['市盈率小于20的银行股','市净率小于1的银行股','ROE大于15的股票','净利润增长率大于30%的股票','近一月涨幅大于10%的股票','近5日涨幅大于5%且成交额大于10亿的股票','主力资金净流入前20的股票','MACD金叉的股票','KDJ超卖的股票','均线多头排列的股票','市盈率小于30且净利润增长大于20%的股票','食品饮料行业市值前20的股票','半导体行业股票','新能源概念股','人工智能概念股','机器人概念股','低估值高股息股票','创业板成交额前20的股票','科创板涨幅前20的股票','北交所涨幅前20的股票','连续三天上涨的股票','近10日跌幅超过20%的股票','换手率大于10%的股票','量比大于2的股票','市净率低于行业均值的股票','股息率大于3%的股票','营收同比大于20%的股票','经营现金流为正的股票','资产负债率小于50%的股票','毛利率大于30%的股票','市盈率低于10且ROE大于10%的股票','近20日新高股票','跌破20日均线的股票','站上60日均线的股票','近5日主力净流入的股票','近1月机构调研较多的股票','市值50亿到200亿的股票','价格10元以下且成交额大于1亿的股票','医药行业低估值股票','军工行业涨幅前20的股票','消费行业ROE前20的股票','金融行业股息率前20的股票','黄金概念股','稀土概念股','光伏概念股','储能概念股','数据中心概念股','国产软件概念股','高成长科技股','近一年ROE排名前50的股票']
    return [case(f'GS-PICK-{i+1:03d}','国信证券','智能选股',q,[['python',str(ROOT/'tools'/'guosen_smart_stock_wrapper.py'),'--searchstring',q,'--searchtype','stock','--api-key',GS_API_KEY_PLACEHOLDER]]) for i,q in enumerate(queries[:50])]

def gs_finance():
    out=[]; cli=str(GS/'gs-stock-financial-query'/'scripts'/'get_data.py'); actions=['a_income','a_balance','a_cashflow']; i=1
    for code,mkt in STOCKS[:10]:
        for j in range(5):
            action=actions[j%3]; rt=['Q4','Q2','Q3','Q1'][j%4]; cnt=[2,4,8][j%3]
            q=f'查询{code}.{mkt}的{action}，报告期{rt}，返回最近{cnt}期关键字段。'
            out.append(case(f'GS-FIN-{i:03d}','国信证券','财务数据',q,[['python',cli,action,'--code',code,'--market',mkt,'--report_type',rt,'--count',str(cnt)]])); i+=1
    return out

def gs_market():
    out=[]; cli=str(GS/'gs-stock-market-query'/'scripts'/'get_data.py'); i=1
    for code,mkt in STOCKS[:15]:
        q=f'查询{code}.{mkt}实时行情、成交额、换手率、市盈率、市净率和总市值。'; sc='1' if mkt=='SH' else '0'
        out.append(case(f'GS-MARKET-{i:03d}','国信证券','行情数据',q,[['python',cli,'single_hq','--code',code,'--set_code',sc]])); i+=1
    for j in range(10):
        c1=STOCKS[j]; c2=STOCKS[j+10]; q=f'对比{c1[0]}和{c2[0]}的实时行情、涨跌幅、成交额和换手率。'
        out.append(case(f'GS-MARKET-{i:03d}','国信证券','行情数据',q,[['python',cli,'comb_hq','--codes',c1[0]+','+c2[0],'--set_codes',('1' if c1[1]=='SH' else '0')+','+('1' if c2[1]=='SH' else '0')]])); i+=1
    for j in range(10):
        code,mkt=STOCKS[j]; q=f'查询{code}.{mkt}近{5+j%3*5}日资金流入流出和主力净流入。'
        out.append(case(f'GS-MARKET-{i:03d}','国信证券','行情数据',q,[['python',cli,'fund_flow','--code',code,'--set_code','1' if mkt=='SH' else '0','--period',str(5+j%3*5)]])); i+=1
    for j in range(5):
        dom=[6,14,12,11005,12006][j]; q=f'查询市场域{dom}涨幅前20，返回代码、名称、涨跌幅、成交额和换手率。'
        out.append(case(f'GS-MARKET-{i:03d}','国信证券','行情数据',q,[['python',cli,'multi_hq','--set_domain',str(dom),'--want_num','20','--sort_type','1']])); i+=1
    for j in range(5):
        code,mkt=STOCKS[j]; q=f'查询{code}.{mkt}关联指数和所属板块。'
        out.append(case(f'GS-MARKET-{i:03d}','国信证券','行情数据',q,[['python',cli,'related_comb','--code',code,'--set_code','1' if mkt=='SH' else '0']])); i+=1
    for j in range(5):
        code,mkt=STOCKS[j]; q=f'查询{code}.{mkt}最近{20+j*10}个交易日历史行情，包含开高低收、成交量和成交额。'
        out.append(case(f'GS-MARKET-{i:03d}','国信证券','行情数据',q,[['python',cli,'past_hq','--code',code,'--set_code','1' if mkt=='SH' else '0','--want_nums',str(20+j*10)]])); i+=1
    return out

def all_cases():
    groups=[gf_etf_rank(),gf_etf_search(),gf_super_fund(),gf_fund_detail(),gf_fund_invest(),gf_lhb(),gf_f10(),gf_valuation(),gs_economy(),gs_etf_filter(),gs_fund_compare(),gs_smart_stock(),gs_finance(),gs_market()]
    for g in groups: assert len(g)==50,(g[0]['skill'],len(g))
    return sum(groups,[])

def parse_json(text):
    try:return json.loads(text)
    except Exception:return None

def find_count(obj):
    if isinstance(obj,list): return len(obj)
    if not isinstance(obj,dict): return 0
    candidates=[]
    for k,v in obj.items():
        if isinstance(v,list) and k.lower() in {'data','items','result','results','fundlist','list','income','balance','cashflow','object','candidates','records','table'}: candidates.append(len(v))
    return max(candidates,default=0)

def collect_artifacts(case_dir):
    out=[]
    if not case_dir or not Path(case_dir).exists(): return out
    for p in sorted(Path(case_dir).rglob('*')):
        if p.is_file():
            item={'path':str(p).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            if p.suffix.lower() in {'.txt','.json','.csv','.md'}:
                item['text']=p.read_text(encoding='utf-8',errors='replace')[:200000]
            out.append(item)
    return out

def _redact(text: str) -> str:
    for key_name in ('GS_API_KEY','GF_SKILLS_APIKEY','COZE_GUOSEN_API_KEY_7627056463827140634','COZE_GUOSEN_API_KEY_7627085587157205043'):
        secret=os.environ.get(key_name,'')
        if secret:
            text=text.replace(secret,'<REDACTED_API_KEY>')
    return text

def run_case(c):
    env=os.environ.copy(); env['PYTHONIOENCODING']='utf-8'; env['GF_SKILLS_APIKEY']=os.environ.get('GF_SKILLS_APIKEY',''); env['GS_API_KEY']=os.environ.get('GS_API_KEY',''); env['COZE_GUOSEN_API_KEY_7627056463827140634']=env['GS_API_KEY']; env['COZE_GUOSEN_API_KEY_7627085587157205043']=env['GS_API_KEY']
    started=time.time(); results=[]
    for cmd in c['commands']:
        public_cmd=[str(x) for x in cmd]
        exec_cmd=[os.environ.get('GS_API_KEY','') if x==GS_API_KEY_PLACEHOLDER else x for x in public_cmd]
        try:
            p=subprocess.run(exec_cmd,capture_output=True,env=env,cwd=str(ROOT),timeout=120)
            stdout=_redact(p.stdout.decode('utf-8',errors='replace')); stderr=_redact(p.stderr.decode('utf-8',errors='replace'))
            results.append({'command':public_cmd,'returncode':p.returncode,'stdout':stdout,'stderr':stderr,'parsed':parse_json(stdout)})
        except Exception as exc:
            results.append({'command':public_cmd,'returncode':-1,'stdout':'','stderr':_redact(f'{type(exc).__name__}: {exc}'),'parsed':None})
    artifact_dir = c.get('output_dir') or str(OUT/'artifacts'/c['case_id'])
    artifacts=collect_artifacts(artifact_dir)
    text='\n'.join((r['stdout'] or '')+'\n'+(r['stderr'] or '') for r in results)
    for a in artifacts:
        if a.get('text'): text += '\n'+a['text']
    count=max(find_count(r['parsed']) for r in results)
    if artifacts:
        m=re.search(r'ETF数量:\s*(\d+)',text); m2=re.search(r'对比基金数量:\s*(\d+)',text); m3=len(re.findall(r'结果 #',text))
        count=max(count,int(m.group(1)) if m else 0,int(m2.group(1)) if m2 else 0,m3)
    error_text=any(x in text for x in ['Traceback','请求失败','未获取到结果','API Key','缺少必要','FundResolveError','error:'])
    ok=all(r['returncode']==0 for r in results) and not error_text
    nonempty=bool(text.strip()) or bool(artifacts)
    status='success' if ok and nonempty and (count>0 or bool(artifacts) or c['skill']=='宏观经济数据' or c['skill'] not in ['ETF筛选','基金对比','智能选股']) else ('empty' if ok and nonempty else 'error')
    if c['skill']=='宏观经济数据' and ok and len(text.strip())>100: status='success'
    return {'case_id':c['case_id'],'institution':c['institution'],'skill':c['skill'],'question':c['question'],'commands':c['commands'],'status':status,'returncode':max(r['returncode'] for r in results),'elapsed_sec':round(time.time()-started,3),'result_count':count,'results':results,'artifacts':artifacts}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--limit',type=int,default=0); ap.add_argument('--workers',type=int,default=4); ap.add_argument('--only-skill'); ap.add_argument('--resume',action='store_true'); ap.add_argument('--merge',action='store_true'); args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True); cases=all_cases()
    if args.only_skill: cases=[c for c in cases if c['skill']==args.only_skill]
    if args.limit: cases=cases[:args.limit]
    (OUT/'cases.jsonl').write_text('\n'.join(json.dumps(c,ensure_ascii=False) for c in cases)+'\n',encoding='utf-8')
    rows=[]; raw=OUT/'results.jsonl'
    existing_byid={}
    if (args.resume or args.merge) and raw.exists():
        rows=[json.loads(x) for x in raw.read_text(encoding='utf-8').splitlines() if x.strip()]
        existing_byid={r['case_id']:r for r in rows}
        if args.resume:
            done=set(existing_byid); cases=[c for c in cases if c['case_id'] not in done]
    with ThreadPoolExecutor(max_workers=max(1,args.workers)) as ex:
        futs={ex.submit(run_case,c):c for c in cases}
        for n,f in enumerate(as_completed(futs),1):
            c=futs[f]
            try:r=f.result()
            except Exception as exc:r={'case_id':c['case_id'],'institution':c['institution'],'skill':c['skill'],'question':c['question'],'status':'harness_error','error':f'{type(exc).__name__}: {exc}','result_count':0,'results':[],'artifacts':[]}
            rows.append(r); print(f'[{n}/{len(cases)}] {r["case_id"]} {r["status"]} count={r.get("result_count",0)}',flush=True)
    if args.merge:
        merged={**existing_byid, **{r['case_id']:r for r in rows}}
        rows=sorted(merged.values(),key=lambda x:x['case_id'])
    else:
        rows.sort(key=lambda x:x['case_id'])
    raw.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n',encoding='utf-8')
    summary=[{'case_id':r['case_id'],'institution':r['institution'],'skill':r['skill'],'question':r['question'],'status':r['status'],'result_count':r.get('result_count',0),'elapsed_sec':r.get('elapsed_sec',0),'artifact_count':len(r.get('artifacts',[])),'error':r.get('error','')} for r in rows]
    with (OUT/'summary.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0].keys())); w.writeheader(); w.writerows(summary)
    print('DONE',len(rows),raw,OUT/'summary.csv')
if __name__=='__main__': main()