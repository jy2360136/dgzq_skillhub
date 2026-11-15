#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SkillHub MCP 直连取数 + 紧凑解析脚本（无 MCP 连接器依赖）。

普通用户只需配置环境变量 CSC_SKILLHUB_API_KEY 即可使用本 Skill，
无需安装/信任任何 MCP 连接器。脚本直接对 SkillHub 的 MCP HTTP 端点
发起标准 JSON-RPC 调用，自动完成 initialize -> tools/list -> tools/call 全流程。

默认输出**紧凑解析结果**（rich_text + nlu + 组件摘要），避免翼答动辄 11 万–22 万字符的
原始 SSE 撑爆工具输出上限而被落盘。

用法：
  # 1) 取数 + 紧凑解析（默认，推荐）
  python3 mcp_skillhub_call.py --server <server名> --slug <skill的slug> --question "<自然语言问题>"

  # 2) 原始返回（排查链路问题时用）
  python3 mcp_skillhub_call.py ... --raw

  # 3) 解析已落盘的 SSE 文件（不重新取数，重发只会再落一个盘）
  python3 mcp_skillhub_call.py --parse-file <落盘的 .txt 路径> [--max-rows 50]

可选参数：
  --max-rows N    组件 datas 最多输出 N 行（默认 50，0 = 不限）
  --max-text N    rich_text 最多输出 N 字符（默认 0 = 不限；设 8000 可显著减小输出体积）

依赖：仅 Python 标准库（urllib / json / argparse），无需 pip install。
"""
import json
import os
import re
import sys
import time
import random
import string
import urllib.request
import urllib.error
import argparse

# 基础地址；生产环境改 SKILLHUB_BASE_URL 或 data-source-config.md
DEFAULT_BASE = "https://skillhub.csc108.com/api/mcp/v1"
# 单次 HTTP 读超时（秒）。翼答为逐 token 流式生成，长回答可能超过 30s，故放宽。
DEFAULT_TIMEOUT = int(os.environ.get("CSC_SKILLHUB_TIMEOUT", "150"))


def _new_session_id():
    """每次调用生成独立 session_id，避免后端 session 卡死（resilience 经验：换 id 可恢复 30004/Connection closed）。"""
    return "wb-{}-{}{}".format(
        int(time.time() * 1000),
        os.getpid(),
        "".join(random.choices(string.ascii_lowercase + string.digits, k=6)),
    )


def _post(url, api_key, slug, body, timeout=None):
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    for h, v in [
        ("Content-Type", "application/json"),
        ("Accept", "application/json, text/event-stream"),
        ("X-API-Key", api_key),
        ("X-Calling-Skill-Id", slug),
    ]:
        req.add_header(h, v)
    r = urllib.request.urlopen(req, timeout=timeout)
    raw = r.read().decode("utf-8")
    out = []
    for ln in raw.splitlines():
        ln = ln.strip()
        if ln.startswith("data:"):
            try:
                out.append(json.loads(ln[5:].strip()))
            except Exception:
                pass
    if not out and raw.strip():
        try:
            out.append(json.loads(raw))
        except Exception:
            out.append({"_raw": raw[:500]})
    return out


# ---------------------------------------------------------------------------
# 解析层（结构层，与数据源无关；两种返回结构都兼容，勿回退成单一结构）
# ---------------------------------------------------------------------------

def _iter_events(sse_text):
    """把 SSE 文本拆成事件 dict 列表。

    兼容三种形态：
      1) 正常 SSE：多行 `data:{json}`
      2) SSE 分片：同一事件的 JSON 被拆到多行 `data:`，需缓冲拼接后解析
      3) 非 SSE：整段就是一个 JSON（含 answer_path / errcode）
    """
    events, buf = [], ""
    for ln in sse_text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("data:"):
            piece = ln[5:].strip()
            if not piece:
                continue
            try:
                events.append(json.loads(piece))
                buf = ""
            except Exception:
                # 可能是被拆行的同一 JSON：缓冲后重试
                buf = (buf + piece) if buf else piece
                try:
                    events.append(json.loads(buf))
                    buf = ""
                except Exception:
                    pass
        else:
            # 无 data: 前缀的行：可能是裸 JSON 或 SSE 的 event:/id: 行
            if ln.startswith("event:") or ln.startswith("id:") or ln.startswith(":"):
                continue
            try:
                events.append(json.loads(ln))
            except Exception:
                pass
    if not events and sse_text.strip():
        try:
            events.append(json.loads(sse_text.strip()))
        except Exception:
            pass
    return events


def _pick_components(section):
    """动态组件双结构兼容：优先 result_page.components[]，退化 answer_list[].components[]。

    ⚠️ 实测多数返回**没有** answer_list 中间层；只按 answer_list 写会解析到 0 个组件。
    """
    if not isinstance(section, dict):
        return []
    rp = section.get("result_page")
    if not isinstance(rp, dict):
        return []
    comps = rp.get("components")
    if isinstance(comps, list) and comps:
        return comps
    for al in (rp.get("answer_list") or []):
        if isinstance(al, dict):
            c = al.get("components")
            if isinstance(c, list) and c:
                return c
    return []


def _pick_row_count(comp):
    """组件的 row_count。

    ⚠️ **row_count 语义因组件类型而异，只对表格类组件才有"候选池总数"含义**：
      - 表格类（如 jgyXuanguTable1）曾测得 row_count=410（候选池总数）；
      - kline3 类实测 row_count=1 而 total_rows=66 —— **无候选池总数含义**。

    故本函数只做"取值"，**不做语义判断**（不聚合到顶层，避免被误当成候选池总数）；
    位置不稳定（data 顶层与 data.meta 内都出现过），两处都读。
    """
    data = comp.get("data") if isinstance(comp, dict) else None
    if not isinstance(data, dict):
        return None
    rc = data.get("row_count")
    if rc is None:
        meta = data.get("meta")
        if isinstance(meta, dict):
            rc = meta.get("row_count")
    return rc


# 被视为"逐点序列类"的组件类型：其 row_count 不表示候选池总数
_SERIES_TYPES = {"kline3", "kline", "bar3", "bar", "line", "line2", "area", "pie"}


def _is_empty_shell(show_type, total_rows):
    """空壳组件判据：组件存在但行数 ≤ 1，视为**数据不可得**。

    ⚠️ 实测（2026-09-23）"国证价值指数"返回 kline3 组件但只有 1 行 →
    若只判"有没有组件"会误认为拿到了数据。**组件存在 ≠ 数据可得。**
    """
    return total_rows <= 1


def _compact_components(events, max_rows):
    """收集全部动态组件，输出精简结构（列名 + datas 截断 + row_count + 可用性标记）。"""
    out = []
    for ev in events:
        sec = ev.get("section") if isinstance(ev, dict) else None
        for comp in _pick_components(sec):
            if not isinstance(comp, dict):
                continue
            data = comp.get("data") if isinstance(comp.get("data"), dict) else {}
            datas = data.get("datas")
            if not isinstance(datas, list):
                datas = []
            show_type = comp.get("show_type") or comp.get("type")
            rc = _pick_row_count(comp)
            item = {
                "show_type": show_type,
                "columns": data.get("columns"),
                "total_rows": len(datas),
                # 组件存在但为空壳 → usable=False，上层不得据此认为"拿到了数据"
                "usable": not _is_empty_shell(show_type, len(datas)),
                # row_count 仅对表格类组件有"候选池总数"含义；序列类需用 total_rows
                "row_count": rc,
                "row_count_meaning": ("候选池总数（表格类）"
                                      if rc is not None and show_type not in _SERIES_TYPES
                                      else ("非候选池总数（序列类，请用 total_rows）"
                                            if rc is not None else None)),
            }
            if max_rows and max_rows > 0:
                item["datas"] = datas[:max_rows]
                if len(datas) > max_rows:
                    item["datas_truncated"] = len(datas) - max_rows
            else:
                item["datas"] = datas
            out.append(item)
    return out


def parse_payload(payload, max_rows=50, max_text=0):
    """把 fetch() 的返回值解析成紧凑结果。

    payload 形态：
      {"raw": "<整段 SSE 文本>"}     —— 常见，必须先拆行剥 data: 再解析
      {"text": "<JSON 字符串>"}      —— 业务报错（如 30004）
      单个已解析 dict（含 answer_path）—— 少数情况
      {"error": {...}}              —— JSON-RPC 层错误
    """
    if not isinstance(payload, dict):
        payload = {"raw": str(payload)}

    if "error" in payload:
        return {"err": payload["error"], "sse_events": 0, "nlu": None,
                "rich_text": "", "rich_text_len": 0, "component_count": 0,
                "usable_component_count": 0, "structured_data_available": False,
                "components": []}

    sse_text = payload.get("raw")
    if sse_text is None:
        txt = payload.get("text")
        if txt is not None:
            # text 可能是 SSE 文本，也可能是业务错误 JSON 字符串
            sse_text = txt
        else:
            sse_text = json.dumps(payload, ensure_ascii=False)

    events = _iter_events(sse_text)

    # 业务错误（30004 等）：可能是解析出的事件里带 errcode，也可能整体就是错误 JSON
    err = None
    for ev in events:
        if isinstance(ev, dict) and ("errcode" in ev or "errmsg" in ev) and "answer_path" not in ev:
            err = {"errcode": ev.get("errcode"), "errmsg": ev.get("errmsg") or ev.get("message")}
            break
    if err is None and not events and isinstance(sse_text, str):
        s = sse_text.strip()
        if s.startswith("{") and ("errcode" in s or "30004" in s):
            try:
                err = json.loads(s)
            except Exception:
                err = {"errcode": "unparsed", "raw": s[:300]}

    # 散文正文 + NLU
    chunks, nlu = [], None
    for ev in events:
        if not isinstance(ev, dict):
            continue
        ap = ev.get("answer_path", "")
        sec = ev.get("section") or {}
        if ap == "logs/baseInfo":
            nlu = (ev.get("base_info") or {}).get("nlu")
        if ap == "other/openAnswer" and isinstance(sec, dict) and sec.get("rich_text"):
            chunks.append(sec["rich_text"])

    # rich_text 为逐 token 增量分片，含大量内容相同的 '0'/' '/'。' —— 只能拼接，
    # 绝不能按文本去重（去重会把 "0.8%" 变 ".%"，见 data-source-queries.md §五 红线）。
    rich_text = _strip_visual("".join(chunks))

    components = _compact_components(events, max_rows)
    usable = [c for c in components if c.get("usable")]

    if max_text and max_text > 0 and len(rich_text) > max_text:
        rich_text_out = rich_text[:max_text] + "\n…[已按 --max-text 截断，剩余 {} 字符]".format(
            len(rich_text) - max_text)
    else:
        rich_text_out = rich_text

    return {
        "err": err,
        "sse_events": len(events),
        "nlu": nlu,
        "rich_text": rich_text_out,
        "rich_text_len": len(rich_text),
        "component_count": len(components),
        # 可用组件数：排除空壳（存在但行数 ≤ 1，实测"国证价值"即该形态）
        "usable_component_count": len(usable),
        # 一句话结论：本轮是否真的拿到了结构化数据（供上层判降级）
        "structured_data_available": bool(usable),
        "components": components,
    }


def _strip_visual(text):
    """去掉 ```visual ... ``` 组件占位块，只留散文（注意实际写法常带空格：``` visual）。"""
    return re.sub(r"```\s*visual.*?```", "", text, flags=re.S)


def fetch(base, server, slug, question, api_key, source="b_zhengquan_zxjt", session_id=None):
    if session_id is None:
        session_id = _new_session_id()
    url = "{}/servers/{}/mcp".format(base.rstrip("/"), server)
    # 1. initialize
    _post(url, api_key, slug, {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                   "clientInfo": {"name": "skill-direct", "version": "1"}},
    })
    # 2. notifications/initialized
    _post(url, api_key, slug, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    # 3. tools/list -> 取工具名（server 一般只暴露一个 yida 入口工具）
    tl = _post(url, api_key, slug, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    tname = None
    for m in tl:
        if isinstance(m, dict) and "result" in m and "tools" in m["result"]:
            tools = m["result"]["tools"]
            if tools:
                tname = tools[0].get("name")
    if not tname:
        tname = "{}_tools_yida".format(server)
    # 4. tools/call
    # 翼答 schema 的 required 含 7 个元数据参数（question 反而在 properties 内），
    # 即使服务端声明了 default 也必须显式传入，否则业务层报错。
    arguments = {
        "question": question,
        "session_id": session_id,
        "add_info": {},
        "source": source,
        "user_name": os.environ.get("CSC_YIDA_USER_NAME", "b_zhengquan_test20-poc-userName"),
        "version": os.environ.get("CSC_YIDA_VERSION", "2"),
        "user_id": os.environ.get("CSC_YIDA_USER_ID",
                                  "jpC8jxREM8ZlGLI6qw2DCBLKpeccXRTioDIORgTPn"
                                  "/8fzQ80T0D2imb9KHDVfnjA"),
        "logid": os.environ.get("CSC_YIDA_LOGID", "b_zhengquan_zxjt-poc-1789622902218"),
    }
    rc = _post(url, api_key, slug, {
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": tname, "arguments": arguments},
    })
    # 收集 content 文本（翼答把整段 SSE 文本塞在一个 text 里）
    texts = []
    for m in rc:
        if not isinstance(m, dict):
            continue
        if "error" in m:
            return {"error": m["error"]}
        res = m.get("result")
        if res is None:
            continue
        for c in res.get("content", []):
            if c.get("type") == "text" and c.get("text"):
                texts.append(c["text"])
    if not texts:
        return {"raw": str(rc)[:500]}
    if len(texts) == 1:
        return {"raw": texts[0]}
    return {"raw": "\n".join(texts)}


def main():
    ap = argparse.ArgumentParser(description="SkillHub MCP 直连取数 + 紧凑解析（无连接器依赖）")
    ap.add_argument("--base", default=os.environ.get("SKILLHUB_BASE_URL", DEFAULT_BASE))
    ap.add_argument("--server", help="MCP server 名，如 csc-ecomm-ra-llmtools-yida")
    ap.add_argument("--slug", help="本 Skill 的 slug，如 csc-macro-analysis")
    ap.add_argument("--question", help="自然语言问题")
    ap.add_argument("--source", default="b_zhengquan_zxjt")
    ap.add_argument("--session-id", default=None,
                    help="可选；不传则每次自动生成随机新 id（避免后端 session 卡死）。显式传入时优先使用传入值。")
    ap.add_argument("--raw", action="store_true", help="输出原始返回（不解析），仅排查用")
    ap.add_argument("--parse-file", default=None, help="解析已落盘的 SSE 文本文件（不再发起取数）")
    ap.add_argument("--max-rows", type=int, default=50, help="组件 datas 最多输出行数（默认 50，0 = 不限）")
    ap.add_argument("--max-text", type=int, default=0, help="rich_text 最多输出字符数（默认 0 = 不限）")
    a = ap.parse_args()

    # 模式 A：解析已落盘文件
    if a.parse_file:
        try:
            with open(a.parse_file, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception as e:
            sys.stderr.write("ERROR: 无法读取 {}: {}\n".format(a.parse_file, e))
            sys.exit(1)
        print(json.dumps(parse_payload({"raw": text}, a.max_rows, a.max_text),
                         ensure_ascii=False, indent=2))
        return

    # 模式 B：正常取数
    if not (a.server and a.slug and a.question):
        ap.error("取数模式需同时提供 --server / --slug / --question（或用 --parse-file）")
    key = os.environ.get("CSC_SKILLHUB_API_KEY")
    if not key:
        sys.stderr.write("ERROR: 未配置环境变量 CSC_SKILLHUB_API_KEY，无法调用 SkillHub。\n"
                         "请前往 SkillHub 申请并 export CSC_SKILLHUB_API_KEY=<你的Key> 后重试。\n")
        sys.exit(2)
    try:
        result = fetch(a.base, a.server, a.slug, a.question, key, a.source, a.session_id)
    except urllib.error.HTTPError as e:
        sys.stderr.write("HTTPError {}: {}\n".format(e.code, e.read().decode("utf-8", "ignore")[:300]))
        sys.exit(e.code)
    except Exception as e:
        sys.stderr.write("ERROR: {}\n".format(e))
        sys.exit(1)

    if a.raw:
        print(json.dumps(result, ensure_ascii=False))
        return

    parsed = {"server": a.server, "slug": a.slug, "question": a.question}
    parsed.update(parse_payload(result, a.max_rows, a.max_text))
    print(json.dumps(parsed, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
