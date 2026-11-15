#!/usr/bin/env python3
"""
盘口异动查询 CLI

查询沪深京市场个股的实时盘口异动数据，支持 20 种异动类型、多维度筛选
（市场、异动类型、板块、自选股）、分页查询。基于 Python 3 标准库实现。
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Optional, Union

API_URL = "https://skillhub.csc108.com/api/skillhub/v1/api/quote/mi/pankou/query"
# 请求头：标识调用方为 AI Agent（鉴权头在调用时动态追加）
BASE_REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "http_agent": "ai-agent",
    "X-Calling-Skill-Id": "csc-pankou",
}
API_KEY_HEADER = "X-API-Key"
API_KEY_ENV_VAR = "CSC_API_KEY"
API_KEY_APPLY_URL = "https://skillhub.csc108.com/finly/?channelCode=workbuddy"
DEFAULT_START = "-1"
DEFAULT_COUNT = "20"
DEFAULT_FORWARD = 1
DEFAULT_TIMEOUT = 30

TYPE_MAP = {
    "11": "主力买入", "12": "主力卖出",
    "21": "加速拉升", "22": "加速下跌",
    "31": "高位回落", "32": "低位反弹",
    "41": "撑杆跳高", "42": "平台跳水",
    "51": "单笔冲涨", "52": "单笔冲跌",
    "61": "区间放量(涨)", "62": "区间放量(跌)", "63": "区间放量(平)",
    "71": "封涨停板", "72": "封跌停板", "73": "封涨大减",
    "74": "封跌大减", "75": "打开涨停", "76": "打开跌停",
    "81": "盘中弱势", "82": "盘中强势",
}

MARKET_MAP = {"sh": "上海", "sz": "深圳", "bz": "北证"}

VALID_TYPES = {str(i) for i in range(11, 83)}


class PankouAPIError(Exception):
    """API 错误异常类"""

    def __init__(self, message: str, status_code: Optional[int] = None,
                 response: Union[str, dict, None] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


def _build_headers(api_key: str) -> dict:
    """构建请求头：基础头 + API Key 鉴权头（不在任何输出中回显 Key 值）。"""
    headers = dict(BASE_REQUEST_HEADERS)
    headers[API_KEY_HEADER] = api_key
    return headers


def query_pankou(
    api_key: str,
    start: str = DEFAULT_START,
    count: str = DEFAULT_COUNT,
    forward: int = DEFAULT_FORWARD,
    types: Optional[list] = None,
    stocks: Optional[list] = None,
    blocks: Optional[list] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    """查询盘口异动数据。

    Args:
        api_key: API Key（CLI --api-key 传入，放入 X-API-Key 请求头）
        start: 查询定位索引，"-1"=最新，其他值=指定序号
        count: 查询条数
        forward: 1=向前查询
        types: 异动类型编码列表，如 ["11","21"]
        stocks: 自选股列表，如 ["600600.sh","000001.sz"]
        blocks: 板块列表，如 ["融资融券","沪深300"]
        timeout: 请求超时秒数

    Returns:
        包含 success、query_params、data 的字典
    """
    params = {
        "start": start,
        "count": count,
        "forward": forward,
    }
    if types:
        params["types"] = types
    if stocks:
        params["stocks"] = stocks
    if blocks:
        params["blocks"] = blocks

    payload = {"cmd": "query.rq", "params": params}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers=_build_headers(api_key),
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            response_body = resp.read().decode("utf-8")

            if not response_body.strip():
                return {
                    "success": False,
                    "error": "API 返回空响应",
                    "query_params": _build_query_params(start, count, forward,
                                                        types, stocks, blocks),
                }

            result = json.loads(response_body)
            items = result.get("data", [])
            enriched = [_enrich_item(item) for item in items]

            return {
                "success": True,
                "status_code": resp.status,
                "query_params": _build_query_params(start, count, forward,
                                                    types, stocks, blocks),
                "date": result.get("date", ""),
                "total": len(enriched),
                "data": enriched,
            }

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise PankouAPIError(
            f"HTTP 错误 {e.code}: {e.reason}",
            status_code=e.code,
            response=error_body,
        )
    except urllib.error.URLError as e:
        raise PankouAPIError(f"网络错误: {e.reason}")
    except json.JSONDecodeError as e:
        raise PankouAPIError(f"响应 JSON 解析失败: {e}")


def _enrich_item(item: dict) -> dict:
    """为异动记录补充中文名称。"""
    item["type_name"] = TYPE_MAP.get(item.get("type", ""), "未知类型")
    item["market_name"] = MARKET_MAP.get(item.get("market", ""), "未知市场")
    return item


def _build_query_params(start: str, count: str, forward: int,
                        types: Optional[list], stocks: Optional[list],
                        blocks: Optional[list]) -> dict:
    """构建查询参数上下文（含中文名称映射）。"""
    params = {
        "start": start,
        "count": count,
        "forward": forward,
    }
    if types:
        params["types"] = types
        params["type_names"] = [TYPE_MAP.get(t, f"未知({t})") for t in types]
    if stocks:
        params["stocks"] = stocks
    if blocks:
        params["blocks"] = blocks
    return params


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="盘口异动查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY"
  python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --count "7"
  python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --types "11" --count "10"
  python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --types "71,75" --count "20"
  python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --blocks "融资融券" --count "10"
  python3 scripts/csc_pankou.py --api-key "$CSC_API_KEY" --stocks "600600.sh,000001.sz" --count "10"

types 取值:
  11=主力买入  12=主力卖出  21=加速拉升  22=加速下跌
  31=高位回落  32=低位反弹  41=撑杆跳高  42=平台跳水
  51=单笔冲涨  52=单笔冲跌  61=区间放量(涨) 62=区间放量(跌) 63=区间放量(平)
  71=封涨停板  72=封跌停板  73=封涨大减  74=封跌大减
  75=打开涨停  76=打开跌停  81=盘中弱势  82=盘中强势
        """
    )
    parser.add_argument(
        "--api-key", type=str, default=None,
        metavar="API_KEY",
        help=f"API Key（放入请求头 {API_KEY_HEADER}）；未提供时回退读取环境变量 "
             f"{API_KEY_ENV_VAR}。调用时请勿在输出中回显真实 Key 值"
    )
    parser.add_argument(
        "--start", type=str, default=DEFAULT_START,
        help=f"查询起始索引，-1=最新 (默认: {DEFAULT_START})"
    )
    parser.add_argument(
        "--count", type=str, default=DEFAULT_COUNT,
        help=f"查询条数 (默认: {DEFAULT_COUNT})"
    )
    parser.add_argument(
        "--forward", type=str, default=str(DEFAULT_FORWARD),
        choices=["0", "1"],
        help=f"是否向前查询: 1=向前 (默认: {DEFAULT_FORWARD})"
    )
    parser.add_argument(
        "--types", type=str, default=None,
        help="异动类型编码，逗号分隔，如 \"11,21\""
    )
    parser.add_argument(
        "--stocks", type=str, default=None,
        help="自选股，逗号分隔，如 \"600600.sh,000001.sz\""
    )
    parser.add_argument(
        "--blocks", type=str, default=None,
        help="板块，逗号分隔，如 \"融资融券,沪深300\""
    )
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT,
        help=f"请求超时秒数 (默认: {DEFAULT_TIMEOUT})"
    )

    args = parser.parse_args()

    try:
        int(args.start)
    except ValueError:
        parser.error(f"--start 必须为整数，当前值: {args.start}")

    try:
        count_int = int(args.count)
        if count_int < 1:
            parser.error(f"--count 必须为正整数，当前值: {args.count}")
    except ValueError:
        parser.error(f"--count 必须为正整数，当前值: {args.count}")

    if args.types:
        type_list = [t.strip() for t in args.types.split(",") if t.strip()]
        for t in type_list:
            if t not in VALID_TYPES:
                parser.error(f"--types 包含无效类型编码: {t}，有效范围 11-82")
        args.types = type_list
    else:
        args.types = None

    if args.stocks:
        args.stocks = [s.strip() for s in args.stocks.split(",") if s.strip()]
    else:
        args.stocks = None

    if args.blocks:
        args.blocks = [b.strip() for b in args.blocks.split(",") if b.strip()]
    else:
        args.blocks = None

    return args


def main():
    args = parse_args()

    api_key = args.api_key or os.environ.get(API_KEY_ENV_VAR)
    if not api_key:
        print(json.dumps({
            "error": f"缺少 API Key：未通过 --api-key 传入，且环境变量 "
                     f"{API_KEY_ENV_VAR} 未配置，已终止本次调用",
            "guidance": f"您好,需要 API Key 才能使用本功能。请前往 {API_KEY_APPLY_URL} "
                        f"申请并配置 API Key 后重试。可将 Key 配置到环境变量 "
                        f"{API_KEY_ENV_VAR}（如写入 ~/.bashrc），再通过 "
                        f"--api-key \"$CSC_API_KEY\" 传入。",
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    try:
        result = query_pankou(
            api_key=api_key,
            start=args.start,
            count=args.count,
            forward=int(args.forward),
            types=args.types,
            stocks=args.stocks,
            blocks=args.blocks,
            timeout=args.timeout,
        )

        if result.get("success"):
            items = result.get("data", [])
            output = {
                "success": True,
                "query_params": result["query_params"],
                "date": result.get("date", ""),
                "total": len(items),
                "data": items,
            }

            if not items:
                output["empty_data_tip"] = (
                    "当前无符合条件的盘口异动数据。"
                    "建议去掉异动类型筛选 或 扩大查询条数 (--count) 后重试。"
                )

            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)

    except PankouAPIError as e:
        error_output = {"error": e.message}
        if e.status_code is not None:
            error_output["status_code"] = e.status_code
        if isinstance(e.response, str) and e.response.strip():
            error_output["response"] = e.response[:500]
        print(json.dumps(error_output, ensure_ascii=False, indent=2))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n操作已取消。", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(json.dumps({"error": f"发生错误: {str(e)}"}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
