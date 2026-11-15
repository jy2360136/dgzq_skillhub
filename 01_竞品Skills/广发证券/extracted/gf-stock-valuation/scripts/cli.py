#!/usr/bin/env python3
"""gf-stock-valuation CLI —— 广发证券股票市值估值对比 + 财务指标对比。

两个工具用子命令区分：
  valuation / basic ：多只股票总市值、PE/PB、行业均值、估值百分位（quant/common_basic_post）
  compare           ：两只股票财务指标横向对比（quant/compare_indicator_post）

一行示例：
  python scripts/cli.py valuation SZ000776 SH600000
  python scripts/cli.py compare --codes SZ000783 SZ000776 --year 2025 --report-type 9
  python scripts/cli.py valuation --json '{"stock_codes":["SZ000776","SH600000"]}'
  python scripts/cli.py compare --json '{"stock_codes":["SZ000783","SZ000776"],"year":"2025","report_type":9}'

股票代码：带交易所前缀大写，上海 SH / 深圳 SZ，如 SZ000776、SH600000（CLI 自动大写去空格）。

参数多 / 含嵌套时也可整段传 --json '<args 的 JSON 对象>'；与命名参数同时用时命名参数覆盖 JSON。

env 依赖：GF_SKILLS_APIKEY 优先，其次 ~/.gf-skills/apikey
         （缺失时去 https://hd.gf.com.cn/skills-market?channel=ytjskills 注册）。
"""

from __future__ import annotations

import argparse
import sys
import os

# 作为被智能体调用的 skill，不在 skill 目录里落字节码缓存（__pycache__）
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gf_client

SERVICE = "quant"
TOOL_VALUATION = "common_basic_post"
TOOL_COMPARE = "compare_indicator_post"

_JSON_HELP = (
    "直接传完整 args 的 JSON 对象（参数多/含嵌套时用），如 '{\"...\":...}'。"
    "与命名参数可同时用，命名参数覆盖 JSON 同名字段。"
)


def _norm_codes(codes):
    """股票代码规整：去空格、大写、去空项。"""
    return [c.strip().upper() for c in codes if c and c.strip()]


def cmd_valuation(args, parser):
    base = gf_client.parse_json_arg(args.json_args)

    override = {}
    if args.codes:
        override["stock_codes"] = _norm_codes(args.codes)

    merged = gf_client.merge_args(base, override)

    # --json 路径也大写一遍 code，避免漏网。
    if isinstance(merged.get("stock_codes"), list):
        merged["stock_codes"] = _norm_codes(merged["stock_codes"])

    codes = merged.get("stock_codes")
    if not isinstance(codes, list) or not codes:
        parser.error("缺少必填参数 stock_codes（非空数组，用命名参数/位置参数或 --json 提供）")

    gf_client.run(SERVICE, TOOL_VALUATION, merged, raw=args.raw)


def cmd_compare(args, parser):
    base = gf_client.parse_json_arg(args.json_args)

    override = {}
    if args.codes:
        override["stock_codes"] = _norm_codes(args.codes)
    if args.year is not None:
        override["year"] = args.year
    if args.report_type is not None:
        override["report_type"] = args.report_type

    merged = gf_client.merge_args(base, override)

    # --json 路径也大写一遍 code，避免漏网。
    if isinstance(merged.get("stock_codes"), list):
        merged["stock_codes"] = _norm_codes(merged["stock_codes"])

    codes = merged.get("stock_codes")
    if not isinstance(codes, list) or len(codes) != 2:
        parser.error("缺少/错误的 stock_codes：财务对比恰好需要两只股票代码（用命名参数或 --json 提供）")
    if not merged.get("year"):
        parser.error('缺少必填参数 year（如 "2025"，用命名参数或 --json 提供）')
    report_type = merged.get("report_type")
    try:
        report_type_int = int(report_type)
    except (TypeError, ValueError):
        report_type_int = None
    if report_type_int not in (1, 6, 9, 12):
        parser.error("缺少/错误的 report_type（须为 1/6/9/12，用命名参数或 --json 提供）")
    merged["report_type"] = report_type_int

    gf_client.run(SERVICE, TOOL_COMPARE, merged, raw=args.raw)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="广发证券股票市值估值对比 + 财务指标对比",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # 工具 1：市值估值对比
    p_val = sub.add_parser(
        "valuation",
        aliases=["basic"],
        help="多只股票总市值、PE/PB、行业均值、估值百分位",
    )
    p_val.add_argument(
        "codes",
        nargs="*",
        help="股票代码（带前缀大写，如 SZ000776 SH600000），也可用 --codes 传",
    )
    p_val.add_argument(
        "--codes",
        dest="codes",
        nargs="+",
        help="股票代码列表（与位置参数二选一）",
    )
    p_val.add_argument("--json", dest="json_args", metavar="JSON", help=_JSON_HELP)
    p_val.add_argument("--raw", action="store_true", help="打印完整网关响应（含 retcode 包裹）")
    p_val.set_defaults(func=cmd_valuation)

    # 工具 2：财务指标对比
    p_cmp = sub.add_parser(
        "compare",
        help="两只股票 ROE/净利率/现金流/负债率/成长性等财务指标对比",
    )
    p_cmp.add_argument(
        "--codes",
        nargs="+",
        help="恰好两只股票代码（带前缀大写，如 SZ000783 SZ000776）",
    )
    p_cmp.add_argument("--year", help='报告年份，如 "2025"')
    p_cmp.add_argument(
        "--report-type",
        dest="report_type",
        type=int,
        choices=[1, 6, 9, 12],
        help="报告期：1=一季报 6=中报 9=三季报 12=年报",
    )
    p_cmp.add_argument("--json", dest="json_args", metavar="JSON", help=_JSON_HELP)
    p_cmp.add_argument("--raw", action="store_true", help="打印完整网关响应（含 retcode 包裹）")
    p_cmp.set_defaults(func=cmd_compare)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args, parser)


if __name__ == "__main__":
    main()
