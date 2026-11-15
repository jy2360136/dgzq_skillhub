#!/usr/bin/env python3
"""广发证券龙虎榜个股列表 CLI。

查询指定交易日、指定市场（沪/深）的龙虎榜异常交易上榜个股及上榜原因。

用法示例：
    python scripts/cli.py --date 20260313 --market sh
    python scripts/cli.py --date 20260313 --market sz --raw
    python scripts/cli.py --json '{"date":20260313,"market":"sh"}'

env 依赖：
    GF_SKILLS_APIKEY 优先，其次 ~/.gf-skills/apikey（缺失时去
    https://hd.gf.com.cn/skills-market?channel=ytjskills 注册获取，自动持久化）。

市场不明时分别用 --market sh 和 --market sz 各查一次。
"""

from __future__ import annotations

import argparse
import os
import sys

# 作为被智能体调用的 skill，不在 skill 目录里落字节码缓存（__pycache__）
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gf_client

SERVICE = "lhb"
TOOL = "lhb_aborttrade_market_date_get"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="查询指定交易日 + 市场的龙虎榜上榜个股和上榜原因。",
        epilog="示例：--json '{\"date\":20260313,\"market\":\"sh\"}'（与命名参数同用时命名参数覆盖 JSON）",
    )
    parser.add_argument(
        "--date",
        type=int,
        help="交易日，整数 YYYYMMDD，如 20260313（须为交易日）",
    )
    parser.add_argument(
        "--market",
        type=str.lower,
        choices=["sh", "sz"],
        help="市场（小写）：sh=上海 / sz=深圳。注意与 F10/估值的大写不同",
    )
    parser.add_argument(
        "--json",
        dest="json_args",
        metavar="JSON",
        help="直接传完整 args 的 JSON 对象（参数多/含嵌套时用），如 '{\"date\":...,\"market\":...}'。"
        "与命名参数可同时用，命名参数覆盖 JSON 同名字段。",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="打印完整网关响应（默认只打印业务数据 data.data）",
    )
    args = parser.parse_args()

    base = gf_client.parse_json_arg(args.json_args)

    # --json 路径：尊重用户给的原值，仅做轻量规整（数字字符串 date → int；market 字符串小写）。
    if "date" in base:
        d = base["date"]
        if isinstance(d, str) and d.strip().lstrip("-").isdigit():
            base["date"] = int(d)
    if "market" in base and isinstance(base["market"], str):
        base["market"] = base["market"].lower()

    # 命名参数路径：date 转 int、market 小写（type 已处理）。仅含用户显式给的值。
    override = {}
    if args.date is not None:
        override["date"] = int(args.date)
    if args.market is not None:
        override["market"] = args.market

    merged = gf_client.merge_args(base, override)

    # 合并后校验必填键
    missing = [k for k in ("date", "market") if k not in merged or merged[k] in (None, "")]
    if missing:
        parser.error(
            "缺少必填参数 %s（用命名参数或 --json 提供）" % "、".join(missing)
        )

    gf_client.run(
        SERVICE,
        TOOL,
        merged,
        raw=args.raw,
    )


if __name__ == "__main__":
    main()
