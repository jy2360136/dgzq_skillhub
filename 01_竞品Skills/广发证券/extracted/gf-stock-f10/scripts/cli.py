#!/usr/bin/env python3
"""广发证券股票 F10 基础信息 CLI。

用途：查询 A 股个股 F10 基础资料 —— 公司全称、板块、上市日期、主营业务范围、所属行业。
底层走 GF Skills 统一入口（service_name=wechat_f10, tool_name=f10_basic_post），
LLM 不要手写 curl，直接调本 CLI。

一行示例：
    python scripts/cli.py --code 000776 --market SZ
    python scripts/cli.py --json '{"code":"000776","market":"SZ"}'

env 依赖：
    GF_SKILLS_APIKEY 优先，其次 ~/.gf-skills/apikey（去 https://hd.gf.com.cn/skills-market?channel=ytjskills 获取）。
"""

from __future__ import annotations

import argparse
import sys
import os

# 作为被智能体调用的 skill，不在 skill 目录里落字节码缓存（__pycache__）
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gf_client

SERVICE = "wechat_f10"
TOOL = "f10_basic_post"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="查询股票 F10 基础信息（公司全称 / 板块 / 上市日期 / 主营业务 / 所属行业）。",
        epilog="示例：python scripts/cli.py --code 000776 --market SZ\n"
        "      python scripts/cli.py --json '{\"code\":\"000776\",\"market\":\"SZ\"}'",
    )
    parser.add_argument(
        "--code",
        help="证券代码，纯数字，如 000776",
    )
    parser.add_argument(
        "--market",
        type=lambda s: s.strip().upper(),
        choices=["SH", "SZ"],
        help="市场（自动转大写）：SH=上海 / SZ=深圳",
    )
    parser.add_argument(
        "--json",
        dest="json_args",
        metavar="JSON",
        help="直接传完整 args 的 JSON 对象（参数多/含嵌套时用），如 '{\"code\":\"000776\",\"market\":\"SZ\"}'。"
        "与命名参数可同时用，命名参数覆盖 JSON 同名字段。",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="打印整个网关响应（默认只打印业务数据 data.data）",
    )
    args = parser.parse_args()

    base = gf_client.parse_json_arg(args.json_args)

    # 命名参数路径：保留原有规整（code 去空格，market 已由 type 去空格+大写+choices 校验）。
    override = {}
    if args.code is not None:
        override["code"] = args.code.strip()
    if args.market is not None:
        override["market"] = args.market

    merged = gf_client.merge_args(base, override)

    # 必填键校验（合并后）。
    missing = [k for k in ("code", "market") if not merged.get(k)]
    if missing:
        parser.error(
            "缺少必填参数 " + ", ".join(missing) + "（用命名参数或 --json 提供）"
        )

    # 走 --json 路径的 market 轻量校验：非 SH/SZ 仅提示，不强行报错或改写。
    json_market = base.get("market")
    if args.market is None and isinstance(json_market, str) and json_market.upper() not in ("SH", "SZ"):
        sys.stderr.write(
            f"WARNING: --json 中 market='{json_market}' 不是 SH/SZ，已原样传给接口。\n"
        )

    gf_client.run(SERVICE, TOOL, merged, raw=args.raw)


if __name__ == "__main__":
    main()
