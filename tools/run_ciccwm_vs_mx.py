#!/usr/bin/env python3
"""Run a large CICC Wealth vs MX MCP comparative suite.

The suite covers six CICC Wealth Skills with positive natural-language questions.
CICC commands are structured; MX receives the same natural-language question.
No API key is written to disk by this script.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CICC = ROOT / "01_竞品Skills" / "中金财富" / "extracted"
OUT = ROOT / "04_测试结果" / "中金财富" / "benchmark"
sys.path.insert(0, str(ROOT / "tools"))
from mx_mcp_client import initialize, call_tool, session_headers, normalized_text  # noqa: E402

STOCKS = [
    ("600519", "贵州茅台", "1"), ("000001", "平安银行", "0"),
    ("300750", "宁德时代", "0"), ("600036", "招商银行", "1"),
    ("601318", "中国平安", "1"), ("000333", "美的集团", "0"),
    ("000858", "五粮液", "0"), ("002594", "比亚迪", "0"),
    ("600900", "长江电力", "1"), ("601166", "兴业银行", "1"),
    ("600030", "中信证券", "1"), ("000776", "广发证券", "0"),
    ("300059", "东方财富", "0"), ("601899", "紫金矿业", "1"),
    ("688981", "中芯国际", "1"),
]
DATES = ["2026-11-13","2026-11-12","2026-11-11","2026-11-10","2026-11-09",
         "2026-11-06","2026-11-05","2026-11-04","2026-11-03","2026-11-02"]
TIGER_CODES = ["0101600715","0001300324","0001002739","0001002520","0001300237",
               "0001002124","0001002623","0001000530","0101603686","0101603366"]
FUND_KEYWORDS = ["华夏成长","易方达蓝筹精选","中证500","沪深300","招商中证白酒",
                 "富国天惠","工银瑞信","南方中证500ETF联接","广发多因子","兴全合润"]

FIELD_ALIASES = {
    "代码": ["代码", "code", "secu_code", "fund_code", "dt_sec_code"],
    "名称": ["名称", "name", "secu_name", "fund_short_name", "fund_name"],
    "最新价": ["最新价", "现价", "now", "close", "f_close_price"],
    "涨跌幅": ["涨跌幅", "涨幅", "rise_down_ratio", "f_change_pct"],
    "成交额": ["成交额", "amount", "AMOUNT"],
    "成交量": ["成交量", "volume", "VOL"],
    "换手率": ["换手率", "turnover_rate", "HSL"],
    "溢价率": ["溢价", "premium_rate", "KZZYJL"],
    "主力净流入": ["主力净", "主力净额", "main_net_amount", "VAR0412", "f_income"],
    "总市值": ["总市值", "total_market_value", "ZSZ"],
    "跟踪指数": ["跟踪", "track_index", "GZZS"],
    "5日涨跌幅": ["5日涨跌幅", "rho_5d", "RHO"],
    "20日涨跌幅": ["20日涨跌幅", "20ZAF"],
    "60日涨跌幅": ["60日涨跌幅", "vega_60d", "VEGA"],
    "今年以来": ["今年以来", "thisyear", "THISYEAR"],
    "连涨天数": ["连涨", "consecutive_days", "CONZAFDATENUM"],
    "市盈率": ["市盈率", "PE", "PETTM", "SYL"],
    "市净率": ["市净率", "PB"],
    "净资产收益率": ["净资产收益率", "ROE", "jzcsyl"],
    "营业收入": ["营业收入", "yysr", "营业总收入"],
    "净利润": ["净利润", "jlr", "kfjlr"],
    "经营现金流": ["经营现金流", "经营活动产生的现金流量净额", "JYXJL"],
    "投资现金流": ["投资现金流", "投资活动产生的现金流量净额"],
    "筹资现金流": ["筹资现金流", "筹资活动产生的现金流量净额"],
    "现金净增加额": ["现金净增加额", "现金及现金等价物净增加额"],
    "总资产": ["总资产", "资产总计"],
    "总负债": ["总负债", "负债合计"],
    "货币资金": ["货币资金"],
    "存货": ["存货"],
    "应收账款": ["应收账款"],
    "资产负债率": ["资产负债率", "zcfzl"],
    "基金代码": ["基金代码", "fund_code"],
    "基金名称": ["基金名称", "fund_name", "fund_short_name"],
    "基金经理": ["基金经理", "manager"],
    "基金规模": ["基金规模", "规模", "scale"],
    "风险等级": ["风险等级", "risk_level"],
    "单位净值": ["单位净值", "nav"],
    "费率": ["费率", "申购费", "赎回费", "管理费", "托管费"],
    "重仓股": ["重仓股", "持仓", "holding"],
    "分红": ["分红", "dividend"],
    "新闻标题": ["标题", "title"],
    "新闻来源": ["来源", "source"],
    "发布时间": ["发布时间", "pub_time", "date"],
    "上榜原因": ["上榜原因", "reason"],
    "净买入": ["净买入", "f_income", "净额"],
    "营业部": ["营业部", "s_name", "yyb"],
    "板块": ["板块", "industry", "concept"],
    "开高低收": ["开盘", "最高", "最低", "收盘", "open", "high", "low", "close"],
}


def base_case(case_id: str, skill: str, question: str, commands: list[list[str]], mx_tool: str, required: list[str]):
    return {"case_id": case_id, "skill": skill, "question": question, "commands": commands, "mx_tool": mx_tool, "mx_query": question, "required_fields": required}


def script(skill: str, name: str) -> str:
    return str(CICC / skill / skill / "scripts" / name)


def market_cases() -> list[dict[str, Any]]:
    out=[]
    mk=script("ciccwm-market-analysis","market_query.py")
    for i,(code,name,mkt) in enumerate(STOCKS[:10],1):
        q=f"查询{name}（{code}）最新价、涨跌幅、成交额、成交量、换手率、总市值、市盈率和市净率，并说明数据日期。"
        out.append(base_case(f"MK-{i:03d}","行情数据",q,[["python",mk,"info","--code",code,"--market",mkt]],"mx_ashare_finance_data",["代码","名称","最新价","涨跌幅","成交额","成交量","换手率","总市值","市盈率","市净率"]))
    for i,(code,name,mkt) in enumerate(STOCKS[:10],11):
        q=f"查询{name}（{code}）今日主力净流入、资金流入、资金流出、成交额和换手率。"
        out.append(base_case(f"MK-{i:03d}","行情数据",q,[["python",mk,"fund","--code",code,"--market",mkt]],"mx_ashare_finance_data",["主力净流入","成交额","换手率"]))
    ranking_specs=[("6","1",10,"沪深A股涨幅前10"),("6","0",10,"沪深A股跌幅前10"),("14","1",10,"创业板涨幅前10"),("0","1",10,"上证A股涨幅前10"),("0","0",10,"上证A股跌幅前10"),("2","1",10,"深证A股涨幅前10"),("2","0",10,"深证A股跌幅前10"),("11005","1",10,"沪深ETF涨幅前10"),("11005","0",10,"沪深ETF跌幅前10"),("12006","1",10,"港股通涨幅前10")]
    for i,(mkt,st,lim,label) in enumerate(ranking_specs,21):
        q=f"查询{label}，返回代码、名称、最新价、涨跌幅、成交额、总市值和主力净额。"
        out.append(base_case(f"MK-{i:03d}","行情数据",q,[["python",mk,"ranking","--market",mkt,"--limit",str(lim),"--sort_type",st]],"mx_stocks_screener",["代码","名称","最新价","涨跌幅","成交额","总市值","主力净流入"]))
    for i,(code,name,mkt) in enumerate(STOCKS[:10],31):
        days=[5,10,20,60][(i-1)%4]
        q=f"查询{name}（{code}）近{days}个交易日开盘、最高、最低、收盘、成交量和成交额。"
        out.append(base_case(f"MK-{i:03d}","行情数据",q,[["python",mk,"history","--code",code,"--market",mkt,"--days",str(days)]],"mx_ashare_finance_data",["开高低收","成交量","成交额"]))
    for i,(code,name,mkt) in enumerate(STOCKS[:10],41):
        q=f"查询{name}（{code}）所属行业、概念板块和地域板块。"
        out.append(base_case(f"MK-{i:03d}","行情数据",q,[["python",mk,"related","--code",code,"--market",mkt]],"mx_ashare_finance_data",["名称","板块"]))
    return out


def finance_cases() -> list[dict[str, Any]]:
    out=[]; fin=script("ciccwm-stock-finance-analysis","finance_query.py")
    for i,(code,name,mkt) in enumerate(STOCKS[:15],1):
        qt=["annual","mid","q1","q3"][(i-1)%4]
        q=f"查询{name}（{code}）最近3期{qt}口径的营业收入、净利润、ROE、毛利率、净利率和资产负债率。"
        out.append(base_case(f"FIN-{i:03d}","财务数据",q,[["python",fin,"indicators","--code",code,"--qtime",qt,"--limit","3"]],"mx_ashare_finance_data",["营业收入","净利润","净资产收益率","资产负债率"]))
    for i,(code,name,mkt) in enumerate(STOCKS[:10],16):
        q=f"查询{name}（{code}）最近3期利润表的营业收入、营业成本、营业利润和净利润。"
        out.append(base_case(f"FIN-{i:03d}","财务数据",q,[["python",fin,"income","--code",code,"--qtime","annual","--limit","3"]],"mx_ashare_finance_data",["营业收入","净利润"]))
    for i,(code,name,mkt) in enumerate(STOCKS[:10],26):
        q=f"查询{name}（{code}）最近3期经营现金流、投资现金流、筹资现金流和现金净增加额。"
        out.append(base_case(f"FIN-{i:03d}","财务数据",q,[["python",fin,"cashflow","--code",code,"--qtime","annual","--limit","3"]],"mx_ashare_finance_data",["经营现金流","投资现金流","筹资现金流","现金净增加额"]))
    for i,(code,name,mkt) in enumerate(STOCKS[:10],36):
        q=f"查询{name}（{code}）最近3期总资产、总负债、货币资金、存货和应收账款。"
        out.append(base_case(f"FIN-{i:03d}","财务数据",q,[["python",fin,"balance","--code",code,"--qtime","annual","--limit","3"]],"mx_ashare_finance_data",["总资产","总负债","货币资金","存货","应收账款"]))
    for i,(code,name,mkt) in enumerate(STOCKS[:5],46):
        q=f"综合查询{name}（{code}）最近1期主要指标、利润表、现金流量表和资产负债表，并给出财务质量摘要。"
        cmds=[["python",fin,"indicators","--code",code,"--qtime","annual","--limit","1"],["python",fin,"income","--code",code,"--qtime","annual","--limit","1"],["python",fin,"cashflow","--code",code,"--qtime","annual","--limit","1"],["python",fin,"balance","--code",code,"--qtime","annual","--limit","1"]]
        out.append(base_case(f"FIN-{i:03d}","财务数据",q,cmds,"mx_ashare_finance_data",["营业收入","净利润","经营现金流","资产负债率"]))
    return out


def etf_cases() -> list[dict[str, Any]]:
    out=[]; etf=script("ciccwm-etf-ranking-analysis","etf_ranking_query.py")
    labels={"today":"今日涨跌幅","5d":"近5日涨跌幅","20d":"近20日涨跌幅","60d":"近60日涨跌幅","year":"今年以来涨跌幅"}
    i=1
    for typ in labels:
        for lim in [5,10,20,50,80]:
            q=f"查询ETF{labels[typ]}榜前{lim}只，返回代码、名称、现价、成交额、换手率、溢价率、总市值、5日涨跌幅、20日涨跌幅、60日涨跌幅和今年以来涨幅。"
            out.append(base_case(f"ETF-{i:03d}","ETF热榜",q,[["python",etf,"price","--type",typ,"--limit",str(lim),"--sort_type","1"]],"mx_stocks_screener",["代码","名称","最新价","成交额","换手率","溢价率","总市值","5日涨跌幅","20日涨跌幅","60日涨跌幅","今年以来"])); i+=1
    for typ in labels:
        for lim in [10,20]:
            q=f"查询ETF{labels[typ]}榜跌幅方向前{lim}只，返回代码、名称、现价、涨跌幅、成交额、换手率和总市值。"
            out.append(base_case(f"ETF-{i:03d}","ETF热榜",q,[["python",etf,"price","--type",typ,"--limit",str(lim),"--sort_type","0"]],"mx_stocks_screener",["代码","名称","最新价","涨跌幅","成交额","换手率","总市值"])); i+=1
    fund_labels={"main":"主力净额","subscribe":"申购净流入","finance":"融资净流入"}
    for typ,label in fund_labels.items():
        for lim in [5,10,20,30,50]:
            q=f"查询ETF{label}榜前{lim}只，返回代码、名称、成交额、主力净额、申购净流入、融资净流入、总市值、换手率和溢价率。"
            out.append(base_case(f"ETF-{i:03d}","ETF热榜",q,[["python",etf,"fund","--type",typ,"--limit",str(lim),"--sort_type","1"]],"mx_stocks_screener",["代码","名称","成交额","主力净流入","总市值","换手率","溢价率"])); i+=1
    special={"consecutive":"连涨榜","turnover":"换手榜","premium":"溢价榜","custom":"自选榜"}
    for typ,label in special.items():
        for lim in [5,10,20]:
            q=f"查询ETF{label}前{lim}只，返回代码、名称、现价、成交额、连涨天数、换手率、溢价率和总市值。"
            out.append(base_case(f"ETF-{i:03d}","ETF热榜",q,[["python",etf,"special","--type",typ,"--limit",str(lim)]],"mx_stocks_screener",["代码","名称","最新价","成交额","连涨天数","换手率","溢价率","总市值"])); i+=1
    for lim in [5,10,20]:
        q=f"查询ETF热搜榜前{lim}只，并补充现价、涨跌幅、成交额、总市值、换手率和溢价率。"
        out.append(base_case(f"ETF-{i:03d}","ETF热榜",q,[["python",etf,"hot_search","--limit",str(lim)]],"mx_stocks_screener",["代码","名称","最新价","涨跌幅","成交额","总市值","换手率","溢价率"])); i+=1
    combos=[
        ["代码","名称","成交额","换手率"],
        ["代码","名称","今日涨跌幅","5日涨跌幅","20日涨跌幅"],
        ["代码","名称","今日涨跌幅","60日涨跌幅","今年以来"],
        ["代码","名称","主力净额","成交额","总市值"],
        ["代码","名称","申购净流入","融资净流入","成交额"],
        ["代码","名称","连涨天数","换手率","溢价率"],
        ["代码","名称","现价","成交额","总市值","换手率","溢价率","5日涨跌幅","20日涨跌幅","60日涨跌幅","今年以来"],
    ]
    types=list(labels)
    for j,fields in enumerate(combos):
        for k,typ in enumerate(types):
            lim=10 if (j+k)%2==0 else 20
            q=f"查询ETF{labels[typ]}榜前{lim}只，并按顺序返回"+ "、".join(fields) +"这些字段。"
            out.append(base_case(f"ETF-{i:03d}","ETF热榜",q,[["python",etf,"price","--type",typ,"--limit",str(lim),"--sort_type","1"]],"mx_stocks_screener",fields)); i+=1
    assert len(out)==100,len(out)
    return out


def news_cases() -> list[dict[str, Any]]:
    out=[]; news=script("ciccwm-hot-news-analysis","get_data.py"); i=1
    for typ in [1,2,3,4]:
        for size in [5,10,20]:
            for page in [1,2]:
                if i>30: break
                q=f"查询今日热榜第{page}页、每页{size}条，资讯类型{typ}，返回标题、来源、发布时间和摘要。"
                out.append(base_case(f"NEWS-{i:03d}","热榜资讯",q,[["python",news,"hot_rank","--page_num",str(page),"--page_size",str(size),"--type",str(typ)]],"mx_finance_search_news",["新闻标题","新闻来源","发布时间"])); i+=1
            if i>30: break
        if i>30: break
    # guarantee 30 cases with valid combinations
    while i<=30:
        q=f"查询今日热榜第{((i-1)%3)+1}页、每页{5 if i%2 else 10}条，返回标题、来源和发布时间。"
        out.append(base_case(f"NEWS-{i:03d}","热榜资讯",q,[["python",news,"hot_rank","--page_num",str(((i-1)%3)+1),"--page_size",str(5 if i%2 else 10),"--type","1"]],"mx_finance_search_news",["新闻标题","新闻来源","发布时间"])); i+=1
    for j in range(20,0,-1):
        typ=(j%4)+1; size=[5,10,20][j%3]; page=(j%2)+1
        q=f"查询专题热榜第{page}页、每页{size}条，类型{typ}，返回标题、来源、发布时间和关联板块。"
        out.append(base_case(f"NEWS-{i:03d}","热榜资讯",q,[["python",news,"topic","--spec_subject_id","35","--page_num",str(page),"--page_size",str(size),"--type",str(typ)]],"mx_finance_search_news",["新闻标题","新闻来源","发布时间","板块"])); i+=1
    assert len(out)==50,len(out)
    return out


def tiger_cases() -> list[dict[str, Any]]:
    out=[]; tiger=script("ciccwm-tiger-list-analysis","tiger_list_query.py"); i=1
    for d in DATES:
        for lt in ["all","overall"]:
            q=f"查询{d}龙虎榜{lt}榜单，返回股票代码、名称、收盘价、涨跌幅、上榜原因、净买入额和席位信息。"
            out.append(base_case(f"TIGER-{i:03d}","龙虎榜",q,[["python",tiger,"stock_list","--req_date",d,"--req_type","2","--list_type",lt]],"mx_finance_search_news",["代码","名称","最新价","涨跌幅","上榜原因","净买入"])); i+=1
    for j,d in enumerate(DATES):
        rt="1" if j%2==0 else "2"
        q=f"查询{d}活跃营业部榜单，返回营业部名称、上榜股票数量和净买入额。"
        out.append(base_case(f"TIGER-{i:03d}","龙虎榜",q,[["python",tiger,"active_orgs","--req_date",d,"--req_type",rt]],"mx_finance_search_news",["营业部","净买入"])); i+=1
    for code in TIGER_CODES:
        q=f"查询龙虎榜股票代码{code}的个股详情、买卖前五席位和净买入额。"
        out.append(base_case(f"TIGER-{i:03d}","龙虎榜",q,[["python",tiger,"stock_detail","--stock_code",code]],"mx_finance_search_news",["代码","名称","净买入","营业部"])); i+=1
    # Resolve valid org names from the latest active list.
    env=os.environ.copy(); env["PYTHONIOENCODING"]="utf-8"
    p=subprocess.run(["python",tiger,"active_orgs"],capture_output=True,env=env,timeout=60)
    try:
        orgs=[x["s_name"] for x in json.loads(p.stdout.decode("utf-8")).get("sale_org_list",[])[:5]]
    except Exception:
        orgs=[]
    for j in range(10):
        if not orgs: break
        org=orgs[j%len(orgs)]; d=DATES[j%len(DATES)]
        q=f"查询营业部“{org}”在{d}的活跃度画像、上榜股票数量和净买入额。"
        out.append(base_case(f"TIGER-{i:03d}","龙虎榜",q,[["python",tiger,"org_detail","--yyb",org,"--req_date",d]],"mx_finance_search_news",["营业部","净买入"])); i+=1
    while len(out)<50:
        d=DATES[len(out)%len(DATES)]; q=f"查询{d}龙虎榜全部榜单并汇总上榜股票和净买入额。"
        out.append(base_case(f"TIGER-{len(out)+1:03d}","龙虎榜",q,[["python",tiger,"stock_list","--req_date",d,"--req_type","2","--list_type","all"]],"mx_finance_search_news",["代码","名称","净买入"]))
    return out


def fund_cases() -> list[dict[str, Any]]:
    out=[]; fund=script("ciccwm-fund-product-info","fund_product_query.py"); i=1
    for kw in FUND_KEYWORDS:
        q=f"搜索基金关键词“{kw}”，返回基金代码、基金名称、风险等级、申购状态和内部产品ID。"
        out.append(base_case(f"FUND-{i:03d}","基金产品",q,[["python",fund,"search","--keyword",kw,"--size","10"]],"mx_fund_finance_data",["基金代码","基金名称","风险等级"])); i+=1
    for kw in FUND_KEYWORDS[:8]:
        q=f"查询基金“{kw}”的档案，返回基金代码、名称、类型、成立日、规模、基金经理、风险等级和投资目标。"
        out.append(base_case(f"FUND-{i:03d}","基金产品",q,[["python",fund,"profile","--keyword",kw,"--select-first"]],"mx_fund_finance_data",["基金代码","基金名称","基金经理","基金规模","风险等级"])); i+=1
    for cmd,count in [("fees",5),("holding",5),("performance",6),("events",6)]:
        req={"fees":["基金代码","基金名称","费率"],"holding":["基金代码","基金名称","重仓股"],"performance":["基金代码","基金名称"],"events":["基金代码","基金名称","分红"]}[cmd]
        for j in range(count):
            kw=FUND_KEYWORDS[(i+j)%len(FUND_KEYWORDS)]
            q=f"查询基金“{kw}”的{ {'fees':'申购赎回费率','holding':'重仓股与行业配置','performance':'阶段收益和历史表现','events':'分红与公告'}[cmd] }，返回基金代码、基金名称及相关明细。"
            out.append(base_case(f"FUND-{i:03d}","基金产品",q,[["python",fund,cmd,"--keyword",kw,"--select-first"]],"mx_fund_finance_data",req)); i+=1
    pairs=[("华夏成长","中证500"),("易方达蓝筹精选","富国天惠"),("沪深300","中证500"),("招商中证白酒","易方达蓝筹精选"),("工银瑞信","华夏成长"),("南方中证500ETF联接","沪深300"),("广发多因子","兴全合润"),("富国天惠","兴全合润"),("华夏成长","工银瑞信"),("中证500","沪深300")]
    for pair in pairs:
        q=f"对比基金“{pair[0]}”和“{pair[1]}”的规模、风险等级、基金经理、费率、阶段表现和持仓。"
        cmds=[["python",fund,"compare","--items",pair[0],pair[1],"--select-first","--include_fees","--include_performance"]]
        out.append(base_case(f"FUND-{i:03d}","基金产品",q,cmds,"mx_fund_finance_data",["基金代码","基金名称","基金经理","基金规模","风险等级","费率"])); i+=1
    assert len(out)==50,len(out)
    return out


def all_cases():
    cases=market_cases()+finance_cases()+etf_cases()+news_cases()+tiger_cases()+fund_cases()
    return cases


def run_command(cmd: list[str]) -> dict[str, Any]:
    env=os.environ.copy(); env["PYTHONIOENCODING"]="utf-8"
    started=time.time()
    try:
        p=subprocess.run(cmd,capture_output=True,env=env,cwd=str(ROOT),timeout=90)
        stdout=p.stdout.decode("utf-8",errors="replace")
        stderr=p.stderr.decode("utf-8",errors="replace")
        parsed=None
        try: parsed=json.loads(stdout)
        except Exception: parsed=None
        return {"command":cmd,"returncode":p.returncode,"elapsed_sec":round(time.time()-started,3),"stdout":stdout,"stderr":stderr,"parsed":parsed}
    except Exception as exc:
        return {"command":cmd,"returncode":-1,"elapsed_sec":round(time.time()-started,3),"stdout":"","stderr":f"{type(exc).__name__}: {exc}","parsed":None}


def deep_parse_strings(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: deep_parse_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [deep_parse_strings(v) for v in obj]
    if isinstance(obj, str):
        stripped = obj.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                return deep_parse_strings(json.loads(stripped))
            except Exception:
                return obj
    return obj


def flatten_text(obj: Any) -> str:
    return json.dumps(obj,ensure_ascii=False) if not isinstance(obj,str) else obj


def extract_codes(obj: Any) -> set[str]:
    codes=set(); allowed={"code","secu_code","fund_code","dt_sec_code","stock_code","securitycode"}
    def walk(x):
        if isinstance(x,dict):
            for k,v in x.items():
                lk=str(k).lower()
                if lk in allowed and isinstance(v,(str,int)):
                    digits=re.sub(r"\D","",str(v))
                    if len(digits)>=6: codes.add(digits[-6:])
                walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(obj); return codes


def mx_codes_from_payload(payload: Any) -> set[str]:
    codes=set()
    if not isinstance(payload,dict): return codes
    for block in payload.get("data",[]) or []:
        cols=[str(x) for x in block.get("columns",[]) or []]
        for col in cols:
            for m in re.findall(r"(?<!\d)(\d{6})(?!\d)", col):
                codes.add(m)
        code_idx=next((i for i,c in enumerate(cols) if "代码" in c or c.lower() in ("code","基金代码")),None)
        if code_idx is not None:
            for row in block.get("items",[]) or []:
                if isinstance(row,list) and code_idx<len(row):
                    digits=re.sub(r"\D","",str(row[code_idx]))
                    if len(digits)>=6: codes.add(digits[-6:])
    codes |= extract_codes(payload)
    return codes


def adoption_from_payload(payload: Any) -> str:
    if not isinstance(payload,dict): return ""
    for block in payload.get("data",[]) or []:
        meta=block.get("meta") or {}
        a=meta.get("screeningResultAdoption") or {}
        if a: return str(a.get("adopted") or "")
    return ""


def field_hits(text: str, required: list[str]) -> list[str]:
    low=text.lower(); hits=[]
    for field in required:
        aliases=FIELD_ALIASES.get(field,[field])
        if any(str(a).lower() in low for a in aliases): hits.append(field)
    return hits


def run_case(case: dict[str, Any], headers: dict[str,str]) -> dict[str, Any]:
    comp_results=[run_command(c) for c in case["commands"]]
    comp_parsed=[deep_parse_strings(r["parsed"]) for r in comp_results if r["parsed"] is not None]
    comp_text=flatten_text(comp_parsed if len(comp_parsed)>1 else (comp_parsed[0] if comp_parsed else comp_results))
    comp_ok=all(r["returncode"]==0 and r["parsed"] is not None for r in comp_results)
    comp_codes=set()
    for p in comp_parsed: comp_codes |= extract_codes(p)
    mx_resp={}; mx_text=""; mx_parsed=None; mx_error=""
    try:
        mx_resp=call_tool(headers,case["mx_tool"],{"query":case["mx_query"]})
        mx_text=normalized_text(mx_resp)
        try: mx_parsed=deep_parse_strings(json.loads(mx_text)) if mx_text else None
        except Exception: mx_parsed=None
    except Exception as exc:
        mx_error=f"{type(exc).__name__}: {exc}"
    mx_codes=mx_codes_from_payload(mx_parsed)
    adoption=adoption_from_payload(mx_parsed)
    mx_items=sum(len(b.get("items",[]) or []) for b in (mx_parsed or {}).get("data",[]) or [] if isinstance(b,dict))
    comp_hits=field_hits(comp_text,case["required_fields"])
    mx_hits=field_hits(mx_text,case["required_fields"])
    comp_field_coverage=round(len(comp_hits)/len(case["required_fields"]),4) if case["required_fields"] else None
    mx_field_coverage=round(len(mx_hits)/len(case["required_fields"]),4) if case["required_fields"] else None
    overlap=round(len(comp_codes & mx_codes)/len(comp_codes),4) if comp_codes else None
    return {
        "case_id":case["case_id"],"skill":case["skill"],"question":case["question"],
        "required_fields":case["required_fields"],"competitor_commands":case["commands"],
        "competitor_returncode":max(r["returncode"] for r in comp_results),
        "competitor_elapsed_sec":round(sum(r["elapsed_sec"] for r in comp_results),3),
        "competitor_ok":comp_ok,"competitor_result":comp_parsed,"competitor_stderr":[r["stderr"] for r in comp_results],
        "competitor_codes":sorted(comp_codes),
        "mx_tool":case["mx_tool"],"mx_query":case["mx_query"],"mx_error":mx_error,
        "mx_adoption":adoption,"mx_item_count":mx_items,"mx_codes":sorted(mx_codes),
        "mx_result":mx_parsed,"mx_raw":mx_resp,
        "competitor_field_hits":comp_hits,"competitor_field_coverage":comp_field_coverage,
        "mx_field_hits":mx_hits,"mx_field_coverage":mx_field_coverage,
        "code_overlap":overlap,
        "status": (
            "mx_error" if mx_error else
            "mx_empty" if (mx_items <= 0 and not mx_codes) else
            "condition_rejected" if (case["mx_tool"] == "mx_stocks_screener" and adoption == "不采用") else
            "equivalent" if comp_ok and (mx_field_coverage or 0) >= 0.8 and (overlap is None or overlap >= 0.8) else
            "partial" if comp_ok and ((mx_field_coverage or 0) >= 0.5 or (overlap or 0) >= 0.5) else
            "unsupported"
        )
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--limit",type=int,default=0); ap.add_argument("--workers",type=int,default=4); ap.add_argument("--resume",action="store_true"); ap.add_argument("--only-skill")
    args=ap.parse_args(); OUT.mkdir(parents=True,exist_ok=True)
    cases=all_cases()
    if args.only_skill: cases=[c for c in cases if c["skill"]==args.only_skill]
    if args.limit: cases=cases[:args.limit]
    (OUT/"cases.jsonl").write_text("\n".join(json.dumps(c,ensure_ascii=False) for c in cases)+"\n",encoding="utf-8")
    initialize(session_headers()); headers=session_headers()
    results=[]; raw_path=OUT/"results.jsonl"
    if args.resume and raw_path.exists():
        done={json.loads(x)["case_id"] for x in raw_path.read_text(encoding="utf-8").splitlines() if x.strip()}
        results=[json.loads(x) for x in raw_path.read_text(encoding="utf-8").splitlines() if x.strip()]
        cases=[c for c in cases if c["case_id"] not in done]
    with ThreadPoolExecutor(max_workers=max(1,args.workers)) as ex:
        futs={ex.submit(run_case,c,headers):c for c in cases}
        for n,f in enumerate(as_completed(futs),1):
            c=futs[f]
            try: r=f.result()
            except Exception as exc: r={"case_id":c["case_id"],"skill":c["skill"],"question":c["question"],"status":"harness_error","error":f"{type(exc).__name__}: {exc}"}
            results.append(r); print(f"[{n}/{len(cases)}] {r['case_id']} {r['status']}",flush=True)
    results.sort(key=lambda x:x["case_id"])
    raw_path.write_text("\n".join(json.dumps(r,ensure_ascii=False) for r in results)+"\n",encoding="utf-8")
    rows=[]
    for r in results:
        rows.append({"case_id":r["case_id"],"skill":r["skill"],"question":r["question"],"status":r["status"],"competitor_ok":r.get("competitor_ok"),"mx_adoption":r.get("mx_adoption",""),"mx_item_count":r.get("mx_item_count",0),"competitor_field_coverage":r.get("competitor_field_coverage"),"mx_field_coverage":r.get("mx_field_coverage"),"code_overlap":r.get("code_overlap"),"competitor_field_hits":"|".join(r.get("competitor_field_hits",[])),"mx_field_hits":"|".join(r.get("mx_field_hits",[])),"required_fields":"|".join(r.get("required_fields",[])),"mx_tool":r.get("mx_tool",""),"mx_error":r.get("mx_error","")})
    with (OUT/"summary.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"DONE cases={len(results)} raw={raw_path} summary={OUT/'summary.csv'}")

if __name__=="__main__":
    main()