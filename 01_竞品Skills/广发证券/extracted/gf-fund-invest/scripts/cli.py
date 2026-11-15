#!/usr/bin/env python3
"""广发证券基金定投计算器 CLI —— 历史区间定投回测（普通 / 均线 / 目标止盈 / 移动止盈等策略）。

封装统一入口 service_name=fund_invest, tool_name=finance_api_product_invest_compute_post，
LLM 用命名参数调用，不要手写 curl / JSON。

一行示例（命名参数）：
    python scripts/cli.py --code 001643 --balance 1000 --rate 0 \
        --start 20200101 --end 20250101 --en-fund-date 1 --strategy 0

整段 JSON 示例（参数多 / 含嵌套 strategyList 时用，命名参数覆盖 JSON 同名字段）：
    python scripts/cli.py --json '{"tradeCode":"001643","balance":1000,"rate":"0",
        "startDate":"20200101","endDate":"20250101","enFundDate":"1",
        "strategyList":[{"prodAIRationType":"0"}]}'

env 依赖：GF_SKILLS_APIKEY 优先，其次 ~/.gf-skills/apikey
（缺失时去 https://hd.gf.com.cn/skills-market?channel=ytjskills 获取，自动持久化复用）。
"""

from __future__ import annotations

import argparse
import sys
import os

# 作为被智能体调用的 skill，不在 skill 目录里落字节码缓存（__pycache__）
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gf_client

SERVICE = "fund_invest"
TOOL = "finance_api_product_invest_compute_post"

# 命名参数路径下用于组装单条 strategy 的可选字段。
STRATEGY_FIELDS = ("expectIncomeRatio", "backRate", "prodIndexType", "prodAverageType", "lockPeriod")


def norm_date(s: str) -> str:
    """接受 YYYYMMDD 或 YYYY-MM-DD，统一去掉 '-'。"""
    return s.replace("-", "").strip()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="广发证券基金定投回测计算器（单策略）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="也可整段传 JSON（含多策略 strategyList 数组）：\n"
               "  --json '{\"tradeCode\":\"001643\",\"balance\":1000,\"rate\":\"0\","
               "\"startDate\":\"20200101\",\"endDate\":\"20250101\","
               "\"strategyList\":[{\"prodAIRationType\":\"0\"}]}'\n"
               "命名参数与 --json 可同时用，命名参数覆盖 JSON 同名字段。",
    )
    p.add_argument("--code", dest="tradeCode", help="基金代码，如 001643")
    p.add_argument("--balance", type=float, help="每期定投金额（元）")
    p.add_argument("--start", dest="startDate", help="开始日期 YYYYMMDD 或 YYYY-MM-DD")
    p.add_argument("--end", dest="endDate", help="结束日期 YYYYMMDD 或 YYYY-MM-DD")
    p.add_argument(
        "--rate",
        choices=["0", "1", "2", "3"],
        help="扣款频率：0=每月 1=每周 2=每天 3=每双周",
    )
    p.add_argument("--en-fund-date", dest="enFundDate", help="扣款日，如 1（每月频率常用）")
    p.add_argument(
        "--strategy",
        type=int,
        default=None,
        choices=[0, 1, 2, 3, 4, 5],
        help="策略 prodAIRationType：0普通 1指数均线 2目标止盈 3移动止盈 4均线+目标止盈 5均线+移动止盈",
    )
    p.add_argument("--expect-income-ratio", dest="expectIncomeRatio",
                   help="止盈目标收益率（目标止盈类 2/4 必带），如 0.2")
    p.add_argument("--back-rate", dest="backRate",
                   help="移动止盈回撤比例（移动止盈类 3/5 必带），如 0.1")
    p.add_argument("--prod-index-type", dest="prodIndexType", help="参考指数 prodIndexType（均线类需带）")
    p.add_argument("--prod-average-type", dest="prodAverageType", help="均线类型 prodAverageType（均线类需带）")
    p.add_argument("--lock-period", dest="lockPeriod", help="止盈锁定期（月）lockPeriod")
    p.add_argument("--json", dest="json_args", metavar="JSON",
                   help="直接传完整 args 的 JSON 对象（参数多/含嵌套 strategyList 数组时用），"
                        "如 '{\"...\":...}'。与命名参数可同时用，命名参数覆盖 JSON 同名字段。")
    p.add_argument("--raw", action="store_true", help="打印整个网关包裹（默认只打印业务数据 data.data）")
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # base 来自 --json（可含多策略 strategyList 数组）。
    base: dict = gf_client.parse_json_arg(args.json_args)

    # 用户是否显式给了任一策略相关 flag。
    strategy_flags_given = args.strategy is not None or any(
        getattr(args, f) is not None for f in STRATEGY_FIELDS
    )

    # override 只放用户显式给的命名参数（值为 None 的不放）。
    override: dict = {}
    if args.tradeCode is not None:
        override["tradeCode"] = args.tradeCode.strip()
    if args.balance is not None:
        override["balance"] = args.balance
    if args.startDate is not None:
        override["startDate"] = norm_date(args.startDate)
    if args.endDate is not None:
        override["endDate"] = norm_date(args.endDate)
    if args.rate is not None:
        override["rate"] = args.rate
    if args.enFundDate is not None:
        override["enFundDate"] = args.enFundDate

    # 命名参数路径：当用户给了策略 flag，或 --json 没有提供 strategyList 时，
    # 从 flag 组装单条 strategy → strategyList=[strategy]。
    # 若 --json 已带 strategyList 且用户未显式给策略 flag，则尊重 --json，不覆盖。
    if strategy_flags_given or not base.get("strategyList"):
        strategy: dict = {"prodAIRationType": str(args.strategy if args.strategy is not None else 0)}
        for field in STRATEGY_FIELDS:
            val = getattr(args, field)
            if val is not None:
                strategy[field] = val
        override["strategyList"] = [strategy]

    merged: dict = gf_client.merge_args(base, override)

    # 合并后校验必填键。
    required = ("tradeCode", "balance", "rate", "startDate", "endDate", "strategyList")
    missing = [k for k in required if k not in merged or merged[k] in (None, "", [])]
    if missing:
        parser.error("缺少必填参数 %s（用命名参数或 --json 提供）" % "、".join(missing))
    if not isinstance(merged["strategyList"], list) or not merged["strategyList"]:
        parser.error("strategyList 必须是非空数组（用 --strategy 等命名参数或 --json 提供）")

    gf_client.run(SERVICE, TOOL, merged, raw=args.raw)


if __name__ == "__main__":
    main()
