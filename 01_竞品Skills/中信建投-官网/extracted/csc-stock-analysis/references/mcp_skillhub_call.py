#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SkillHub MCP 直连取数脚本（无 MCP 连接器依赖）。

普通用户只需配置环境变量 CSC_SKILLHUB_API_KEY 即可使用本 Skill，
无需安装/信任任何 MCP 连接器。脚本直接对 SkillHub 的 MCP HTTP 端点
发起标准 JSON-RPC 调用，自动完成 initialize -> tools/call 全流程。

用法：
  python3 mcp_skillhub_call.py --server <server名> --slug <skill的slug> --question "<自然语言问题>"

依赖：仅 Python 标准库（urllib / json / argparse），无需 pip install。
"""
import json
import os
import sys
import time
import random
import string
import urllib.request
import urllib.error
import argparse

# 基础地址；SKILLHUB_BASE_URL 或 data-source-config.md
DEFAULT_BASE = "https://skillhub.csc108.com/api/mcp/v1"


def _new_session_id():
    """每次调用生成唯一 session_id，避免复用固定 id 阻碍网关 30004/Connection closed 恢复。"""
    return "wb-{}-{}{}".format(
        int(time.time() * 1000),
        os.getpid(),
        "".join(random.choices(string.ascii_lowercase + string.digits, k=6)),
    )


# 单次 HTTP 客户端超时（秒）。**由环境层配置，不写死为业务逻辑**。
# 取值理由见 references/data-source-resilience.md §二：网关过载时会挂满约 62s 才回 504，
# 等待超过该时长属白等；默认值取"明显高于实测正常返回耗时上限、明显小于 62s"。
DEFAULT_TIMEOUT = float(os.environ.get("SKILLHUB_HTTP_TIMEOUT", "40"))


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
    # 解析 answer
    for m in rc:
        if not isinstance(m, dict):
            continue
        if "error" in m:
            return {"error": m["error"]}
        res = m.get("result")
        if res is None:
            continue
        for c in res.get("content", []):
            if c.get("type") == "text":
                txt = c["text"]
                # 翼答的 tools/call 返回是 SSE 流：多行 "data:{json}"
                # （逐 token 推送 rich_text / 逐组件推送 result_page）。
                # 必须按行剥前缀后逐行解析，不能当单个 JSON 整体 loads。
                events = []
                for ln in txt.splitlines():
                    ln = ln.strip()
                    if not ln.startswith("data:"):
                        continue
                    try:
                        events.append(json.loads(ln[5:].strip()))
                    except Exception:
                        pass
                if events:
                    return {"events": events}
                return {"text": txt}
    return {"raw": str(rc)[:500]}


def main():
    ap = argparse.ArgumentParser(description="SkillHub MCP 直连取数（无连接器依赖）")
    ap.add_argument("--base", default=os.environ.get("SKILLHUB_BASE_URL", DEFAULT_BASE))
    ap.add_argument("--server", required=True, help="MCP server 名，如 csc-ecomm-ra-llmtools-yida")
    ap.add_argument("--slug", required=True, help="本 Skill 的 slug，如 csc-stock-analysis")
    ap.add_argument("--question", required=True, help="自然语言问题")
    ap.add_argument("--source", default="b_zhengquan_zxjt")
    ap.add_argument("--session-id", default=None,
                    help="可选；不传则每次自动生成新 session_id（wb-{时间戳}-{随机}）")
    a = ap.parse_args()

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
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
