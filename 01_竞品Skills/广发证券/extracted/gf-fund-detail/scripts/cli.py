#!/usr/bin/env python3
"""广发证券基金详情 CLI —— 查询单只基金的完整档案。

通过 jijin_info / finance-api_product_fund_detail_get 获取：基金代码/全名/简称、
类型、风险等级、最新净值、各阶段收益率、资产规模、管理公司、成立日期、状态、
是否可申购赎回、最低认购/申购金额、投资目标、风险收益特征、综合评价等。

用法示例：
    python scripts/cli.py --code 519002
    python scripts/cli.py --trade-code 001643 --raw
    python scripts/cli.py --json '{"tradeCode":"519002"}'

env 依赖：
    GF_SKILLS_APIKEY 优先，其次 ~/.gf-skills/apikey（缺失时去
    https://hd.gf.com.cn/skills-market?channel=ytjskills 注册获取）。
"""

from __future__ import annotations

import argparse
import sys
import os

# 作为被智能体调用的 skill，不在 skill 目录里落字节码缓存（__pycache__）
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gf_client

SERVICE = "jijin_info"
TOOL = "finance-api_product_fund_detail_get"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="查询单只基金详情（净值/收益率/风险等级/申赎规则/管理公司/综合评价）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：python scripts/cli.py --code 519002\n"
        "      python scripts/cli.py --json '{\"tradeCode\":\"519002\"}'",
    )
    parser.add_argument(
        "--code",
        "--trade-code",
        dest="tradeCode",
        help="基金交易代码（必填），如 519002、001643。",
    )
    parser.add_argument(
        "--json",
        dest="json_args",
        metavar="JSON",
        help="直接传完整 args 的 JSON 对象（参数多/含嵌套时用），如 '{\"tradeCode\":\"519002\"}'。"
        "与命名参数可同时用，命名参数覆盖 JSON 同名字段。",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="打印完整网关响应（默认只打印业务数据 data.data）。",
    )
    args = parser.parse_args()

    base = gf_client.parse_json_arg(args.json_args)

    override = {}
    if args.tradeCode is not None:
        override["tradeCode"] = args.tradeCode.strip()

    merged = gf_client.merge_args(base, override)

    if not merged.get("tradeCode"):
        parser.error("缺少必填参数 tradeCode（用命名参数 --code 或 --json 提供）")

    gf_client.run(SERVICE, TOOL, merged, raw=args.raw)


if __name__ == "__main__":
    main()
