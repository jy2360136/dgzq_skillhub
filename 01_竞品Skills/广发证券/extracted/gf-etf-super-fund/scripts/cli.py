#!/usr/bin/env python3
"""广发证券 ETF 超级资金异动 CLI。

查询发生「大幅流入 / 大幅流出 / 持续流入 / 持续流出」超级资金异动的 ETF 列表
及近 14 日资金明细。一次只查一种异动方向。

用途：跟踪 ETF 资金异动方向、观察市场情绪、识别资金抢筹 / 出逃的 ETF。
注意：这是「资金异动方向」，不是「排名榜 / 前 N 名」（含主力资金净流入榜，
那是 gf-etf-rank 的 type=4）。

一行示例：
    python scripts/cli.py --type 持续流入
    python scripts/cli.py --type 大幅流出 --raw
    python scripts/cli.py --json '{"type":"持续流入"}'

env 依赖：GF_SKILLS_APIKEY 优先，其次 ~/.gf-skills/apikey
（缺失时去 https://hd.gf.com.cn/skills-market?channel=ytjskills 注册，写入后自动复用）。
"""

from __future__ import annotations

import argparse
import sys
import os

# 作为被智能体调用的 skill，不在 skill 目录里落字节码缓存（__pycache__）
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gf_client

SERVICE = "etf-super-fund"
TOOL = "gfmiddle_eits_super_fund_etf_superfund_get"
TYPES = ["大幅流入", "大幅流出", "持续流入", "持续流出"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="广发证券 ETF 超级资金异动：查询某一资金异动方向的 ETF 列表 + 近 14 日明细。",
        epilog="示例：python scripts/cli.py --type 持续流入；"
        "或 python scripts/cli.py --json '{\"type\":\"持续流入\"}'",
    )
    parser.add_argument(
        "--type",
        choices=TYPES,
        help="资金异动方向（必填，固定值）：大幅流入 / 大幅流出 / 持续流入 / 持续流出。一次只查一种。",
    )
    parser.add_argument(
        "--json",
        dest="json_args",
        metavar="JSON",
        help="直接传完整 args 的 JSON 对象（参数多/含嵌套时用），如 '{\"type\":\"持续流入\"}'。"
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
    if args.type is not None:
        override["type"] = args.type
    merged = gf_client.merge_args(base, override)

    if "type" not in merged or merged["type"] is None:
        parser.error("缺少必填参数 type（用命名参数 --type 或 --json 提供）")
    if merged["type"] not in TYPES:
        parser.error(
            "type 取值非法：%r，必须是 %s 之一" % (merged["type"], " / ".join(TYPES))
        )

    gf_client.run(SERVICE, TOOL, merged, raw=args.raw)


if __name__ == "__main__":
    main()
