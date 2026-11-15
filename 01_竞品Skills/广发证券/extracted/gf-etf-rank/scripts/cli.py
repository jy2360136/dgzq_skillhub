#!/usr/bin/env python3
"""广发证券 ETF 榜单 CLI —— ETF 涨幅 / 跌幅 / 换手 / 主力资金净流入 / 净申购 / 溢价率排名。

用途：查 ETF 各类「排名榜 / 前 N 名」（含主力资金净流入榜 type=4），用于看市场热点、
资金偏好、龙头 ETF。注意：这是「排名榜」，不是「资金异动方向（大幅/持续 流入流出）」，
那是另一个 skill gf-etf-super-fund。

一行示例：
    python scripts/cli.py --type 4 --size 20

更多示例：
    python scripts/cli.py --type 1               # 涨幅榜
    python scripts/cli.py --type 3 --same-index-filter 1   # 换手榜，同指数只留 1 只
    python scripts/cli.py --type 1 --continue-rise-limit 3  # 连涨 ≥3 天的涨幅榜
    python scripts/cli.py --json '{"type":4,"size":20}'     # 直接传完整 JSON

env 依赖：GF_SKILLS_APIKEY（或 ~/.gf-skills/apikey）。缺失时去
https://hd.gf.com.cn/skills-market?channel=ytjskills 注册获取，gf_client 会给出引导。
"""

from __future__ import annotations

import argparse
import sys
import os

# 作为被智能体调用的 skill，不在 skill 目录里落字节码缓存（__pycache__）
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gf_client

SERVICE = "etf_rank"
TOOL = "finance-api_product_etf_rank_get"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="广发证券 ETF 榜单：涨幅/跌幅/换手/主力资金净流入/净申购/溢价率 排名。",
        epilog="示例：--type 4 --size 20 | --json '{\"type\":4,\"size\":20}'",
    )
    parser.add_argument(
        "--type",
        type=int,
        choices=[1, 2, 3, 4, 12, 13],
        help="榜单类型（必填，可由 --json 提供）：1=涨幅 2=跌幅 3=换手 4=主力资金净流入 12=净申购 13=溢价率",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=None,
        help="每页条数，默认 20",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=None,
        help="页码，从 0 开始，默认 0",
    )
    parser.add_argument(
        "--same-index-filter",
        type=int,
        dest="sameIndexFilter",
        choices=[0, 1],
        help="同指数 ETF 只展示 1 只：1=开启 0=关闭",
    )
    parser.add_argument(
        "--continue-rise-limit",
        type=int,
        dest="continueRiseLimit",
        help="连涨/连跌天数过滤（仅返回连涨/连跌 ≥ 该值的 ETF）",
    )
    parser.add_argument(
        "--json",
        dest="json_args",
        metavar="JSON",
        help="直接传完整 args 的 JSON 对象（参数多/含嵌套时用），如 '{\"type\":4,\"size\":20}'。"
             "与命名参数可同时用，命名参数覆盖 JSON 同名字段。",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="打印网关完整响应（默认只打印业务数据 data.data）",
    )
    args = parser.parse_args()

    # base 来自 --json；override 只含用户显式给了的命名参数（None 不放）。
    base = gf_client.parse_json_arg(args.json_args)
    override: dict = {}
    if args.type is not None:
        override["type"] = args.type
    if args.size is not None:
        override["size"] = args.size
    if args.page is not None:
        override["page"] = args.page
    if args.sameIndexFilter is not None:
        override["sameIndexFilter"] = args.sameIndexFilter
    if args.continueRiseLimit is not None:
        override["continueRiseLimit"] = args.continueRiseLimit

    merged = gf_client.merge_args(base, override)

    # 默认值兜底：仅当 json 与命名参数都没给时才生效。
    if "size" not in merged:
        merged["size"] = 20
    if "page" not in merged:
        merged["page"] = 0

    # 必填键校验（合并后）。
    if "type" not in merged or merged["type"] is None:
        parser.error("缺少必填参数 type（用 --type 或 --json 提供）")
    try:
        merged["type"] = int(merged["type"])
    except (TypeError, ValueError):
        parser.error("type 必须为整数，且取值 1/2/3/4/12/13")
    if merged["type"] not in (1, 2, 3, 4, 12, 13):
        parser.error("type 取值非法，只能是 1/2/3/4/12/13")

    gf_client.run(SERVICE, TOOL, merged, raw=args.raw)


if __name__ == "__main__":
    main()
