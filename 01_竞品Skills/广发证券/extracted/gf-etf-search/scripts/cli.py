#!/usr/bin/env python3
"""广发证券 ETF 多维度筛选 CLI（service_name=etf_search）。

按收益率 / 回撤 / 夏普 / 估值温度 / 规模 / 赛道 / 交易属性等条件筛选 ETF，
构建候选池。LLM 调本脚本而不是手写 curl。

一行示例：
    python scripts/cli.py --trak-type 行业 --roc1m 5~ --sort -roc1m --limit 20 --add-real-time-roc 1

参数很多：常用条件给了独立 flags，其余任意参数用 `--arg KEY=VALUE`（可多次）透传；
也可整段传 `--json '{"trakType":"行业","roc1m":"5~","sort":"-roc1m","limit":20}'`。
合并顺序：--json 为底，--arg 覆盖其上，命名参数最终覆盖（命名参数优先）。
至少要传一个筛选条件（含来自 --json / --arg 的键），否则报错。

env 依赖：GF_SKILLS_APIKEY（或 ~/.gf-skills/apikey），缺失时去
https://hd.gf.com.cn/skills-market?channel=ytjskills 注册。
"""

from __future__ import annotations

import argparse
import sys
import os

# 作为被智能体调用的 skill，不在 skill 目录里落字节码缓存（__pycache__）
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gf_client  # noqa: E402

SERVICE = "etf_search"
TOOL = "finance_api_inclusive_etf_list_get"

# flag dest -> 接口 args key（仅列与 dest 名不同的；其余同名直接用）
DEST_TO_ARG = {
    "trak_type": "trakType",
    "one_trak_name": "oneTrakName",
    "trade_code": "tradeCode",
    "trade_t0": "tradeT0",
    "margin_trade": "marginTrade",
    "return1y": "return1y",
    "return3y": "return3y",
    "max_drawdown1y": "maxDrawdown1y",
    "sharp_ratio1y": "sharpRatio1y",
    "valuation_result": "valuationResult",
    "index_temp_type": "indexTempType",
    "asset_scale": "assetScale",
    "add_real_time_roc": "addRealTimeRoc",
}

# 这些 dest 与接口 key 同名（直接透传）
SAME_NAME = ["search", "type", "roc1m", "roc1y", "sort", "start", "limit"]


def _coerce(value: str):
    """纯整数串转 int，其余保留 str。"""
    s = value.strip()
    if s.lstrip("-").isdigit():
        try:
            return int(s)
        except ValueError:
            return s
    return s


def parse_arg_kv(pairs):
    """解析 --arg KEY=VALUE 列表为 dict，数字串转 int。"""
    out = {}
    for item in pairs or []:
        if "=" not in item:
            raise SystemExit(f"ERROR: --arg 需要 KEY=VALUE 形式，收到：{item!r}")
        k, v = item.split("=", 1)
        k = k.strip()
        if not k:
            raise SystemExit(f"ERROR: --arg 的 KEY 不能为空：{item!r}")
        out[k] = _coerce(v)
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="广发证券 ETF 多维度筛选（收益/回撤/夏普/估值温度/规模/赛道/交易属性）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "区间格式：5~ (≥5%)，~10 (≤10%)，0~20 (0~20%)。\n"
            "排序：sort 字段降序加 - 前缀，如 -roc1m。\n"
            "一次优先 2~4 个核心条件 + --limit，条件过多易无结果。\n"
            "示例：python scripts/cli.py --trak-type 行业 --roc1m 5~ --sort -roc1m --limit 20 --add-real-time-roc 1\n"
            "--json 示例：python scripts/cli.py --json '{\"trakType\":\"行业\",\"roc1m\":\"5~\",\"sort\":\"-roc1m\",\"limit\":20}'\n"
            "合并顺序：--json（底）→ --arg → 命名参数（顶，优先）。"
        ),
    )

    # 整段 JSON 入参（参数多 / 含嵌套时用），与命名参数 / --arg 可同时用
    p.add_argument("--json", dest="json_args", metavar="JSON",
                   help="直接传完整 args 的 JSON 对象，如 '{\"trakType\":\"行业\",\"roc1m\":\"5~\"}'。"
                        "与命名参数 / --arg 可同时用；合并顺序 --json→--arg→命名参数（命名参数优先）。")

    # 赛道 / 类型 / 搜索
    p.add_argument("--search", help="模糊搜索代码或名称")
    p.add_argument("--type", help="ETF 类型，如 股票ETF / 境外ETF")
    p.add_argument("--trak-type", dest="trak_type", help="赛道分类，如 宽基 / 行业")
    p.add_argument("--one-trak-name", dest="one_trak_name", help="一级赛道名称，如 科技")
    p.add_argument("--trade-code", dest="trade_code", help="交易代码，多个用逗号分隔")

    # 交易属性
    p.add_argument("--trade-t0", dest="trade_t0", type=int, choices=[0, 1], help="是否 T+0，1=是")
    p.add_argument("--margin-trade", dest="margin_trade", type=int, choices=[0, 1], help="是否两融，1=是")

    # 收益 / 涨跌幅 / 回撤 / 夏普（区间格式 5~ / ~10 / 0~20）
    p.add_argument("--roc1m", help="近 1 月涨跌幅区间，如 5~")
    p.add_argument("--roc1y", help="近 1 年涨跌幅区间")
    p.add_argument("--return1y", help="近 1 年收益率区间")
    p.add_argument("--return3y", help="近 3 年收益率区间")
    p.add_argument("--max-drawdown1y", dest="max_drawdown1y", help="近 1 年最大回撤区间，如 ~20")
    p.add_argument("--sharp-ratio1y", dest="sharp_ratio1y", help="近 1 年夏普比率区间")

    # 估值 / 温度 / 规模
    p.add_argument("--valuation-result", dest="valuation_result", type=int, choices=[1, 2, 3],
                   help="估值区：1 低位 / 2 中位 / 3 高位")
    p.add_argument("--index-temp-type", dest="index_temp_type", choices=["low", "ord", "high"],
                   help="指数温度：low / ord / high")
    p.add_argument("--asset-scale", dest="asset_scale", help="资产规模区间，如 50~")

    # 排序 / 分页 / 实时
    p.add_argument("--sort", help="排序字段，降序加 - 前缀，如 -roc1m")
    p.add_argument("--start", type=int, help="分页起始")
    p.add_argument("--limit", type=int, help="返回数量（默认 20）")
    p.add_argument("--add-real-time-roc", dest="add_real_time_roc", type=int, choices=[0, 1],
                   help="是否带实时涨跌幅，1=是")

    # 通用透传 + raw
    p.add_argument("--arg", action="append", metavar="KEY=VALUE",
                   help="透传任意接口参数，可多次，如 --arg roc6m=10~ --arg return6m=0~30")
    p.add_argument("--raw", action="store_true", help="打印完整网关响应而非 data.data")

    return p


def build_named_args(ns: argparse.Namespace) -> dict:
    """只收集「用户显式给了的命名参数」（值非 None），作为合并 override。

    不含 --arg / --json；规整逻辑（trade_code 去空格等）只作用于命名参数路径。
    """
    args: dict = {}

    for dest in SAME_NAME:
        val = getattr(ns, dest, None)
        if val is not None:
            args[dest] = val

    for dest, key in DEST_TO_ARG.items():
        val = getattr(ns, dest, None)
        if val is not None:
            v = val.strip() if isinstance(val, str) else val
            if dest == "trade_code" and isinstance(v, str):
                # 规整：去空格，保持逗号分隔
                v = ",".join(part.strip() for part in v.split(",") if part.strip())
            args[key] = v

    return args


# 取值可能以 - 开头（如 sort=-roc1m，区间 ~-5），argparse 会误判成选项。
# 把这些 flag 的 "--flag VALUE" 重写成 "--flag=VALUE"，让负值 / - 前缀正常透传。
_DASH_VALUE_FLAGS = {
    "--sort", "--roc1m", "--roc1y", "--return1y", "--return3y",
    "--max-drawdown1y", "--sharp-ratio1y", "--asset-scale", "--arg",
}


def _normalize_argv(argv):
    out = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok in _DASH_VALUE_FLAGS and i + 1 < len(argv):
            nxt = argv[i + 1]
            if nxt.startswith("-") and "=" not in tok:
                out.append(f"{tok}={nxt}")
                i += 2
                continue
        out.append(tok)
        i += 1
    return out


def main(argv=None) -> None:
    if argv is None:
        argv = sys.argv[1:]
    parser = build_parser()
    ns = parser.parse_args(_normalize_argv(argv))

    # 合并顺序：--json（底）→ --arg → 命名参数（顶，优先）
    args = gf_client.parse_json_arg(ns.json_args)
    args = gf_client.merge_args(args, parse_arg_kv(ns.arg))
    args = gf_client.merge_args(args, build_named_args(ns))

    # 默认 limit 兜底（未显式给且 --json 也没给时）
    if args.get("limit") is None:
        args["limit"] = 20

    # 在最终 merged 上重评：纯分页 / 仅排序 / 仅实时不算「筛选条件」
    filter_keys = {k for k in args if k not in ("limit", "start", "sort", "addRealTimeRoc")}
    if not filter_keys:
        parser.error(
            "至少需要一个筛选条件（如 --trak-type / --roc1m / --return1y / --valuation-result / "
            "--index-temp-type / --search 等，或用 --arg KEY=VALUE / --json 透传）。"
        )

    gf_client.run(SERVICE, TOOL, args, raw=ns.raw)


if __name__ == "__main__":
    main()
